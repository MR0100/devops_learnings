# L18/C03/T02 — LogQL

## Learning Objectives

- Query Loki
- Use filters

## LogQL

Loki Query Language. PromQL-like.

## Stream Selector

```
{app="api"}
{app="api", env="prod"}
{app=~"api|web"}     # regex
{app!="api"}
```

## Filters

After stream:
```
{app="api"} |= "error"    # contains
{app="api"} != "debug"    # not contains
{app="api"} |~ "error|fail"   # regex
{app="api"} !~ "debug"
```

## Parse

JSON:
```
{app="api"} | json
{app="api"} | json | status="500"
```

logfmt:
```
{app="api"} | logfmt
```

regex:
```
{app="api"} | regexp `level=(?P<level>\w+)`
```

## After Parse

```
{app="api"} | json | duration > 1000
{app="api"} | json | status >= 500
```

Filter on parsed fields.

## Aggregations

```
sum(rate({app="api"}[5m]))
count_over_time({app="api"}[5m])
sum by (status) (rate({app="api"} | json | __error__="" [5m]))
```

## Metric Queries

```
rate({app="api"} |= "error" [5m])
sum by (level) (rate({app="api"} | json [5m]))
```

For: log-derived metrics.

## Common Queries

### Error logs
```
{app="api", level="error"}
```

### Find user
```
{app="api"} | json | user_id="alice"
```

### Slow requests
```
{app="api"} | json | duration > 1000
```

### Error rate
```
sum(rate({app="api"} |= "error" [5m]))
/
sum(rate({app="api"} [5m]))
```

### Top errors
```
topk(10, sum by (msg) (count_over_time({app="api", level="error"}[1h])))
```

## Line Format

```
{app="api"} | json | line_format "{{.user_id}} {{.action}}"
```

Reformat output.

## Label Format

```
{app="api"} | json | label_format new_label=other_label
```

Rename.

## Unwrap

For numeric extraction:
```
{app="api"} | json | unwrap duration | quantile_over_time(0.99, ...[5m])
```

For: stats on JSON field.

## Performance Tips

1. Specific labels first (drops streams)
2. Then filters
3. Avoid full regex if simple `|=` works

## Common Mistakes

### Too Broad
```
{} |~ "error"   # scans everything; slow
```

Use labels:
```
{app="api"} |~ "error"
```

### High Cardinality in Filter
```
{user_id="alice"}   # bad: explodes streams
```

### Heavy Parse
```
| json   # expensive per line
```

Use sparingly.

## Compared to ELK

| | LogQL | ES DSL |
|---|---|---|
| Search | filter-based | full-text |
| Aggregations | yes (PromQL-like) | yes (rich) |
| Speed | label fast | content fast |

For: different use cases.

## Time Range

In Grafana / explore. Or:
```
{app="api"}[5m]
```

For range vector functions.

## Examples

### Most errors per service (last 1h)
```
topk(5, sum by (service) (count_over_time({level="error"}[1h])))
```

### Error rate per service
```
sum by (service) (rate({level="error"}[5m]))
/
sum by (service) (rate({}[5m]))
```

### Histogram of latencies
```
histogram_quantile(0.99,
  sum by (le) (rate({app="api"} | json | unwrap duration_ms | __error__="" [5m]))
)
```

## Limits

Loki limits (config):
- Max query length
- Max chunks per query
- Max samples

Tune for huge.

## Best Practices

- Label-first queries
- Avoid `{}` (broad)
- Parse only as needed
- Use rate() for metrics
- Save common queries

## Common Mistakes

- Too broad
- Parse before label filter
- High cardinality
- Regex when not needed

## Quick Refs

```
{labels} |= "string"
{labels} | json | field="value"
rate({labels}[5m])
sum by (X) (count_over_time({labels}[5m]))
```

## Interview Prep

**Junior**: "What is LogQL?" — Loki's PromQL-inspired query language: you start with a `{label="value"}` stream selector, then chain line filters like `|= "error"` and parsers like `| json` to narrow results.

**Mid**: "What's the difference between a stream selector and a line filter?" — The stream selector (`{app="api"}`) uses the index to pick which streams to read and is cheap, while line filters (`|= "error"`, `| json | status="500"`) scan the actual log content and run only on the streams the selector already narrowed to.

**Senior**: "How does querying Loki differ from querying Elasticsearch?" — Loki is fast when you filter by label first then scan content linearly, so it suits label-scoped grep workloads; ES uses an inverted index so arbitrary full-text and rich aggregations are fast, so a bare `{} |~ "error"` in Loki scans everything and is the classic anti-pattern.

**Staff**: "How do you keep LogQL queries fast and cheap at scale?" — Always lead with specific labels to drop streams before scanning, parse (`| json`) only after filtering and only when needed, prefer `|=` over regex when possible, use metric queries (`rate`, `count_over_time`) for log-derived alerting, and tune Loki's per-query chunk/sample limits to cap blast radius.

## Next Topic

→ [T03 — Cost Tradeoffs vs ELK](T03-Loki-vs-ELK.md)
