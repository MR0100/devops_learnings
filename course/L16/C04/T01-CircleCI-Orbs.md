# L16/C04/T01 — CircleCI Orbs & Reusability

## Learning Objectives

- Use CircleCI orbs
- Set up CircleCI

## CircleCI

SaaS CI/CD; fast; macOS support.

## Config

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run: pip install -r requirements.txt
      - run: pytest

workflows:
  ci:
    jobs:
      - test
```

## Orbs

Reusable packages:
```yaml
version: 2.1

orbs:
  aws-cli: circleci/aws-cli@5.0
  python: circleci/python@2.1
  slack: circleci/slack@4.12

jobs:
  build:
    executor: python/default
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
      - run: pytest
      - aws-cli/setup
      - run: aws s3 ls
      - slack/notify:
          event: pass
          channel: ci
```

For: pre-built reusable.

## Public Orbs

- circleci/aws-cli
- circleci/aws-eks
- circleci/aws-s3
- circleci/gcp-cli
- circleci/azure-cli
- circleci/python, node, go, etc.
- circleci/docker
- circleci/kubernetes
- circleci/slack

## Private Orbs

Org-specific:
```bash
circleci orb publish my-orb.yml my-org/my-orb@1.0.0
```

For: internal reuse.

## Orb Anatomy

```yaml
version: 2.1
description: My orb

commands:
  greet:
    parameters:
      name:
        type: string
    steps:
      - run: echo "Hello ${{ parameters.name }}"

jobs:
  test:
    docker:
      - image: cimg/base:stable
    steps:
      - greet:
          name: World

executors:
  default:
    docker:
      - image: cimg/python:3.12
```

## Use Orb

```yaml
orbs:
  my-orb: my-org/my-orb@1.0.0

jobs:
  test:
    executor: my-orb/default
    steps:
      - checkout
      - my-orb/greet:
          name: Alice
```

## Executors

Pre-defined environments:
```yaml
executors:
  python-test:
    docker:
      - image: cimg/python:3.12
        environment:
          DB_URL: postgres://localhost:5432
      - image: postgres:15

jobs:
  test:
    executor: python-test
```

## Workflows

```yaml
workflows:
  ci:
    jobs:
      - build
      - test:
          requires: [build]
      - deploy:
          requires: [test]
          filters:
            branches:
              only: main
```

## Approval

```yaml
workflows:
  ci:
    jobs:
      - build
      - hold-for-approval:
          type: approval
          requires: [build]
      - deploy:
          requires: [hold-for-approval]
```

Manual gate.

## Caching

```yaml
- restore_cache:
    keys:
      - v1-deps-{{ checksum "requirements.txt" }}

- run: pip install -r requirements.txt

- save_cache:
    paths:
      - ~/.cache/pip
    key: v1-deps-{{ checksum "requirements.txt" }}
```

## Resource Class

```yaml
jobs:
  test:
    resource_class: large   # more CPU/RAM
```

Sizes: small, medium, large, xlarge, 2xlarge.

For: bigger jobs.

## macOS

```yaml
jobs:
  ios:
    macos:
      xcode: 15.0.0
    steps: [...]
```

iOS builds; expensive but unique.

## GPU

```yaml
jobs:
  ml:
    machine:
      image: linux-cuda-11
    resource_class: gpu.nvidia.medium
```

## Parameters

```yaml
parameters:
  env:
    type: string
    default: dev

jobs:
  deploy:
    steps:
      - run: deploy.sh --env=<<pipeline.parameters.env>>
```

## Dynamic Config

```yaml
# Config that generates config
setup: true

jobs:
  setup:
    docker: [image: cimg/base:stable]
    steps:
      - checkout
      - run: ./generate.sh > generated.yml
      - continuation/continue:
          configuration_path: generated.yml
```

For: runtime config.

## Pros

- Fast
- macOS / GPU
- Orbs ecosystem
- Polished UI

## Cons

- Paid plans
- Vendor lock-in
- Smaller community vs GitHub Actions

## When CircleCI

- Mac/iOS heavy
- GPU workloads
- Want polished UX

## When Not

- Cost-sensitive
- GitHub-tied (GitHub Actions free)
- Open source

## Best Practices

- Orbs for common patterns
- Executors for env reuse
- Cache aggressively
- Parameterize
- Resource class right-sized

## Common Mistakes

- Build mac on Linux runner (fails)
- No cache
- Over-allocate resource class
- Public orbs untested in your context

## Quick Refs

```yaml
version: 2.1
orbs:
  X: namespace/orb@vN

jobs:
  X:
    docker: [...] | machine: ... | macos: ...
    steps: [...]

workflows:
  X:
    jobs: [...]
```

## Interview Prep

**Mid**: "CircleCI orbs."

**Senior**: "When CircleCI."

## Next Topic

→ Move to [L16/C05 — Tekton](../C05/README.md)
