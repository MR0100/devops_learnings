# L04/C02/T05 — jq for JSON, yq for YAML

## Learning Objectives

- Query JSON with jq fluently
- Transform JSON
- Use yq for YAML

## jq Basics

```bash
echo '{"name":"alice","age":30}' | jq
# Pretty-prints
```

## Extract Fields

```bash
jq '.name' data.json                       # field
jq '.users[0].name' data.json              # nested + array index
jq '.users[].name' data.json               # all names
jq '.users[]' data.json                    # iterate
jq '.["odd-name"]' data.json               # bracket for special chars
```

## Filters

```bash
jq '.users[] | select(.age > 30)' data.json
jq '.[] | select(.status == "active")' data.json
jq 'select(.tags | contains(["prod"]))' data.json
```

## Transform / Map

```bash
jq '.users | map({id: .id, name: .name})' data.json
jq '.users[] | {id, name}' data.json       # shorthand
jq '.[].user.email' data.json
jq 'map(.price * 1.2)' data.json
```

## Conditionals

```bash
jq 'if .status == "active" then "✓" else "✗" end' data.json
jq '.users[] | if .age >= 18 then . else empty end' data.json
```

## Aggregations

```bash
jq 'length' data.json                       # array/object size
jq '[.users[].age] | add' data.json         # sum
jq '[.users[].age] | min' data.json         # min
jq '[.users[].age] | max' data.json
jq '[.users[].age] | add/length' data.json  # average
```

## String Operations

```bash
jq '.name | ascii_upcase' data.json
jq '.name | length' data.json
jq '.name | startswith("a")' data.json
jq '.name | test("[A-Z]")' data.json        # regex
jq '.path | split("/")' data.json
jq '[.tags[]] | join(",")' data.json
```

## Raw Output

```bash
jq -r '.name' data.json                     # no JSON quotes
jq -r '.users[].email' data.json            # for piping to other tools
```

`-r` is essential when output feeds non-JSON tools.

## Group By

```bash
jq 'group_by(.dept) | map({dept: .[0].dept, count: length})' users.json
```

## Real Examples

### Kubernetes
```bash
kubectl get pods -o json | jq '.items[] | {name: .metadata.name, status: .status.phase}'

kubectl get pods -o json | jq '.items[] | select(.status.phase != "Running") | .metadata.name'

kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, cpu: .status.allocatable.cpu, mem: .status.allocatable.memory}'
```

### AWS
```bash
aws ec2 describe-instances | jq '.Reservations[].Instances[] | {id: .InstanceId, state: .State.Name, ip: .PrivateIpAddress}'

aws s3api list-buckets | jq -r '.Buckets[].Name'

aws cloudwatch list-metrics --namespace AWS/EC2 | jq '.Metrics[] | .MetricName' | sort -u
```

### Log Analysis
```bash
# Top error codes
cat structured.log | jq -r 'select(.level=="error") | .error_code' | sort | uniq -c | sort -rn
```

## Update / Set

```bash
jq '.name = "new_name"' data.json
jq '.users[0].age = 35' data.json
jq '.tags += ["new"]' data.json             # append
jq 'del(.password)' data.json               # delete field
jq '.users |= map(. + {active: true})' data.json
```

## Combine / Multi-File

```bash
# Combine
jq -s '.[0] + .[1]' file1.json file2.json    # merge top-level

# Or
jq -s 'add' *.json                           # add many

# Apply same filter to many
jq '.name' *.json
```

## Compact vs Pretty

```bash
jq -c '.users' data.json                     # one line
jq '.users' data.json                        # pretty (default)
```

## Variables and Arguments

```bash
jq --arg name "alice" '.users[] | select(.name == $name)' data.json
jq --argjson n 30 '.users[] | select(.age > $n)' data.json
```

## yq

YAML processor. Mike Farah's yq (Go) is most common.

```bash
yq '.metadata.name' deployment.yaml
yq '.spec.containers[].image' pod.yaml
yq '.spec.replicas = 5' deployment.yaml       # set; outputs new YAML
yq -i '.spec.replicas = 5' deployment.yaml    # in-place
yq -o json deployment.yaml                    # convert YAML → JSON
yq -o yaml '.spec' deployment.yaml > spec.yaml
```

### Multi-doc YAML
```bash
yq '.kind' multi.yaml         # all docs
yq 'select(.kind == "Deployment")' multi.yaml
```

### From JSON
```bash
cat data.json | yq -P              # JSON → YAML
```

## Combine jq and yq

```bash
kubectl get cm -o yaml | yq '.items[].metadata.name'

yq -o json deployment.yaml | jq '.spec.containers[]'
```

## Tools

- **jq** — JSON; most ubiquitous
- **yq** (Mike Farah) — YAML; recommended
- **dasel** — multi-format (JSON, YAML, TOML, XML)
- **gron** — flatten JSON for grep-friendliness

## Common Mistakes

- **Forgetting `-r`**: piping jq output to another tool while it still has JSON quotes (`"name"`) breaks the consumer. Use `-r` for raw strings.
- **Interpolating shell variables into the program**: `jq ".name==\"$x\""` is fragile and injectable. Pass values with `--arg`/`--argjson`.
- **Confusing the two `yq`s**: Mike Farah's Go `yq` and the Python `yq` wrapper have different syntax; scripts written for one fail on the other.
- **`yq -i` rewriting comments/formatting**: in-place edits can drop YAML comments and reorder keys — review the diff before committing.
- **Assuming one JSON document**: streamed/NDJSON input needs `jq -s` (slurp) or per-line processing, not a single filter.
- **Iterating with `.[]` over a possibly-null field**: errors out; guard with `.field // [] | .[]` or use `?` (`.[]?`).

## Best Practices

- Use `-r` whenever output feeds non-JSON tools, and `-c` for compact one-object-per-line streams.
- Inject external data with `--arg name value` (string) or `--argjson name '{...}'` (parsed JSON); never string-concatenate.
- Build filters incrementally — pipe stages (`.a | .b[] | select(...)`) and test each addition against real input.
- Standardize on Mike Farah's `yq` for YAML and convert to JSON (`yq -o=json`) when you want jq's full power.
- Prefer `jq -e` in scripts so a `false`/`null`/empty result sets a non-zero exit code you can branch on.
- For multi-document YAML, filter with `select(.kind == "...")` rather than positional indexing.

## Quick Refs

```bash
# Extract / iterate
jq '.name' f.json                 # field
jq -r '.items[].metadata.name' f  # raw strings from an array
jq '.users[] | {id, name}'        # project specific keys

# Filter / select
jq '.[] | select(.age > 30)'                 # by condition
jq -e '.status == "active"'                  # exit code reflects result

# Transform / aggregate
jq 'map(.price * 1.2)'                        # map over array
jq '[.users[].age] | add/length'             # average
jq 'group_by(.dept) | map({dept:.[0].dept, n:length})'

# Mutate
jq '.replicas = 5'                            # set
jq 'del(.secret)'                             # delete field
jq '.tags += ["new"]'                         # append

# Pass shell values safely
jq --arg n "$name" '.users[] | select(.name==$n)' f.json
jq --argjson min 30 '.users[] | select(.age >= $min)' f.json

# Slurp multiple inputs / merge
jq -s 'add' *.json

# yq (Mike Farah)
yq '.spec.replicas' deploy.yaml
yq -i '.spec.replicas = 5' deploy.yaml        # in-place
yq -o=json deploy.yaml | jq '.spec'           # YAML -> JSON -> jq
yq 'select(.kind == "Deployment")' multi.yaml
```

## Interview Prep

**Mid**: "Extract all pod names from kubectl JSON."

**Senior**: "Filter pods not in Running state."

**Staff**: "Pipeline: list all S3 buckets in account, output as CSV."

## Next Chapter

→ [C03 — Advanced Bash](../C03/README.md)
