# L16/C01/T03 — Jenkins Shared Libraries

## Learning Objectives

- Share Groovy code across pipelines
- DRY across teams

## Shared Library

Reusable Groovy code in Git repo:
```
my-shared-lib/
  vars/
    standardPipeline.groovy
    deployService.groovy
  src/
    com/example/Utils.groovy
  resources/
    templates/
```

## Configure

```
Jenkins → Manage Jenkins → System → Global Pipeline Libraries
- Name: my-shared-lib
- Source: Git
- Default version: main
```

## Use

```groovy
@Library('my-shared-lib') _

standardPipeline {
  service = 'myapp'
  env = 'prod'
}
```

## Define

```groovy
// vars/standardPipeline.groovy
def call(Map config) {
  pipeline {
    agent any
    stages {
      stage('Build') {
        steps { sh "build ${config.service}" }
      }
      stage('Deploy') {
        when { branch 'main' }
        steps { sh "deploy ${config.service} to ${config.env}" }
      }
    }
  }
}
```

## src/ Classes

```groovy
// src/com/example/Utils.groovy
package com.example

class Utils {
  static String greet(String name) {
    return "Hello, ${name}!"
  }
}
```

Use:
```groovy
@Library('my-shared-lib') _
import com.example.Utils

echo Utils.greet('World')
```

## Versioning

```groovy
@Library('my-shared-lib@v1.0.0') _
```

Pin to tag. For: stability.

## Multiple Libraries

```groovy
@Library(['lib-a@v1', 'lib-b@v2']) _
```

## Auto-Load

Configure as default; no `@Library` needed.

## Steps

```groovy
// vars/deployService.groovy
def call(String env, String version) {
  echo "Deploying to ${env} version ${version}"
  sh "kubectl set image deploy/myapp myapp=image:${version} -n ${env}"
}
```

Use:
```groovy
deployService 'prod', '1.0.0'
```

## Resources

```groovy
def template = libraryResource 'templates/k8s.yaml'
writeFile file: 'deploy.yaml', text: template
```

For: shared templates.

## Best Practices

- Library per concern (deploy, test, build)
- Semantic versioning
- Tests for shared library
- Document each step
- Pin versions in pipelines

## Common Mistakes

- Untested shared library
- No version pinning (drift)
- All in one library (monolith)
- No docs

## Quick Refs

```groovy
@Library('lib@v1') _

// vars/X.groovy: def call() { ... }
// src/com/X.groovy: classes
// resources/X: templates
```

## Interview Prep

**Mid**: "Shared library."

**Senior**: "Sharing patterns."

## Next Topic

→ [T04 — Plugins Ecosystem (and Risks)](T04-Plugins.md)
