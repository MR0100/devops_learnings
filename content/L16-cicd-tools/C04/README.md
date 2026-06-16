# L16/C04 — CircleCI

## Topics

- **T01 Orbs & Reusability** — Orbs = packaged reusable config (commands, jobs, executors).

## .circleci/config.yml

```yaml
version: 2.1

orbs:
  aws-ecr: circleci/aws-ecr@9.0
  docker: circleci/docker@2.5

executors:
  go:
    docker: [{image: cimg/go:1.22}]

jobs:
  test:
    executor: go
    steps:
      - checkout
      - restore_cache: { keys: ["go-mod-{{ checksum \"go.sum\" }}"] }
      - run: go test ./...
      - save_cache:
          key: go-mod-{{ checksum "go.sum" }}
          paths: [/home/circleci/go/pkg/mod]

  build:
    executor: go
    steps:
      - checkout
      - setup_remote_docker
      - docker/build:
          image: myorg/myapp
          tag: ${CIRCLE_SHA1}
      - aws-ecr/push-image:
          repo: myorg/myapp
          tag: ${CIRCLE_SHA1}

workflows:
  ci:
    jobs:
      - test
      - build:
          requires: [test]
          filters: { branches: { only: main } }
```

## When CircleCI

- macOS builds (one of the cheapest options for Macs)
- GPU runners
- Smaller team without GitHub Actions
- Orbs marketplace

## When NOT CircleCI

- Already on GitHub Actions or GitLab CI — no compelling reason to move
- Free tier limited

## Interview Themes
- "Orbs — what are they?"
- "CircleCI vs GitHub Actions"
- "Mac builds — CircleCI strengths"
