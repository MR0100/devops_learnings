# L13/C16/T03 — DNS, Service, Ingress Issues

## Learning Objectives

- Debug network layers
- Test each in isolation

## Network Layers

```
External user → Ingress → Service → Endpoints → Pods
                  ↓
              kube-proxy iptables/IPVS
                  ↓
              CoreDNS
```

Each layer can break. Test from outside in OR inside out.

## DNS Issues

### Pod Can't Resolve
```bash
kubectl exec my-pod -- nslookup kubernetes.default
# error: lookup failed
```

### Causes

1. **CoreDNS Down**
```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system <coredns-pod>
```

2. **Wrong DNS Config in Pod**
```bash
kubectl exec my-pod -- cat /etc/resolv.conf
# Should show: nameserver 10.96.0.10 (Service IP)
```

If not: pod's dnsPolicy issue.

3. **NetworkPolicy Blocks**
Pod can't reach CoreDNS:
```yaml
# allow egress to DNS
egress:
- to:
  - namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: kube-system}}
    podSelector: {matchLabels: {k8s-app: kube-dns}}
  ports:
  - port: 53
    protocol: UDP
```

4. **CoreDNS Misconfig**
```bash
kubectl get cm coredns -n kube-system -o yaml
# Check Corefile
```

## Test DNS

```bash
# Cluster service
kubectl exec my-pod -- nslookup kubernetes.default

# External
kubectl exec my-pod -- nslookup google.com

# Specific service
kubectl exec my-pod -- nslookup my-service.namespace.svc.cluster.local

# Via dig (more detail)
kubectl exec my-pod -- dig my-service.default.svc.cluster.local
```

If kubernetes.default fails: in-cluster DNS broken.
If external fails: forwarder issue.

## CoreDNS Logs

```bash
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50
```

Errors? High CPU?

## Service Issues

### No Endpoints
```bash
kubectl get endpoints my-svc
# my-svc   <none>   1m
```

Empty → no backend pods.

### Causes

1. **Selector Mismatch**
```bash
kubectl get svc my-svc -o jsonpath='{.spec.selector}'
# {app: web}

kubectl get pods -l app=web
# (empty)
```

Pod labels don't match.

Fix: align labels OR fix selector.

2. **Pods Not Ready**
Service only includes Ready pods:
```bash
kubectl get pods -l app=web
# my-app-1   0/1   Running   1m
```

`0/1` = not Ready. Check readiness probe.

3. **Wrong Port**
```yaml
# Service
spec:
  ports:
  - port: 80
    targetPort: 8080   # must match pod's containerPort

# Pod
containers:
- ports:
  - containerPort: 8080
```

Mismatch → connection refused.

## Test Service

From pod:
```bash
# DNS resolution
kubectl exec my-pod -- nslookup my-svc

# Connect
kubectl exec my-pod -- curl http://my-svc/
kubectl exec my-pod -- nc -zv my-svc 80
```

Or via port-forward:
```bash
kubectl port-forward svc/my-svc 8080:80
curl http://localhost:8080/
```

## kube-proxy

If Service has endpoints but traffic doesn't route:
```bash
kubectl get pods -n kube-system -l k8s-app=kube-proxy
kubectl logs -n kube-system <kube-proxy-pod>

# iptables rules
kubectl exec -n kube-system <kube-proxy-pod> -- iptables -t nat -L | head
```

For Cilium replacement: check Cilium logs.

## NetworkPolicy

Block traffic unexpectedly:
```bash
# Cilium Hubble
hubble observe --pod my-pod --verdict DENIED

# Calico
calicoctl get networkpolicy
```

If pod-to-service blocked: NetworkPolicy missing allow.

## Ingress Issues

### Returns 404
- Path mismatch
- Host header wrong
- Backend Service not found

```bash
kubectl describe ingress my-ing
# Rules:
#   Host         Path  Backend
#   app.com      /     my-svc:80
```

Verify:
- DNS for app.com → ingress controller LB
- Path `/` matches
- Service `my-svc` exists + has endpoints

### Returns 502 Bad Gateway
Backend can't be reached:
- Pod not ready (Service endpoint missing)
- targetPort wrong
- App returns error

### Returns 503 Service Unavailable
No backends or all unhealthy.

## Test Ingress

```bash
# DNS resolves
dig app.example.com

# Returns LB IP

# Curl
curl -v https://app.example.com/

# With custom Host header
curl -H "Host: app.example.com" http://INGRESS_IP/

# Verify Ingress
kubectl describe ingress my-ing
kubectl get ingress -A
```

## Ingress Controller Logs

```bash
kubectl logs -n ingress-nginx ingress-nginx-controller-xxx
```

Errors? 404 / 502 patterns?

## Path Types

```yaml
- path: /
  pathType: Prefix    # / matches /, /a, /a/b

- path: /api
  pathType: Exact     # only /api
```

Mismatch → 404.

## TLS Issues

```bash
# Inspect cert
kubectl get secret my-tls -o yaml
echo "<base64-cert>" | base64 -d | openssl x509 -text -noout

# Verify domain
openssl s_client -servername app.example.com -connect app.example.com:443
```

## ALB / NLB (AWS)

```bash
# ALB target group health
aws elbv2 describe-target-health --target-group-arn ...

# SG allows ingress?
aws ec2 describe-security-groups
```

## DNS Outside Cluster

External user → app.example.com:
```bash
dig app.example.com
# Should return Ingress LB hostname / IP
```

If wrong:
- DNS record missing
- TTL stale
- External DNS controller not syncing

## ExternalDNS

```bash
kubectl logs -n external-dns external-dns-xxx
```

For: auto-create Route53 records from Ingress.

## Diagnosis Workflow

External user → app fails:

1. DNS
```bash
dig app.example.com
```

2. LB reachable
```bash
curl -v https://app.example.com
```

3. Ingress receives
```bash
kubectl logs -n ingress-nginx
```

4. Service has endpoints
```bash
kubectl get endpoints my-svc
```

5. Pod ready
```bash
kubectl get pod
```

6. Pod responds
```bash
kubectl exec my-pod -- curl localhost:8080/
```

7. Network policies
```bash
hubble observe --pod my-pod --verdict DENIED
```

Find broken link.

## Common Issues

### Service Latency
- Check kube-proxy mode (iptables slow at scale)
- Check Service endpoints distribution
- Check CNI overhead

### Service Returns Wrong Pod
- Selector matches too many pods
- Stale endpoints

### Connection Refused
- Pod not running
- Port mismatch
- App not listening

### Connection Timeout
- NetworkPolicy
- SG
- Firewall
- Network partition

## Tools

### nicolaka/netshoot
```bash
kubectl run debug --rm -it --image=nicolaka/netshoot -- bash

# Inside:
nslookup my-svc
curl my-svc:80
dig +trace my-svc.default.svc.cluster.local
```

### Cilium Hubble
```bash
hubble observe --pod my-pod
hubble observe --to-pod my-target --verdict DENIED
```

### Calico
```bash
calicoctl get networkpolicy
calicoctl ipam show
```

## Best Practices

- Test each layer independently
- Use netshoot in debug containers
- Verify endpoints before app
- Monitor DNS / Service / Ingress
- NetworkPolicies tested
- Documentation per app

## Common Mistakes

- Assuming DNS works (test)
- Wrong selector
- Probe failure = no endpoints
- Path mismatch in Ingress
- TLS cert expired

## Quick Refs

```bash
# DNS
kubectl exec POD -- nslookup SVC

# Endpoints
kubectl get endpoints SVC

# Curl from pod
kubectl exec POD -- curl SVC:PORT

# Ingress
kubectl describe ingress NAME
kubectl logs -n ingress-nginx CONTROLLER

# Test from netshoot
kubectl run debug --rm -it --image=nicolaka/netshoot -- bash
```

## Interview Prep

**Mid**: "Service not working — diagnose."

**Senior**: "DNS failure investigation."

**Staff**: "Network troubleshooting playbook."

## Next Topic

→ [T04 — etcd Recovery](T04-etcd-Recovery.md)
