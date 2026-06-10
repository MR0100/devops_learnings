# L16/C01/T05 — Configuration as Code (JCasC)

## Learning Objectives

- Configure Jenkins via YAML
- Reproducible setup

## JCasC

Jenkins Configuration as Code:
- jenkins.yaml file
- Auto-applied on startup
- No UI clicks
- Versioned

## Install

Plugin: configuration-as-code.

## Sample

```yaml
jenkins:
  systemMessage: "Welcome to Jenkins"
  numExecutors: 0   # no builds on controller
  scmCheckoutRetryCount: 3

  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: admin
          password: "${ADMIN_PASSWORD}"

  authorizationStrategy:
    globalMatrix:
      permissions:
        - "Overall/Administer:admin"
        - "Overall/Read:authenticated"

  clouds:
    - kubernetes:
        name: k8s
        serverUrl: https://k8s.example.com
        namespace: jenkins
        jenkinsUrl: http://jenkins.jenkins.svc.cluster.local:8080

unclassified:
  location:
    url: https://jenkins.example.com/
  gitHubPluginConfig:
    configs:
      - name: GitHub
        apiUrl: https://api.github.com
        credentialsId: github-token

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: github-token
              username: jenkins-bot
              password: "${GITHUB_TOKEN}"
```

## Apply

Place in `$JENKINS_HOME/jenkins.yaml`.

Or env:
```bash
CASC_JENKINS_CONFIG=/var/jenkins_conf/jenkins.yaml
```

Jenkins reads at startup.

## Reload

```
Manage Jenkins → Configuration as Code → Reload
```

Or restart.

## Env Vars

Reference secrets:
```yaml
password: "${ADMIN_PASSWORD}"
```

Set via:
- Docker env
- K8s Secret mount
- Vault

## Sections

- jenkins (core)
- credentials
- jobs (via plugin)
- tools
- unclassified (catch-all)

## Job DSL

Define jobs in YAML/Groovy:
```yaml
jobs:
  - script: >
      job('my-job') {
        scm { git('https://github.com/me/repo.git') }
        steps { shell('make test') }
      }
```

For: codified job creation.

## Multibranch Pipelines

Auto-discover branches. Configured once.

```yaml
jobs:
  - script: >
      multibranchPipelineJob('my-project') {
        branchSources {
          github {
            repoOwner('me')
            repository('repo')
          }
        }
      }
```

## Plugin Config

Most plugins JCasC-compatible:
```yaml
unclassified:
  globalLibraries:
    libraries:
      - name: my-lib
        defaultVersion: main
        retriever:
          modernSCM:
            scm:
              git:
                remote: https://github.com/org/my-lib.git
```

## Bootstrap Pattern

```dockerfile
FROM jenkins/jenkins:lts

# Install plugins
COPY plugins.txt /usr/share/jenkins/ref/
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# JCasC config
COPY jenkins.yaml /var/jenkins_home/
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/jenkins.yaml

# Skip setup wizard
ENV JAVA_OPTS=-Djenkins.install.runSetupWizard=false
```

For: turnkey Jenkins.

## K8s

```yaml
apiVersion: apps/v1
kind: StatefulSet
spec:
  template:
    spec:
      containers:
      - name: jenkins
        image: jenkins/jenkins:lts
        env:
        - name: CASC_JENKINS_CONFIG
          value: /var/jenkins_conf/jenkins.yaml
        volumeMounts:
        - name: config
          mountPath: /var/jenkins_conf
      volumes:
      - name: config
        configMap:
          name: jenkins-casc
```

ConfigMap holds jenkins.yaml.

## Helm

```bash
helm install jenkins jenkinsci/jenkins \
  --set controller.JCasC.configScripts.welcome-message=... \
  --set controller.JCasC.defaultConfig=true
```

Helm chart supports JCasC.

## Git Workflow

```
1. Update jenkins.yaml
2. Commit
3. PR review
4. Merge → Argo CD syncs ConfigMap
5. Jenkins reloads (manual or operator)
```

GitOps for Jenkins.

## Pros

- Reproducible
- Versioned
- Reviewable
- Disaster recovery (re-deploy)

## Cons

- Learning curve
- Some plugins don't support
- Schema drift across versions
- Reload != restart sometimes

## Best Practices

- jenkins.yaml in Git
- Secrets via env
- Plugin pinning + JCasC
- Reload testing in staging
- Document each section
- Backup persistent jobs

## Common Mistakes

- Manual UI changes (drift from JCasC)
- Secrets in YAML (plaintext)
- No backup of jobs (JCasC doesn't cover job content)
- Old JCasC schema (upgrade pain)

## Migration

Existing Jenkins:
1. Export current config (JCasC plugin can export)
2. Adjust YAML
3. Test in staging Jenkins
4. Apply

For: gradual.

## Drift Detection

Compare:
```bash
diff jenkins.yaml exported-from-running.yaml
```

Find UI changes. Reconcile or commit.

## Quick Refs

```yaml
# Sections
jenkins:
credentials:
jobs:
tools:
unclassified:
```

```bash
# Reload
curl -X POST /casc/reload
```

## Interview Prep

**Mid**: "JCasC."

**Senior**: "Jenkins reproducibility."

**Staff**: "GitOps for Jenkins."

## Next Topic

→ Move to [L16/C02 — GitHub Actions](../C02/README.md)
