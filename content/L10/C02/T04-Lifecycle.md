# L10/C02/T04 — Lifecycle Meta-Arguments

## Learning Objectives

- Use lifecycle effectively
- Avoid common pitfalls

## Lifecycle Block

```hcl
resource "aws_instance" "web" {
  ...
  lifecycle {
    create_before_destroy = true
    prevent_destroy       = true
    ignore_changes        = [tags]
    replace_triggered_by  = [aws_security_group.web]
  }
}
```

## create_before_destroy

Default: destroy old, create new (downtime).

`true`: create new first, then destroy old (zero downtime).

For: load balancers, AMIs with replacement (ASG manages but if direct resource).

Requires: unique names (Terraform creates with random suffix or you ensure).

```hcl
resource "aws_launch_template" "web" {
  name_prefix = "web-"   # auto-generates unique name
  
  lifecycle {
    create_before_destroy = true
  }
}
```

## prevent_destroy

Refuse to destroy resource:
```hcl
resource "aws_db_instance" "main" {
  ...
  lifecycle {
    prevent_destroy = true
  }
}
```

Plan/apply error if destroy:
```
Error: Instance cannot be destroyed
```

For: critical DBs, S3 buckets with data.

To actually destroy: remove `prevent_destroy = true`; then apply.

## ignore_changes

Don't track changes on specified attributes:
```hcl
resource "aws_autoscaling_group" "web" {
  desired_capacity = 3
  
  lifecycle {
    ignore_changes = [desired_capacity]
  }
}
```

ASG can change desired_capacity via scaling; Terraform won't revert.

Other use cases:
- AWS-managed tags
- Auto-rotated passwords
- ECS desired count (auto-scaled)

```hcl
ignore_changes = all     # ignore everything (rarely useful)
ignore_changes = [tags, desired_capacity]
```

## replace_triggered_by

Force replace when another resource changes:
```hcl
resource "aws_instance" "web" {
  user_data = data.template_file.userdata.rendered
  
  lifecycle {
    replace_triggered_by = [data.template_file.userdata]
  }
}
```

Useful for: update user data → recreate instance.

## Precondition / Postcondition

Newer (1.2+):
```hcl
resource "aws_instance" "web" {
  ami           = var.ami
  instance_type = "t3.micro"
  
  lifecycle {
    precondition {
      condition     = data.aws_ami.this.architecture == "x86_64"
      error_message = "AMI must be x86_64"
    }
    
    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance must have public IP"
    }
  }
}
```

Validation at plan/apply time. Fail fast.

## Use Cases

### ASG with Launch Template
```hcl
resource "aws_launch_template" "web" {
  name_prefix = "web-"
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "web" {
  launch_template {
    id      = aws_launch_template.web.id
    version = aws_launch_template.web.latest_version
  }
}
```

LT updates → new version; ASG uses new version on new instances.

### Critical Database
```hcl
resource "aws_db_instance" "main" {
  ...
  deletion_protection = true   # AWS-level
  
  lifecycle {
    prevent_destroy = true      # Terraform-level
    ignore_changes = [password]  # rotated externally
  }
}
```

Double protection.

### Auto-Scaled Resource
```hcl
resource "aws_ecs_service" "web" {
  desired_count = 3
  
  lifecycle {
    ignore_changes = [desired_count]
  }
}
```

Auto Scaling adjusts; Terraform doesn't fight.

### IAM Policy from AWS
```hcl
resource "aws_iam_role" "service" {
  managed_policy_arns = [...]
  
  lifecycle {
    ignore_changes = [managed_policy_arns]
  }
}
```

If org policies attach via SCP / org tools.

## Pitfalls

### prevent_destroy Forever
Forgot you set it; deploy fails:
```
Error: cannot destroy
```

Document; review.

### ignore_changes = all
Defeats Terraform. Almost never right.

### create_before_destroy Without Name Prefix
Conflict on create (two with same name).

Use `name_prefix` or unique random suffix.

### Lifecycle Disagreement
Module says `create_before_destroy`; calling code can't override.

## When NOT Lifecycle

- ASG without need (use ASG's own settings)
- Critical resources without prevent_destroy (asking for disaster)
- Ignore everything (defeats purpose)

## Common Patterns

### Blue/Green via Lifecycle
```hcl
resource "aws_launch_template" "web" {
  name_prefix = "web-"
  image_id    = var.ami_id
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "web" {
  name_prefix         = "web-asg-"
  launch_template { ... }
  
  lifecycle {
    create_before_destroy = true
  }
  
  health_check_grace_period = 300
  health_check_type         = "ELB"
  min_elb_capacity          = var.min_capacity   # ensure new healthy before destroy old
}
```

New ASG created; healthy; old destroyed.

### Database with Snapshot
```hcl
resource "aws_db_instance" "main" {
  ...
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.name}-final-snapshot"
  
  lifecycle {
    prevent_destroy = true
  }
}
```

Snapshot on destroy; protected by lifecycle.

## Module Lifecycle

Modules: lifecycle can be inside module; visible to callers (must understand).

Document in module README.

## Plan Output

Lifecycle changes visible:
```
# aws_instance.web must be replaced
-/+ resource "aws_instance" "web" {
      lifecycle {
        create_before_destroy = true   # plan reflects
      }
}
```

`-/+` (forces replacement) vs `~` (update in place).

## Replace via -replace

Force replace specific resource:
```bash
terraform apply -replace=aws_instance.web
```

Modern (1.5+) replacement for `terraform taint`.

## Lifecycle + Drift

`ignore_changes` doesn't ignore drift; just ignores in plan diff.

```hcl
ignore_changes = [tags]
```

Tags change in AWS console → plan shows no diff for tags (ignored). Terraform won't fight.

But: Terraform won't tell you tags drifted either.

## Best Practices

- create_before_destroy for replaceable critical
- prevent_destroy on stateful
- ignore_changes for auto-managed attrs
- Document why each lifecycle is set
- Pre/post conditions for invariants
- Test lifecycle changes carefully

## Examples in Practice

### CloudFront Distribution
```hcl
resource "aws_cloudfront_distribution" "main" {
  ...
  
  lifecycle {
    create_before_destroy = true   # don't go dark during change
  }
}
```

Actually: CF distribution update is in-place; lifecycle doesn't matter here.

### S3 Bucket
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-data"
  
  lifecycle {
    prevent_destroy = true
  }
}
```

Critical data: protected.

### Kubernetes Provider
```hcl
resource "kubernetes_deployment" "app" {
  ...
  
  spec {
    replicas = 3
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].replicas       # HPA manages this
    ]
  }
}
```

HPA scales replicas; Terraform doesn't fight.

## Common Mistakes

- prevent_destroy + apt to delete (process confusion)
- create_before_destroy without name uniqueness
- ignore_changes too broad
- Forgetting lifecycle is a tool, not a wall

## Quick Refs

```hcl
lifecycle {
  create_before_destroy = true
  prevent_destroy       = true
  ignore_changes        = [tags, desired_count]
  replace_triggered_by  = [aws_secret_x]
  
  precondition {...}
  postcondition {...}
}
```

```bash
terraform apply -replace=aws_x.y     # force replace
```

## Interview Prep

**Mid**: "Lifecycle use cases."

**Senior**: "create_before_destroy for ASG."

**Staff**: "Protected resource pattern."

## Next Topic

→ Move to [L10/C03 — Terraform State](../C03/README.md)
