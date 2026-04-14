# DP-700 Cheat Sheet: Real-Time Intelligence (RTI) in Microsoft Fabric

Sourced from official Microsoft Learn docs, 2026-04-14.

---

## RTI Architecture — 4 core components

```
Sources → Eventstream → Eventhouse (KQL Database) → Dashboards/Alerts
                ↓                    ↓
           Lakehouse            Activator
```

| Component | What it is | Analogy |
|---|---|---|
| **Real-Time Hub** | Central catalog of all streaming data in org | "Stream marketplace" |
| **Eventstream** | No-code data pipeline for streaming events | Azure Stream Analytics |
| **Eventhouse** | Time-series analytics engine (stores KQL databases) | ADX (Azure Data Explorer) |
| **Activator** | Alert/trigger engine that reacts to patterns | Azure Logic Apps for events |

---

## Eventstream — what it does

- Ingest streaming data from 30+ sources (no code required)
- Transform in-flight: filter, aggregate, group by, join, union
- Route to multiple destinations simultaneously
- **No minimum throughput required** — works for any event rate

### Key sources (exam-relevant)
- Azure Event Hubs, IoT Hub, Azure Service Bus
- Azure SQL DB CDC, PostgreSQL CDC, Cosmos DB CDC, MySQL CDC
- Amazon Kinesis, Google Pub/Sub, Confluent Kafka, Apache Kafka
- Fabric Workspace events, OneLake events, Job events
- Custom endpoint (Kafka protocol)

### Key destinations
- **Eventhouse** — primary destination for KQL analytics
- **Lakehouse** — converts to Delta format, stores in tables
- **Activator** — trigger alerts/workflows from stream
- **Custom endpoint** — send to external system
- **Derived stream** — create a new stream after transformation

### Transformation operators
| Operator | Use |
|---|---|
| Filter | Keep/drop events by field value |
| Manage Fields | Add, remove, rename, cast columns |
| Aggregate | Running aggregation (sum/min/max/avg) on time window |
| Group By | Time-window aggregation with grouping |
| Union | Merge two streams with matching schema |
| Join | Combine two streams on matching key |
| Expand | Flatten arrays into rows |

### Ingestion modes to Eventhouse
- **Direct ingestion** — fastest, raw events go straight to KQL table
- **Event processing before ingestion** — apply transformations first, then store

### Limitations
- Max message size: **1 MB**
- Max data retention: **90 days**
- Delivery guarantee: **at-least-once** (not exactly-once)
- Recommended capacity: **F4 or higher**

---

## Eventhouse — what it is

- Container for one or more **KQL databases**
- Optimized for **time-series, streaming, high-cardinality** data
- Auto-organizes data by arrival time
- Supports KQL and T-SQL queries
- Data is exposed in **OneLake as a logical copy** (one-logical-copy)

### Native tables vs OneLake shortcuts

| | **Native Eventhouse table** | **OneLake shortcut in Eventhouse** |
|---|---|---|
| Data stored | In Eventhouse (columnar, KQL-optimized) | In OneLake (Delta Parquet) |
| Latency | Sub-second for fresh data | Minutes (shortcut reads from Delta) |
| Query perf | Fastest for time-series/KQL | Slower for hot data |
| Use when | Real-time analytics, dashboards | Historical/batch data alongside streams |

### Query acceleration for OneLake shortcuts
- Builds a hot cache over OneLake shortcut data in the Eventhouse
- Enables fast KQL queries on external Delta data without full ingestion
- Use when: you want KQL query performance on OneLake data without migrating it

---

## KQL essentials for the exam

### Basic structure
```kql
TableName
| where Timestamp > ago(1h)
| summarize count() by bin(Timestamp, 5m), Region
| order by Timestamp asc
```

### Windowing functions

| Window type | KQL syntax | Description |
|---|---|---|
| Tumbling (non-overlapping) | `summarize ... by bin(Timestamp, 5m)` | Fixed 5-min buckets |
| Sliding | `sliding_window_counts(...)` | Overlapping windows |
| Session | `session_count(...)` | Groups by activity sessions |

### Common aggregations
```kql
// Count events per 5-min window
Events
| summarize Count=count() by bin(Timestamp, 5m)

// Max value in last hour
Sensors
| where Timestamp > ago(1h)
| summarize MaxTemp=max(Temperature) by DeviceId

// Top 10 by count
Errors
| summarize Count=count() by ErrorCode
| top 10 by Count desc
```

### Time filters
```kql
| where Timestamp > ago(1h)           // last hour
| where Timestamp between (ago(7d) .. ago(1d))  // 7d to 1d ago
| where Timestamp > datetime(2026-04-01)
```

### Joins
```kql
Events
| join kind=inner (
    Devices | project DeviceId, DeviceName
) on DeviceId
```

---

## When to use what — exam decision tree

**Streaming data with low latency (<1 min) + KQL queries**
→ Eventstream → Eventhouse (direct ingestion)

**Streaming data + need Delta Lake format for Spark/SQL queries**
→ Eventstream → Lakehouse (Delta conversion)

**IoT/sensor data + alert when threshold exceeded**
→ Eventstream → Eventhouse + Activator on KQL result

**Historical batch data + want KQL query performance**
→ OneLake shortcut in Eventhouse + Query acceleration

**CDC (change data capture) from SQL DB → analytics**
→ Eventstream (CDC connector + DeltaFlow) → Eventhouse

**Stream processing with complex logic / custom SQL**
→ Eventstream SQL operator (preview) or Spark Structured Streaming

---

## Common exam scenarios

**Q: You need to ingest IoT sensor data from Azure IoT Hub and detect temperature anomalies within 30 seconds. What's the architecture?**
→ IoT Hub → Eventstream → Eventhouse → Activator (KQL-based alert)

**Q: You want to query historical OneLake data using KQL alongside fresh streaming data.**
→ Create OneLake shortcut in Eventhouse + enable query acceleration for the shortcut

**Q: A KQL query is running slowly against an Eventstream-fed table with 1 billion rows. What can improve performance?**
→ Use `bin()` for time partitioning in queries; ensure ingestion uses a time-based partition key; check if query acceleration is enabled

**Q: You need to route the same event stream to both an Eventhouse (for analytics) and a Lakehouse (for long-term storage). Is this possible?**
→ Yes — attach multiple destinations to a single Eventstream; each receives data independently

**Q: What is the maximum message size for Eventstream?**
→ 1 MB

**Q: You need exactly-once delivery semantics for a financial transaction stream. Can Eventstream provide this?**
→ No — Eventstream guarantees at-least-once delivery only. For exactly-once, use a deduplication step downstream in the Eventhouse.

---

## Quick memory aids

- **Eventstream = ingest + transform + route** (no code, multiple sources/destinations)
- **Eventhouse = KQL engine** (time-series, fast, Kusto under the hood)
- **Activator = if-this-then-that** for streaming data
- **bin() = tumbling window** in KQL
- **1 MB / 90 days / at-least-once** = Eventstream limits to memorize
- **Direct ingestion = fastest; Event processing before ingestion = transform first**
- **OneLake shortcut + query acceleration** = KQL on external Delta data without full copy
