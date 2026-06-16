# L06/C03/T04 — Cobra for CLIs (kubectl, helm, hugo all use it)

## Learning Objectives

- Build production CLI tools in Go
- Use Cobra + Viper

## Cobra

The de facto Go CLI framework. Used by:
- kubectl
- helm
- hugo
- docker
- istioctl
- gh (GitHub CLI)
- Many more

```bash
go get github.com/spf13/cobra
go get github.com/spf13/cobra-cli       # generator
cobra-cli init
cobra-cli add deploy
cobra-cli add rollback
```

## Minimal Structure

```go
// cmd/root.go
package cmd

import (
    "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
    Use:   "mytool",
    Short: "My DevOps tool",
    Long:  "Longer description here",
}

func Execute() error {
    return rootCmd.Execute()
}
```

```go
// cmd/deploy.go
var deployCmd = &cobra.Command{
    Use:   "deploy [service]",
    Short: "Deploy a service",
    Args:  cobra.ExactArgs(1),
    Run: func(cmd *cobra.Command, args []string) {
        service := args[0]
        version, _ := cmd.Flags().GetString("version")
        deploy(service, version)
    },
}

func init() {
    rootCmd.AddCommand(deployCmd)
    deployCmd.Flags().StringP("version", "v", "latest", "Version to deploy")
    deployCmd.Flags().Bool("dry-run", false, "Don't actually deploy")
}
```

```go
// main.go
func main() {
    if err := cmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

```bash
$ mytool deploy myapp -v v1.2.3
$ mytool deploy myapp --version=v1.2.3
$ mytool deploy myapp --dry-run
$ mytool --help
$ mytool deploy --help
```

## Subcommand Hierarchy

```
mytool
├── deploy
├── rollback
├── config
│   ├── view
│   └── set
└── get
    ├── pods
    └── services
```

```go
configCmd := &cobra.Command{Use: "config"}
viewCmd := &cobra.Command{Use: "view", Run: func(...) {...}}
setCmd := &cobra.Command{Use: "set", Run: func(...) {...}}

configCmd.AddCommand(viewCmd)
configCmd.AddCommand(setCmd)
rootCmd.AddCommand(configCmd)
```

## Flags

### Persistent (Inherit)
Available on this command + all subcommands:
```go
rootCmd.PersistentFlags().StringVar(&kubeconfig, "kubeconfig", "", "kubeconfig path")
```

### Local
Only this command:
```go
deployCmd.Flags().Bool("dry-run", false, "...")
```

### Required
```go
deployCmd.MarkFlagRequired("version")
```

### Types
```go
cmd.Flags().StringP("name", "n", "default", "help")
cmd.Flags().IntP("count", "c", 1, "...")
cmd.Flags().BoolP("verbose", "v", false, "...")
cmd.Flags().StringSlice("tags", []string{}, "...")     // --tags a,b,c
cmd.Flags().Duration("timeout", 5*time.Second, "...")
```

## Args Validation

```go
Args: cobra.ExactArgs(2),
Args: cobra.MinimumNArgs(1),
Args: cobra.NoArgs,
Args: cobra.OnlyValidArgs,
ValidArgs: []string{"start", "stop"},

// Custom
Args: func(cmd *cobra.Command, args []string) error {
    if len(args) < 1 {
        return errors.New("requires service name")
    }
    return nil
},
```

## Pre/Post Hooks

```go
PreRun: func(cmd *cobra.Command, args []string) {
    setupLogging()
},
Run: func(cmd *cobra.Command, args []string) {
    doWork()
},
PostRun: func(cmd *cobra.Command, args []string) {
    cleanup()
},
```

`PersistentPreRun`: inherited to subcommands.

## Viper for Config

Cobra + Viper: config files, env vars, flags merged.

```bash
go get github.com/spf13/viper
```

```go
import "github.com/spf13/viper"

func initConfig() {
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath("$HOME/.mytool")
    viper.AddConfigPath(".")
    viper.AutomaticEnv()                  // MYTOOL_DATABASE_URL → viper.GetString("database.url")
    
    if err := viper.ReadInConfig(); err == nil {
        log.Println("Using config:", viper.ConfigFileUsed())
    }
}

// Bind flags to viper
viper.BindPFlag("region", deployCmd.Flags().Lookup("region"))

// Get value (precedence: flag > env > config > default)
region := viper.GetString("region")
```

## Command Completion

```go
// Auto-generate completion script
mytool completion bash > /etc/bash_completion.d/mytool
mytool completion zsh > "${fpath[1]}/_mytool"
mytool completion fish > ~/.config/fish/completions/mytool.fish
```

Hook custom completion:
```go
deployCmd.RegisterFlagCompletionFunc("service", func(...) ([]string, cobra.ShellCompDirective) {
    return []string{"web", "api", "worker"}, cobra.ShellCompDirectiveNoFileComp
})
```

## Help Customization

Cobra generates `--help` automatically. To customize:
```go
rootCmd.SetUsageTemplate(...)
rootCmd.SetHelpTemplate(...)
```

Examples:
```go
deployCmd.Example = `  # Deploy latest
  mytool deploy myapp
  
  # Specific version
  mytool deploy myapp -v v1.2.3`
```

## Output

Stdout for data; stderr for messages:
```go
fmt.Fprintln(cmd.OutOrStdout(), "data")
fmt.Fprintln(cmd.ErrOrStderr(), "warning")
```

For colors / formatting: `github.com/fatih/color`.

## Exit Codes

```go
Run: func(cmd *cobra.Command, args []string) {
    if err := doWork(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
},

// Or use RunE for error
RunE: func(cmd *cobra.Command, args []string) error {
    return doWork()
},
```

`RunE`: Cobra exits 1 if non-nil error returned.

## Building & Distribution

```bash
# Static binary
go build -o mytool

# Strip; smaller
go build -ldflags="-s -w" -o mytool

# With version
go build -ldflags="-X main.version=v1.0.0" -o mytool

# Cross-compile
GOOS=linux GOARCH=amd64 go build -o mytool-linux-amd64
```

Distribute via:
- GitHub releases (use goreleaser)
- Homebrew tap
- apt/yum
- Docker image

## goreleaser

Automate release builds + GitHub uploads:
```yaml
# .goreleaser.yaml
builds:
  - main: ./cmd/mytool
    goos: [linux, darwin, windows]
    goarch: [amd64, arm64]

archives:
  - format: tar.gz
```

```bash
goreleaser release
```

## Common Mistakes

- Heavy logic in `Run`; should be testable funcs
- Forgetting flag validation
- Not differentiating stdout/stderr
- No version flag

## Testing Cobra Commands

```go
func TestDeploy(t *testing.T) {
    var stdout bytes.Buffer
    cmd := rootCmd
    cmd.SetOut(&stdout)
    cmd.SetArgs([]string{"deploy", "myapp", "-v", "v1"})
    
    err := cmd.Execute()
    assert.NoError(t, err)
    assert.Contains(t, stdout.String(), "deployed")
}
```

## Best Practices

- Keep `RunE` thin: parse/validate flags, then call a plain testable function; return errors instead of `os.Exit` so Cobra sets the exit code.
- Write results to `cmd.OutOrStdout()` and diagnostics to `cmd.ErrOrStderr()` so tests can capture output and pipes stay clean.
- Use `RunE`/`PersistentPreRunE` (the `E` variants) so errors propagate and the process exits non-zero on failure.
- Wire config precedence with Viper (flag > env > file > default) and bind flags via `viper.BindPFlag`.
- Add a `--version` (ldflags-injected) and ship shell completion via Cobra's built-in `completion` command.
- Validate positional args with `cobra.ExactArgs`/`cobra.MinimumNArgs` rather than hand-rolled length checks.

## Quick Refs

```go
// Command with validation, env-bound flags, and propagated errors
var rootCmd = &cobra.Command{Use: "tool", Version: version}

var deployCmd = &cobra.Command{
    Use:  "deploy <service>",
    Args: cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        replicas := viper.GetInt("replicas")
        return runDeploy(cmd.Context(), args[0], replicas)  // testable
    },
}

func init() {
    deployCmd.Flags().Int("replicas", 3, "desired replicas")
    _ = viper.BindPFlag("replicas", deployCmd.Flags().Lookup("replicas"))
    viper.SetEnvPrefix("TOOL")            // TOOL_REPLICAS
    viper.AutomaticEnv()
    rootCmd.AddCommand(deployCmd)
}
```

```yaml
# .goreleaser.yaml — cross-platform release binaries
builds:
  - env: [CGO_ENABLED=0]
    goos: [linux, darwin]
    goarch: [amd64, arm64]
    ldflags: ["-s -w -X main.version={{.Version}}"]
```

```bash
go build -ldflags="-X main.version=$(git describe --tags)" -o tool .
goreleaser release --clean        # build + checksums + archives + release
goreleaser build --snapshot --clean   # local test build, no publish
```

## Interview Prep

**Mid**: "Why Cobra?"

**Senior**: "Implement subcommand hierarchy."

**Staff**: "Plugin architecture for CLI."

## Next Topic

→ [T05 — client-go for Kubernetes](T05-Client-Go.md)
