# L18/C02/T03 — Kibana

## Learning Objectives

- Use Kibana
- Build dashboards

## Kibana

UI for ES:
- Search logs
- Dashboards
- Visualizations
- Alerts (in some tiers)

## Install

```bash
helm install kibana elastic/kibana
```

```bash
docker run -p 5601:5601 kibana
```

## Discover

Search logs:
```
KQL: level: "error" AND service: "api"
```

Or Lucene:
```
level:error AND service:api
```

Filter, time range, columns.

## Visualizations

- Bar / line chart
- Pie
- Data table
- Heatmap
- Tag cloud
- Maps

Build from search.

## Dashboards

Combine visualizations:
- Per-service
- Error trends
- Infrastructure

## Index Patterns

```
Settings → Data Views → Create
Pattern: logs-*
Time field: @timestamp
```

Tells Kibana which indices.

## Lens

Drag-drop visualization. Modern.

## TSVB / Time Series

For time-based views.

## Maps

Geographic:
- Heat maps of IP origins
- Per-region metrics

## Saved Objects

- Searches
- Visualizations
- Dashboards

Export / import.

## Spaces

Multi-tenant:
- Per team
- Per project

## RBAC

- Read
- Write
- Admin

Per index, dashboard, or space.

## Alerts (Watcher / Kibana)

Email / Slack / PagerDuty.

## Dev Tools

REST console for ES queries:
```
GET _cluster/health
POST my-index/_search { ... }
```

## Machine Learning (Paid)

- Anomaly detection
- Auto-categorization
- Forecasts

For: data scientists; expensive.

## Best Practices

- Saved searches reusable
- Dashboards per audience
- Time range default sensible
- Spaces for teams
- Backup saved objects

## Common Mistakes

- Index pattern too broad
- Aggregation on text field (use keyword)
- No dashboards (only Discover)

## Performance

- Aggregations slow on huge data
- Use date_histogram
- Limit time range

## Quick Refs

```
Discover:      search + filter
Visualize:     create chart
Dashboard:     combine
Dev Tools:     ES API console
KQL:           level:error
Lucene:        level:error AND service:api
```

## Interview Prep

**Junior**: "What is Kibana?" — The visualization and exploration UI for Elasticsearch, used to search logs in Discover, build charts and dashboards, and run raw ES queries from Dev Tools.

**Mid**: "What's a data view (index pattern) and why does it matter?" — It tells Kibana which indices to query and which field is the time field (e.g. `logs-*` with `@timestamp`); too broad a pattern pulls in unrelated indices and slows everything, and aggregating on a `text` field instead of its `keyword` sub-field fails or misbehaves.

**Senior**: "How do you design dashboards for an audience?" — Build per-audience views (on-call sees error rate and latency; capacity sees throughput and saturation), set sensible default time ranges, reuse saved searches, and isolate teams with Spaces and RBAC so dashboards stay focused and access-controlled.

**Staff**: "How do you keep Kibana usable and performant at scale?" — Constrain time ranges and use `date_histogram` so aggregations don't scan everything, back long retention with ILM tiers, version-control and back up saved objects, and govern access with Spaces + RBAC rather than letting every team query every index.

## Next Topic

→ [T04 — Index Lifecycle Management](T04-ILM.md)
