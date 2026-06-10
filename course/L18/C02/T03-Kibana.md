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

**Mid**: "What's Kibana."

**Senior**: "Dashboard design."

## Next Topic

→ [T04 — Index Lifecycle Management](T04-ILM.md)
