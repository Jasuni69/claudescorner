# Eventstream

## Q1 — Resolving runtime errors in eventstream

**Scenario:** Company uses Microsoft Fabric eventstream for real-time data. Frequent runtime errors affect processing. Need to identify and resolve them.

**Question:** Which three actions should be performed?

| Action | Correct |
|--------|---------|
| Check Data insights for event metrics | ✅ |
| Disable eventstream data transformation | ❌ |
| Filter logs by error severity | ✅ |
| Modify data transformation logic | ❌ |
| Review Runtime logs for error details | ✅ |

**Why:**
- **Runtime logs** → detailed error info, essential for diagnosis
- **Data insights** → identifies performance bottlenecks
- **Filter by severity** → prioritizes critical errors

**Why not:**
- Modifying transformation logic doesn't resolve the root cause
- Increasing node count doesn't address runtime errors

---

## Q2 — Remove unnecessary columns before storing IoT data in Delta Lake

**Scenario:** IoT data from Azure Event Hubs ingested into Delta Lake. Need to strip sensor ID columns before storage.

**Question:** What should you do?

| Action | Correct |
|--------|---------|
| Store in staging area and filter before final storage | ❌ |
| Use a batch processing system to clean before transfer | ❌ |
| Use a Spark job to preprocess before ingestion | ❌ |
| Use the event processor to remove unnecessary columns | ✅ |

**Why:**
- **Event processor** → built-in filtering at ingestion time; automates column removal before data hits the lakehouse

**Why not:**
- Spark job → works but unnecessarily complex/resource-intensive vs native tooling
- Staging area → adds processing/storage inefficiency
- Batch processing → introduces delays; not suited for real-time streams

---

## Q3 — No-code ingestion and transformation of IoT streaming data

**Scenario:** Real-time IoT data in Fabric. Need to ingest and transform without writing code.

**Question:** What should you do?

| Action | Correct |
|--------|---------|
| Use Azure Event Hubs to ingest and transform | ❌ |
| Use Azure Stream Analytics | ❌ |
| Use Spark Structured Streaming with PySpark | ❌ |
| Use eventstreams feature with enhanced capabilities | ✅ |

**Why:**
- **Eventstreams (enhanced)** → built-in no-code UI for ingestion + transformation of streaming data in Fabric

**Why not:**
- Stream Analytics → requires writing queries → not no-code
- Event Hubs → requires code for transformation
- PySpark Structured Streaming → code-based

> **Key term:** "enhanced capabilities" = the no-code transformation mode in Fabric eventstreams.

---
