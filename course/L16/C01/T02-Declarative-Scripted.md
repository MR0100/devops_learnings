# L16/C01/T02 — Declarative vs Scripted Pipelines

## Learning Objectives

- Choose pipeline style
- Write modern Jenkinsfile

## Declarative

Structured DSL:
```groovy
pipeline {
  agent any
  environment {
    VERSION = '1.0.0'
  }
  stages {
    stage('Build') {
      steps { sh 'make build' }
    }
    stage('Test') {
      steps { sh 'make test' }
    }
  }
  post {
    always { archiveArtifacts 'out/**' }
    failure { mail to: 'team@example.com', subject: 'Failed' }
  }
}
```

For: most cases. Easier to read.

## Scripted

Groovy-based:
```groovy
node {
  stage('Build') {
    sh 'make build'
  }
  stage('Test') {
    sh 'make test'
  }
}
```

For: complex flow, dynamic.

## Comparison

| | Declarative | Scripted |
|---|---|---|
| Syntax | Structured | Free Groovy |
| Learn | Easier | Harder |
| Dynamic | Limited | Full |
| Recommended | Yes (default) | Edge cases |
| Validation | Pre-checked | Runtime |

## Declarative Sections

- agent
- environment
- options
- parameters
- triggers
- stages
- post

Strict order.

## Parameters

```groovy
parameters {
  string(name: 'BRANCH', defaultValue: 'main')
  booleanParam(name: 'DEPLOY', defaultValue: false)
  choice(name: 'ENV', choices: ['dev', 'staging', 'prod'])
}
```

## When (Conditional)

```groovy
stage('Deploy') {
  when {
    branch 'main'
    expression { params.DEPLOY }
  }
  steps { sh 'deploy.sh' }
}
```

## Parallel

```groovy
stage('Tests') {
  parallel {
    stage('Unit') { steps { sh 'make test-unit' } }
    stage('Integration') { steps { sh 'make test-int' } }
  }
}
```

## Matrix

```groovy
stage('Matrix') {
  matrix {
    axes {
      axis {
        name 'OS'
        values 'linux', 'mac', 'windows'
      }
    }
    stages {
      stage('Test') { steps { sh 'test on ${OS}' } }
    }
  }
}
```

## Agent Per Stage

```groovy
stages {
  stage('Build') {
    agent { docker 'maven:3.9' }
    steps { sh 'mvn build' }
  }
  stage('Deploy') {
    agent { docker 'alpine' }
    steps { sh 'deploy.sh' }
  }
}
```

## Post

```groovy
post {
  always { ... }
  success { ... }
  failure { slackSend channel: '#alerts', message: 'Build failed' }
  unstable { ... }
  changed { ... }
}
```

## Scripted Use Cases

Dynamic stages:
```groovy
def services = ['api', 'web', 'worker']
node {
  services.each { svc ->
    stage("Build ${svc}") {
      sh "make build-${svc}"
    }
  }
}
```

For: loops.

## Hybrid

```groovy
pipeline {
  agent any
  stages {
    stage('Dynamic') {
      steps {
        script {
          // Scripted Groovy here
          def envs = ['dev', 'staging']
          envs.each { e ->
            sh "deploy ${e}"
          }
        }
      }
    }
  }
}
```

`script { }` block for Groovy inside declarative.

## Linting

```bash
# Check Jenkinsfile
curl -X POST -F "jenkinsfile=<Jenkinsfile" https://jenkins.example.com/pipeline-model-converter/validate
```

For: pre-commit.

## Replay

Jenkins UI: replay job with modified Jenkinsfile. For: iterative.

## Best Practices

- Declarative default
- Scripted only for dynamic
- Use post for cleanup/notify
- Parallel for speed
- Agent per stage
- Parameters for flexibility

## Common Mistakes

- All scripted (hard to read)
- No post (no cleanup)
- Sequential when parallel possible
- Hardcoded values

## Quick Refs

```groovy
pipeline {
  agent any
  stages {
    stage('X') {
      steps { ... }
    }
  }
  post { ... }
}
```

## Interview Prep

**Mid**: "Declarative vs scripted."

**Senior**: "When each."

## Next Topic

→ [T03 — Shared Libraries](T03-Shared-Libraries.md)
