# L16/C01/T04 — Jenkins Plugins Ecosystem (and Risks)

## Learning Objectives

- Manage plugins
- Avoid pitfalls

## Plugins

Jenkins extensibility:
- 1800+ plugins
- Add-on functionality
- Java-based

## Common Plugins

- Git
- Pipeline (built-in)
- Credentials Binding
- Kubernetes
- AWS
- Docker
- Slack
- Configuration as Code (JCasC)
- Blue Ocean (UI)
- Role-Based Authorization Strategy

## Install

UI: Manage Jenkins → Plugins → Available.

Or JCasC config.

## Issues

### Compatibility
Plugin X needs Jenkins core ≥ 2.400.
Plugin Y needs ≤ 2.300.
Conflict.

### CVEs
Plugins have own security history.
Watch security advisories.

### Abandoned
Plugin author stopped maintaining.
Bugs persist.

### Upgrade Pain
Plugin upgrades break pipelines.

## Minimize Plugins

For each plugin:
- Is it needed?
- Active development?
- Org-wide use justified?

Less = less risk.

## Plugin Audit

Quarterly:
- Update all
- Test
- Remove unused

## Security

```
Jenkins Security Advisories
https://www.jenkins.io/security/advisories/
```

Subscribe. Patch CVEs.

## Pinning

Pin versions:
```yaml
# plugins.txt
git:5.0.0
pipeline:600.vbeec61b9c?1
```

Reproducible installs.

## Plugin Management Tool

```bash
jenkins-plugin-cli --plugin-file plugins.txt
```

For: declarative.

## JCasC for Plugin Config

```yaml
jenkins:
  ...
  systemMessage: "Welcome"

unclassified:
  globalLibraries:
    libraries:
      - name: "my-lib"
        defaultVersion: "main"
        retriever:
          modernSCM:
            scm:
              git:
                remote: "https://github.com/org/my-lib.git"
```

## Risky Plugins

Caution with:
- Sandbox bypass plugins
- Untrusted authors
- Complex inter-plugin deps
- Build agents installing arbitrary plugins

## Build Step Plugins

Many: shell, docker, sonarqube, etc.

Prefer: shell + script. Fewer deps.

## Notification Plugins

- Slack
- Email
- Microsoft Teams
- PagerDuty

For: build status.

## Source Plugins

- Git
- GitHub Branch Source (multibranch)
- Bitbucket
- GitLab

## Cloud Plugins

- Kubernetes
- AWS EC2
- Google Cloud

For: dynamic agents.

## Best Practices

- Minimum plugins
- LTS only
- Audit quarterly
- Subscribe to advisories
- Test upgrades in staging Jenkins
- Pin versions
- JCasC for config

## Common Mistakes

- 200+ plugins (sprawl)
- Auto-update (breakage)
- No pinning
- Ignored CVE alerts
- Plugin installs without review

## Alternative

For new orgs: prefer GitHub Actions / GitLab CI / Tekton.

Jenkins overhead often not justified.

## Quick Refs

```bash
# Plugin CLI
jenkins-plugin-cli --plugin-file plugins.txt

# Update center
Manage Jenkins → Updates

# Restart
http://jenkins/restart
```

## Interview Prep

**Mid**: "Jenkins plugins."

**Senior**: "Plugin risk management."

## Next Topic

→ [T05 — Configuration as Code (JCasC)](T05-JCasC.md)
