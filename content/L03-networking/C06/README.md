# L03/C06 — Network Troubleshooting

## Chapter Overview

You will spend hours of your career debugging networks. This chapter is the toolkit.

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Ping-Traceroute.md) | ping, traceroute, mtr | 0.5 hr |
| [T02](T02-Tcpdump-Wireshark.md) | tcpdump & Wireshark | 1.5 hr |
| [T03](T03-Netstat-SS.md) | netstat, ss, lsof | 1 hr |
| [T04](T04-Curl-HTTP-Debug.md) | curl and HTTP Debugging | 1 hr |
| [T05](T05-Packet-Captures.md) | Reading Real Packet Captures | 1.5 hr |

## The Diagnosis Decision Tree

```
"Service unreachable"
│
├── Can I resolve DNS? → dig host
│      └─ if no: DNS issue (resolver, NS, records)
├── Can I reach the IP? → ping <ip>
│      └─ if no: routing, firewall, host down
├── Is the port open? → nc -vz <ip> <port>
│      └─ if no: app not running, security group, iptables
├── Does TCP handshake succeed? → tcpdump
│      └─ if RST: app rejecting; if no SYN-ACK: firewall
├── Does TLS handshake succeed? → openssl s_client
│      └─ if no: cert, cipher, protocol mismatch
├── Does HTTP respond? → curl -v
│      └─ if 5xx: app issue; if 4xx: client/auth issue
```

## Layer 3 Tools

### ping
- ICMP Echo Request/Reply
- Shows RTT, loss
- Many networks drop ICMP — absence of ping doesn't prove unreachability

```bash
ping -c 4 example.com
ping -i 0.2 example.com   # 5/sec
ping -M do -s 1472 example.com   # MTU discovery
```

### traceroute / mtr
Sends packets with increasing TTL; intermediate routers reply with ICMP Time Exceeded.

```bash
traceroute example.com
traceroute -T -p 443 example.com   # TCP variant (better for firewalled paths)
mtr example.com                    # combined continuous traceroute + ping
mtr -rwn -c 100 example.com        # report mode
```

## Layer 4 Tools

### tcpdump
The packet-level diagnostic. Master this.

```bash
# Capture on interface
tcpdump -i eth0

# Filter (BPF expressions)
tcpdump -i any 'host 1.2.3.4'
tcpdump -i any 'port 443'
tcpdump -i any 'tcp port 443 and host 1.2.3.4'
tcpdump -i any 'src 1.2.3.4 or dst 1.2.3.4'
tcpdump -i any 'tcp[tcpflags] & (tcp-syn|tcp-fin) != 0'  # SYN or FIN
tcpdump -i any 'tcp[tcpflags] & tcp-rst != 0'            # RESETs

# Verbose / hex / write to file
tcpdump -nn -vvv -X -i any port 53      # DNS in detail
tcpdump -w capture.pcap -i any port 443  # save for Wireshark
tcpdump -r capture.pcap                  # read

# Decode HTTP (cleartext)
tcpdump -s 0 -A -i any 'tcp port 80'
```

### Wireshark
GUI inspection of pcaps. Filters:

```
ip.addr == 1.2.3.4
tcp.port == 443
tls.handshake.type == 1     # ClientHello
http.request.method == "POST"
tcp.flags.reset == 1
```

### Reading a TCP problem in tcpdump

```
12:00:00.001  10.0.0.1.54321 > 10.0.0.2.443: Flags [S], seq 100
12:00:00.002  10.0.0.2.443 > 10.0.0.1.54321: Flags [S.], seq 200, ack 101
12:00:00.003  10.0.0.1.54321 > 10.0.0.2.443: Flags [.], ack 201
12:00:00.010  10.0.0.1.54321 > 10.0.0.2.443: Flags [P.], seq 101:300, ack 201
12:00:01.500  10.0.0.1.54321 > 10.0.0.2.443: Flags [P.], seq 101:300, ack 201  (retransmit!)
12:00:03.000  10.0.0.1.54321 > 10.0.0.2.443: Flags [R.], seq 300, ack 201      (give up)
```

→ Server got SYN but stopped responding. Investigate server side.

## Socket Inspection

### ss (modern, fast)
```bash
ss -tn state established       # established TCP
ss -tlnp                       # listening TCP, processes
ss -tn '( dport = :443 )'      # to port 443
ss -tn '( dst 1.2.3.4 )'       # to specific dest
ss -s                          # summary

# State counts (helpful)
ss -tan | awk '{print $1}' | sort | uniq -c
```

### lsof
```bash
lsof -i :443                   # what's using port 443
lsof -i tcp -p <pid>           # connections of process
lsof -i @1.2.3.4               # connections to host
```

### netstat (legacy, slower; use ss when possible)
```bash
netstat -tulpn
netstat -an | grep TIME_WAIT | wc -l
```

## Layer 7 Tools

### curl

```bash
# Verbose with timing
curl -v https://api.example.com/users

# Timing breakdown
curl -w "@curl-format.txt" -o /dev/null -s https://example.com

# curl-format.txt content:
#     time_namelookup:  %{time_namelookup}\n
#        time_connect:  %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#    time_pretransfer:  %{time_pretransfer}\n
#       time_redirect:  %{time_redirect}\n
#  time_starttransfer:  %{time_starttransfer}\n
#                      ----------\n
#          time_total:  %{time_total}\n

# Force HTTP version
curl --http1.1 https://example.com
curl --http2 https://example.com
curl --http3 https://example.com

# Bypass DNS for testing
curl --resolve example.com:443:1.2.3.4 https://example.com/

# Headers
curl -I https://example.com    # HEAD
curl -H 'X-Debug: 1' https://example.com

# Body & method
curl -X POST -H 'Content-Type: application/json' -d '{"x":1}' https://example.com/api
```

### Other
- `httpie` — friendlier curl
- `grpcurl` — for gRPC
- `nc` (netcat) — raw TCP/UDP testing

## Common Debug Workflows

### "Connection refused"
- App not listening on that port
- Wrong port
- Bound to loopback only (`127.0.0.1` not `0.0.0.0`)

### "Connection timed out"
- Firewall dropping packets (silent)
- Wrong IP, no route
- Server overloaded (SYN_RECV stuck)

### "Connection reset"
- App actively closed (`RST` packet)
- Stateful firewall removed flow state
- Conntrack table full

### Random slowness
- Packet loss → retransmissions
- MTU mismatch → fragmentation
- Congestion → backpressure

## Interview Themes

- "Walk me through diagnosing a slow API call"
- "tcpdump filter for SYN packets to port 443"
- "Compare ss and netstat"
- "Customer reports intermittent timeouts. Walk through investigation."
- "What's a TCP RST and when do you see it?"

## Hands-On Lab

1. Open Wireshark/tcpdump
2. `curl -v https://example.com`
3. Identify: DNS query, TCP handshake, TLS handshake, HTTP request, HTTP response, connection close
4. Repeat with `--http3` (if supported); compare
