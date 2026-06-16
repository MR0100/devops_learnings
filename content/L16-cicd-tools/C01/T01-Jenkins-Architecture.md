# L16/C01/T01 — Jenkins Architecture (Controller / Agent)

## Learning Objectives

- Understand Jenkins
- Set up controller/agent

## Jenkins

Open-source CI/CD; oldest popular:
- Plugin-based
- Self-hosted
- Java
- Extensive ecosystem

## Architecture

```
Controller (formerly "master")
├─ Web UI
├─ Config
├─ Build queue
├─ Plugins
└─ User mgmt

Agents (formerly "slaves")
└─ Execute jobs
```

## Controller

Single (often). Manages:
- Job definitions
- Scheduling
- Results storage
- Plugin install

## Agents

Per-job execution:
- Linux / Windows / Mac
- Static or ephemeral
- Docker, K8s, VM-based

## Install Controller

```bash
# Docker
docker run -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

Or:
```bash
sudo apt install jenkins
sudo systemctl start jenkins
```

## Initial Setup

- Unlock with admin password
- Install plugins
- Create admin user

## Agent Types

### Static Agents
Persistent VM; configured manually.

### Docker Agents
Spin up per build:
```groovy
agent {
  docker { image 'maven:3.9' }
}
```

### K8s Agents
Pod per build:
```groovy
agent {
  kubernetes {
    yaml '''
      apiVersion: v1
      kind: Pod
      spec:
        containers:
        - name: maven
          image: maven:3.9
    '''
  }
}
```

For: dynamic scale.

### EC2 Plugin
Auto-spin EC2 instances.

## Master Should Not Build

Old default: builds on master.

Best practice: no builds on controller. Security + scale.

```
Build executors on controller: 0
```

For: separation.

## Plugins

```
Jenkins UI → Manage Plugins → Install
```

Or as code (JCasC).

Examples:
- Git
- Pipeline
- Credentials
- Kubernetes
- Cloud-specific

## Plugin Risks

- Compatibility (Jenkins core + plugin versions)
- Security (CVEs)
- Maintenance (some abandoned)
- Upgrade pain

For: minimize plugin sprawl.

## High Availability

Controller HA tricky:
- Active/passive (CloudBees enterprise)
- Backup + restore
- Don't lose JENKINS_HOME

For: backup is critical.

## JENKINS_HOME

```
/var/jenkins_home/
├─ config.xml
├─ jobs/
├─ users/
├─ plugins/
├─ secrets/
└─ workspaces/
```

Backup this dir.

## Backup

```bash
# tar
tar -czf jenkins-backup.tar.gz /var/jenkins_home

# Plugin: ThinBackup
```

## Job Types

### Freestyle (Legacy)
UI-configured. Limited; deprecated.

### Pipeline
Code-driven (Jenkinsfile).

### Multibranch Pipeline
Auto-discovers branches; runs Jenkinsfile.

### Folder
Grouping.

## Distributed Build

```
Controller assigns job → Agent runs → Reports back
```

For scale: many agents.

## Credentials

```
Manage Jenkins → Credentials
```

Types:
- Username/Password
- SSH Key
- Secret Text
- File

Stored encrypted (~).

## RBAC

Role-based Access Control plugin:
- Read
- Build
- Configure
- Admin

Per-folder / per-job.

For: org Jenkins.

## Monitoring

- /metrics (Prometheus plugin)
- /computer (agent status)
- Build duration trends

Tools: Grafana, ELK.

## Webhooks

```
GitHub → Jenkins webhook → trigger build
```

```
http://jenkins.example.com/github-webhook/
```

For: push-driven CI.

## Build Triggers

- Webhook
- SCM polling (slow; avoid)
- Cron schedule
- Manual
- Upstream job

## Pipeline Code

In Jenkinsfile:
```groovy
pipeline {
  agent any
  stages {
    stage('Build') {
      steps { sh 'mvn clean install' }
    }
    stage('Test') {
      steps { sh 'mvn test' }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps { sh 'deploy.sh' }
    }
  }
}
```

## Issues

- Heavy (Java; lots of plugins)
- UI dated
- Cloud-native poorly
- Maintenance burden
- Declining mindshare

## Why Still Used

- Legacy installations
- Complex enterprise pipelines
- Plugin ecosystem (vast)
- On-prem reliable
- Customizable

## Modern Alternatives

- GitHub Actions / GitLab CI (cloud-native)
- Tekton (K8s-native)
- ArgoCD + workflow (CD-focused)

For new: rarely Jenkins.
For existing: maintain or migrate gradually.

## Migration Out

Tools:
- Jenkins → GitHub Actions: manual or community tools
- Jenkins → Tekton: K8s-friendly

Start with simple jobs; migrate complex last.

## CloudBees

Commercial Jenkins:
- CloudBees CI (Jenkins + extras)
- HA, support
- Enterprise features

For: enterprises stuck on Jenkins.

## Best Practices

- Pipeline as code (Jenkinsfile)
- No builds on controller
- K8s agents (dynamic)
- JCasC for config
- Backup JENKINS_HOME
- Plugin auditing
- LTS only

## Common Mistakes

- Freestyle jobs (no version control)
- UI config (no traceability)
- Plugin sprawl
- Controller as builder (load + risk)
- No backup
- Old LTS (CVEs)

## Quick Refs

```bash
# Status
systemctl status jenkins

# CLI
jenkins-cli help

# Backup
tar -czf backup.tar.gz /var/jenkins_home
```

## Interview Prep

**Junior**: "Jenkins basics."

**Mid**: "Controller/agent."

**Senior**: "Jenkins at scale."

**Staff**: "Migration off Jenkins."

## Next Topic

→ [T02 — Declarative vs Scripted Pipelines](T02-Declarative-Scripted.md)
