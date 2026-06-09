# L06/C05/T04 — Configuration: Env, Files, Flags

## Learning Objectives

- Handle config across environments
- Use the 12-factor pattern

## 12-Factor Config

From the 12-Factor App methodology:
> Store config in the environment.

Why:
- Config varies between deploys (dev, staging, prod); code doesn't
- Don't commit secrets
- Env vars are language/OS independent
- Easy to override per process

## Precedence

Three (or four) sources, with precedence:

1. **Default in code** (lowest)
2. **Config file**
3. **Environment variable**
4. **CLI flag** (highest)

User sets at the most convenient level; can override.

```bash
# Default: us-east-1 (in code)
mytool deploy           # uses us-east-1

# config.yaml has region: us-west-2
mytool deploy           # uses us-west-2

# Env var
MYTOOL_REGION=eu-west-1 mytool deploy    # uses eu-west-1

# Flag wins
MYTOOL_REGION=eu-west-1 mytool deploy --region=ap-south-1
# uses ap-south-1
```

## Implementation (Python)

```python
import os
import yaml
from pathlib import Path

class Config:
    def __init__(self):
        # 1. Defaults
        self.region = "us-east-1"
        self.timeout = 30
        
        # 2. Config file
        cfg_path = Path.home() / ".mytool" / "config.yaml"
        if cfg_path.exists():
            data = yaml.safe_load(cfg_path.read_text())
            self.region = data.get("region", self.region)
            self.timeout = data.get("timeout", self.timeout)
        
        # 3. Env
        if "MYTOOL_REGION" in os.environ:
            self.region = os.environ["MYTOOL_REGION"]
        if "MYTOOL_TIMEOUT" in os.environ:
            self.timeout = int(os.environ["MYTOOL_TIMEOUT"])
    
    def apply_flags(self, args):
        # 4. Flags (highest priority)
        if args.region:
            self.region = args.region
```

## With Pydantic

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    region: str = "us-east-1"
    timeout: int = 30
    
    class Config:
        env_prefix = "MYTOOL_"
        env_file = ".env"

settings = Settings()
# Reads env, .env file, fallback to defaults
```

## With Viper (Go)

```go
viper.SetConfigName("config")
viper.SetConfigType("yaml")
viper.AddConfigPath("$HOME/.mytool")
viper.AddConfigPath(".")
viper.SetEnvPrefix("MYTOOL")
viper.AutomaticEnv()                  // MYTOOL_REGION → viper.GetString("region")
viper.SetDefault("region", "us-east-1")

// Bind flag
viper.BindPFlag("region", cmd.Flags().Lookup("region"))

region := viper.GetString("region")
```

## Config File Format

YAML:
```yaml
region: us-west-2
timeout: 60
cluster:
  name: prod
  context: prod
```

TOML:
```toml
region = "us-west-2"
timeout = 60

[cluster]
name = "prod"
context = "prod"
```

JSON: ugly to write; OK to generate.

Pick one; document it. YAML for K8s ecosystem; TOML for Rust/Hashi; INI legacy.

## Config Location

Common conventions:
- `~/.config/mytool/config.yaml` (XDG)
- `~/.mytool/config.yaml`
- `~/.mytool.yaml`
- `./mytool.yaml` (project-local)

Tools often check multiple; first found wins.

## Profiles

Different configs for different envs:
```yaml
default:
  region: us-east-1

profiles:
  staging:
    region: us-west-2
    cluster: staging-cluster
  prod:
    region: eu-west-1
    cluster: prod-cluster
```

```bash
mytool --profile=prod deploy
```

Like AWS CLI's `--profile`.

## Env Var Naming

`MYTOOL_<UPPERCASE_KEY>`:
```
MYTOOL_REGION
MYTOOL_TIMEOUT
MYTOOL_CLUSTER_NAME      # nested via underscore
```

Documented in `--help` / README.

## .env Files

Load from `.env` for local dev:
```
# .env
MYTOOL_REGION=us-west-2
MYTOOL_DEBUG=true
```

```python
from dotenv import load_dotenv
load_dotenv()
```

DON'T commit `.env`; commit `.env.example`:
```
# .env.example
MYTOOL_REGION=
MYTOOL_DEBUG=
```

## Secrets

DON'T put secrets in config files (committed) or flags (in shell history). Instead:
- Env var (set by secret manager)
- Vault / AWS Secrets Manager (read at runtime)
- Workload identity (IAM role / OIDC)

```python
import boto3
secret = boto3.client("secretsmanager").get_secret_value(SecretId="my-secret")
```

## Validation

```python
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    region: str
    timeout: int
    
    @validator("region")
    def valid_region(cls, v):
        if v not in ["us-east-1", "us-west-2", "eu-west-1"]:
            raise ValueError("invalid region")
        return v
    
    @validator("timeout")
    def positive(cls, v):
        if v <= 0:
            raise ValueError("timeout must be > 0")
        return v
```

Fail fast at startup; clear error.

## Hot Reload

For daemons: watch config; reload without restart.
```go
viper.WatchConfig()
viper.OnConfigChange(func(e fsnotify.Event) {
    fmt.Println("config changed:", e.Name)
    reloadHandler()
})
```

Be careful: not all config can be safely reloaded.

## Inspect Config

```bash
mytool config view
mytool config get region
mytool config set region us-west-2
```

Lets users debug "what's my actual config?"

## Multi-Tenant Config

For tools used by multiple users in same machine:
- Per-user: `~/.mytool/`
- Per-project: `./mytool.yaml`
- Global: `/etc/mytool/config.yaml`

Precedence: project > user > global.

## Common Mistakes

- Hardcoded values
- Secrets in flags / files
- Inconsistent precedence
- No validation; silently bad values
- Reading config every call (slow)
- No way to inspect effective config

## CI / Containers

In CI: env vars (set by CI system).
In containers: env vars (Docker `-e`, K8s env).
Mounted config: K8s ConfigMap mounted as file.

Tool should work the same way regardless.

## kubectl Pattern

`kubectl` reads from:
1. `--kubeconfig` flag
2. `KUBECONFIG` env (colon-separated paths)
3. `~/.kube/config`

Then within file, "current-context" selects which cluster.

Excellent model; mimic in your tools.

## Interview Prep

**Mid**: "Config precedence — design."

**Senior**: "Secrets in tool — strategy."

**Staff**: "Hot reload for stateful daemon."

## Next Topic

→ Move to [L07 — Cloud Foundations](../../L07/README.md)
