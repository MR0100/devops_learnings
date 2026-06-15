# L06/C02/T06 — Writing CLIs with Click / Typer

## Learning Objectives

- Build CLI tools in Python
- Choose between Click and Typer

## Click

Composable CLI framework. Mature, widely used.

```python
import click

@click.command()
@click.argument("file")
@click.option("--verbose", "-v", is_flag=True)
@click.option("--count", default=10, type=int)
def main(file, verbose, count):
    """Process FILE."""
    if verbose:
        click.echo(f"Processing {file}...")

if __name__ == "__main__":
    main()
```

```bash
python cli.py myfile.txt --verbose --count 20
```

### Groups (Subcommands)
```python
@click.group()
def cli():
    """My tool."""
    pass

@cli.command()
def start():
    """Start the service."""
    click.echo("starting")

@cli.command()
@click.argument("name")
def stop(name):
    """Stop NAME."""
    click.echo(f"stopping {name}")

if __name__ == "__main__":
    cli()
```

```bash
python cli.py start
python cli.py stop myservice
```

## Typer

Built on Click; uses type hints. Newer; modern. Recommended.

```python
import typer
app = typer.Typer()

@app.command()
def deploy(
    service: str,
    version: str,
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Deploy SERVICE at VERSION."""
    typer.echo(f"Deploying {service} v{version}")

@app.command()
def rollback(service: str):
    """Rollback SERVICE."""
    typer.echo(f"Rolling back {service}")

if __name__ == "__main__":
    app()
```

```bash
python cli.py deploy myapp v1.2.3 --dry-run
python cli.py rollback myapp
```

Cleaner than Click; same engine under hood.

## Why Typer

- Type hints auto-derive validation
- Less boilerplate
- Easier to read
- IDE autocompletion works

## Help Generation

Both auto-generate `--help`:
```bash
python cli.py --help
python cli.py deploy --help
```

Docstrings + arg types become help text.

## Prompts

```python
# Typer
@app.command()
def setup(
    name: str = typer.Option(..., prompt="Name?"),
    confirm: bool = typer.Confirm("Sure?"),
):
    ...

# Click
@click.command()
@click.option("--name", prompt="Name?")
@click.confirmation_option(prompt="Sure?")
def setup(name):
    ...
```

## Progress Bars

```python
# Typer
with typer.progressbar(items) as progress:
    for item in progress:
        process(item)

# Or
from rich.progress import Progress
with Progress() as p:
    task = p.add_task("Processing", total=len(items))
    for item in items:
        process(item)
        p.update(task, advance=1)
```

## Colors / Formatting

```python
# Typer (uses Rich under hood)
typer.echo(typer.style("OK", fg=typer.colors.GREEN))
typer.echo(typer.style("ERROR", fg=typer.colors.RED, bold=True))
```

## Context

Pass shared state:
```python
@app.callback()
def main(ctx: typer.Context, env: str = "dev"):
    ctx.obj = {"env": env}

@app.command()
def deploy(ctx: typer.Context):
    env = ctx.obj["env"]
    typer.echo(f"deploying to {env}")
```

## Exit Codes

```python
raise typer.Exit(code=1)
```

For success: just return.

## Examples

### kubectl-style Tool
```python
import typer
app = typer.Typer()

config = typer.Typer()
get = typer.Typer()
app.add_typer(config, name="config")
app.add_typer(get, name="get")

@config.command("view")
def config_view():
    typer.echo("config")

@get.command("pods")
def get_pods(namespace: str = typer.Option("default", "-n")):
    typer.echo(f"pods in {namespace}")

if __name__ == "__main__":
    app()
```

```bash
mytool config view
mytool get pods -n myns
```

## Distribution

Build executable:
```bash
# pyinstaller
pyinstaller --onefile cli.py
# → dist/cli  (single binary, with embedded Python)

# uv tool install
uv tool install .
# → installs as user-level tool
```

Or distribute as Python package on PyPI:
```bash
pip install mytool
mytool deploy ...
```

## Configuration Files

```python
import yaml
from pathlib import Path

def load_config():
    p = Path.home() / ".mytool" / "config.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text())

@app.command()
def deploy(service: str):
    cfg = load_config()
    ...
```

## Plugin Architecture

For extensible CLIs:
- Each plugin is a separate package
- CLI discovers via entry_points
- Click `click-plugins` package

## Click vs Typer

| | Click | Typer |
|---|---|---|
| Style | Decorators | Type hints |
| Boilerplate | More | Less |
| Maturity | Higher | High enough |
| Recommended | Stable | New code |

Both built on same engine. Typer outputs to Click under the hood.

## Common Mistakes

- Using `print` instead of `typer.echo` (loses formatting)
- No `--help` examples in docstrings
- Subcommand with required arg as positional → confusing UX
- Heavy imports → slow CLI startup

## Operations

For `argcomplete` (bash/zsh completion):
```bash
typer cli.py utils install-completion
# Future: tab completion works
```

## Best Practices

- Prefer Typer for new CLIs: type hints become args/options/validation for free, and it builds on Click so you keep the ecosystem.
- Write to `typer.echo`/`rich` and send diagnostics to stderr; reserve stdout for machine-parseable output so the tool composes in pipes.
- Exit with explicit, meaningful codes via `raise typer.Exit(code=...)` — 0 success, non-zero per failure class.
- Add a `--dry-run` and a `--yes/--force` flag to any command that mutates infrastructure, and confirm destructive actions by default.
- Keep top-level imports light (lazy-import heavy SDKs like boto3 inside the command) so `--help` and startup stay fast.
- Provide examples in command docstrings and ship shell completion so the CLI is discoverable.

## Quick Refs

```python
# Typer skeleton: typed args -> validation + help for free
import typer

app = typer.Typer(help="Deploy tool")

@app.command()
def deploy(
    service: str,
    replicas: int = typer.Option(3, help="Desired replica count"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    if dry_run:
        typer.echo(f"Would scale {service} to {replicas}")
        raise typer.Exit()
    if not yes:
        typer.confirm(f"Scale {service} to {replicas}?", abort=True)
    typer.echo(f"Scaled {service} -> {replicas}")

if __name__ == "__main__":
    app()
```

```bash
python cli.py deploy web --replicas 5 --dry-run
python cli.py --install-completion        # enable shell completion
uv tool install .                          # install CLI as a user-level tool
pyinstaller --onefile cli.py               # single self-contained binary
```

## Interview Prep

**Junior**: "argparse vs Click vs Typer?"

**Mid**: "Build kubectl-style CLI in Python."

**Senior**: "Slow CLI — diagnose."

## Next Topic

→ [T07 — Testing with pytest](T07-Pytest.md)
