# L16/C01 — Jenkins

## Topics

- **T01 Architecture (Controller / Agent)** — Controller orchestrates jobs; agents run them. Distributed via SSH, JNLP, or Kubernetes plugin.
- **T02 Declarative vs Scripted Pipelines** — Declarative (default, opinionated `Jenkinsfile`); Scripted (Groovy DSL, more flexible).
- **T03 Shared Libraries** — Reusable Groovy code across pipelines; versioned in Git; `@Library('mylib')`.
- **T04 Plugins Ecosystem (and Risks)** — Thousands of plugins; major source of CVEs; pin and audit aggressively.
- **T05 Configuration as Code (JCasC)** — Configure Jenkins via YAML; reproducible setup; replaces UI clicks.

## Declarative Pipeline Example

```groovy
@Library('shared-pipeline-lib@v1.0') _

pipeline {
  agent { kubernetes { yamlFile 'k8s-agent.yaml' } }
  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '30'))
    disableConcurrentBuilds()
  }
  environment {
    REGISTRY = 'ghcr.io/me'
    APP      = 'myapp'
    SHA      = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
  }
  stages {
    stage('Test') {
      steps {
        sh 'make test'
      }
    }
    stage('Build') {
      steps {
        sh "docker build -t ${REGISTRY}/${APP}:${SHA} ."
      }
    }
    stage('Push') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
          sh "echo $PASS | docker login ghcr.io -u $USER --password-stdin"
          sh "docker push ${REGISTRY}/${APP}:${SHA}"
        }
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        sh "kubectl set image deployment/${APP} ${APP}=${REGISTRY}/${APP}:${SHA}"
      }
    }
  }
  post {
    failure {
      slackSend channel: '#ops', message: "Build failed: ${env.BUILD_URL}"
    }
  }
}
```

## When Jenkins (2025+)

- Existing investment (you have it)
- Hybrid (on-prem + cloud) with complex needs
- Air-gapped environments
- Need extreme customization

## When NOT Jenkins

- Greenfield modern stack — GitHub Actions, GitLab CI, or Tekton more pleasant
- Small team — too much ops overhead
- Plugin sprawl concern

## Risks & Operations

- **Plugin CVEs**: monthly maintenance burden
- **Master scalability**: single Java process, GC tuning
- **Agent connectivity**: long-lived sessions; flaky on cloud
- **State on master**: jobs, builds, config — backup carefully
- **Kubernetes plugin** (recommended for cloud): pods per build, auto-cleanup
- **JCasC** mandatory for reproducible deployments

## Interview Themes

- "Jenkins architecture"
- "Declarative vs Scripted"
- "Why is Jenkins risk-prone at scale?"
- "Kubernetes plugin — how it works"
- "When would you migrate off Jenkins?"
