# Notebooks & Spark

## Q1 — Enhance Spark job performance without code changes

**Scenario:** Performance issues with Spark jobs on Delta format data (complex transformations/aggregations). Cannot modify codebase.

**Question:** What should you do?

| Action | Correct |
|--------|---------|
| Enable adaptive query execution | ❌ |
| Enable dynamic allocation | ❌ |
| Enable high concurrency mode | ❌ |
| Enable native execution engine | ✅ |

**Why:**
- **Native execution engine** → optimizes complex Spark jobs via environment settings, no code changes needed; specifically targets transformations/aggregations on Delta data

**Why not:**
- Adaptive query execution doesn't directly address Delta transformation performance
- Dynamic allocation can cause resource inefficiencies
- High concurrency mode is for multi-user session sharing, not throughput

---

## Q2 — Spark Structured Streaming to Delta table without errors on data changes

**Scenario:** IoT streaming data written to Delta table via Spark Structured Streaming. Need to handle data changes without errors.

**Question:** What should you do?

| Action | Correct |
|--------|---------|
| Enable overwrite mode | ❌ |
| Set checkpointLocation to null | ❌ |
| Use ignoreChanges | ✅ |
| Use the Append method | ❌ |

**Why:**
- **ignoreChanges** → allows stream to tolerate data modifications in Delta source without throwing errors

**Why not:**
- Overwrite mode replaces existing data — breaks streaming continuity
- `checkpointLocation = null` → no state tracking → data loss risk
- Append only adds new data; doesn't handle modifications → potential duplication

---

## Q3 — Near real-time IoT ingestion into KQL database

**Scenario:** IoT temperature/humidity data streamed into Fabric KQL database. Need efficient ingestion + near real-time querying.

**Question:** What should you do?

| Action | Correct |
|--------|---------|
| Spark Structured Streaming → Delta table | ✅ |
| Store in Blob Storage, load periodically into KQL | ❌ |
| Use Azure Data Explorer for storage and querying | ❌ |
| Use Azure Stream Analytics | ❌ |

**Why:**
- **Spark Structured Streaming → Delta table** → efficient continuous ingestion + near real-time query support within Fabric

**Why not:**
- Stream Analytics → doesn't integrate with Fabric KQL database
- Blob Storage + periodic load → not real-time
- Azure Data Explorer → not directly integrated with Fabric KQL database

> **Trap:** Even though the scenario mentions a KQL database, the correct ingestion path is Spark Structured Streaming to Delta — not piping directly into KQL via ADX.

---

## Q4 — Streaming data transformation and storage in lakehouse

**Scenario:** Streaming data from various sources. Need transformation + storage in lakehouse for analytics.

**Question:** Which method?

| Action | Correct |
|--------|---------|
| Azure Data Factory | ❌ |
| Azure Stream Analytics | ❌ |
| Azure Synapse Analytics | ❌ |
| Spark Structured Streaming with Delta tables | ✅ |

**Why:**
- **Spark Structured Streaming + Delta** → real-time transformation + ACID-compliant lakehouse storage; built for this exact pattern

**Why not:**
- ADF → batch-oriented, lacks real-time streaming capability
- Stream Analytics → real-time processing only, not lakehouse storage
- Synapse → not designed for real-time streaming + lakehouse ingestion

---

## Q5 — Filter invalid data and add calculated fields before lakehouse storage

**Scenario:** Large streaming data volumes. Need to filter invalid rows and add calculated fields before storing in lakehouse.

**Question:** Which three actions?

| Action | Correct |
|--------|---------|
| Add calculated columns using Spark SQL expressions | ✅ |
| Filter out rows with NULL values in critical columns | ✅ |
| Use a CSV file for batch processing | ❌ |
| Use batch processing for data transformations | ❌ |
| Use Spark Structured Streaming to read the data stream | ✅ |

**Why:**
- **Spark Structured Streaming** → reads continuous data stream into DataFrame
- **Filter NULLs** → ensures only valid data is stored
- **Calculated columns (Spark SQL)** → enriches stream before write

**Why not:**
- CSV batch → no real-time support
- Batch processing → doesn't support continuous data flow

---

## Q6 — Configure streaming job for near real-time IoT querying

**Scenario:** IoT streaming data in Fabric. Need to configure a job to ingest into a table for near real-time queries.

**Question:** Which three actions?

| Action | Correct |
|--------|---------|
| Create Spark Job Definition with Python Structured Streaming script | ✅ |
| Set the checkpoint location | ✅ |
| Store data in JSON file for later analysis | ❌ |
| Use batch processing to ingest into lakehouse | ❌ |
| Use Delta table as sink | ✅ |

**Why:**
- **Spark Job Definition (Python/Structured Streaming)** → processes and writes streaming data continuously
- **Delta table as sink** → structured format enabling efficient queries + ACID
- **Checkpoint location** → maintains stream state, ensures fault tolerance

**Why not:**
- JSON file → no real-time query support, no transactions
- Batch processing → no continuous flow support

---

## Q7 — Efficient streaming processing for prompt querying

**Scenario:** IoT streaming data in Fabric. Need efficient processing for near real-time querying.

**Question:** Which two actions?

| Action | Correct |
|--------|---------|
| Implement Spark Structured Streaming | ✅ |
| Set up a SQL analytics endpoint | ✅ |
| Store streaming data in JSON file | ❌ |
| Use Azure Stream Analytics | ❌ |
| Use batch processing every hour | ❌ |

**Why:**
- **Spark Structured Streaming** → writes stream to Delta tables continuously; ACID support
- **SQL analytics endpoint** → enables near real-time SQL queries on Delta tables in the lakehouse

**Why not:**
- JSON file → no ACID, no real-time query
- Stream Analytics → not the native Fabric streaming tool
- Hourly batch → not near real-time

---

## Q8 — Streaming data processed and accessible for analysis (variant of Q7)

**Same correct pattern:** Spark Structured Streaming + SQL analytics endpoint.

| Action | Correct |
|--------|---------|
| Configure a SQL analytics endpoint | ✅ |
| Set up a Power BI dataflow | ❌ |
| Use Azure Stream Analytics | ❌ |
| Use Spark Structured Streaming | ✅ |

**Additional distractor:**
- **Power BI dataflow** → not suitable for real-time streaming ingestion

> See Q7 for full explanation. This question tests the same concept with Power BI dataflow as an extra distractor.

---
