# Lakehouses & Data Warehouse

## Q1 — Efficient data ingestion from Azure Blob Storage

**Scenario:** Data warehouse on Fabric, loading large datasets from Azure Blob Storage. Need efficient ingestion with minimal errors.

**Question:** What should you do?

| Action | Correct |
|--------|---------|
| Enable data partitioning before loading | ❌ |
| Use a single INSERT statement for each row | ❌ |
| Use COPY statement with wildcards | ✅ |
| Use multiple INSERT statements for each row | ❌ |

**Why:**
- **COPY with wildcards** → bulk loads from multiple files in one operation, efficient and low error surface

**Why not:**
- Partitioning optimizes query performance, not ingestion
- Single/multiple INSERT per row is slow and error-prone at scale

**Ref:** [Load data using T-SQL — Microsoft Learn](https://learn.microsoft.com/training)

---

## Q2 — Reduce storage costs by removing unnecessary files

**Scenario:** Increased storage costs from old files no longer needed. Must maintain data integrity.

**Question:** What should you do?

| Action | Correct |
|--------|---------|
| Enable V-Order compression | ❌ |
| Reduce file retention period | ❌ |
| Use the OPTIMIZE command | ❌ |
| Use VACUUM command | ✅ |

**Why:**
- **VACUUM** → removes unreferenced files older than retention threshold; reduces storage without touching live data

**Why not:**
- V-Order → optimizes compression/read, doesn't delete files
- Reducing retention period → risks data integrity and breaks Delta time travel
- OPTIMIZE → consolidates small files for performance, doesn't delete unreferenced ones

---

## Q3 — Maintenance strategies for Delta table query performance

**Scenario:** Large lakehouse with frequently updated Delta tables. Query performance degraded over time.

**Question:** Which three actions should you recommend?

| Action | Correct |
|--------|---------|
| Apply V-Order | ✅ |
| Enable Delta caching | ❌ |
| Use the OPTIMIZE command | ✅ |
| Reduce the retention period | ❌ |
| Use the VACUUM command | ✅ |

**Why:**
- **V-Order** → optimizes sorting, encoding, compression of Delta Parquet files → faster reads
- **OPTIMIZE** → bin-compaction; consolidates small Parquet files into larger ones → fewer files scanned
- **VACUUM** → removes old unreferenced files → reduces storage clutter

**Why not:**
- Delta caching can increase memory pressure and degrade performance if unmanaged
- Reducing retention risks data loss and breaks time travel

---

## Q4 — Loading pattern supporting full and incremental loads

**Scenario:** Lakehouse with data from Azure Event Hubs and local files, used for Power BI reports. Need both full and incremental load support.

**Question:** Which approach?

| Action | Correct |
|--------|---------|
| Develop a custom ETL tool | ❌ |
| Use Azure Synapse Analytics | ❌ |
| Use Data Factory for incremental loads | ❌ |
| Use Dataflows Gen2 for full and incremental loads | ✅ |

**Why:**
- **Dataflows Gen2** → natively supports both full and incremental load modes in Fabric; flexible and efficient for report generation

**Why not:**
- Custom ETL → unnecessary when native tools exist
- Data Factory → handles incremental but not both modes together in this context
- Synapse → doesn't specifically address full+incremental in Fabric lakehouse

---

## Q5 — Incremental data loads with data integrity

**Scenario:** Large lakehouse with multi-region sales transactions. Need incremental load strategy with integrity and consistency.

**Question:** Which two actions?

| Action | Correct |
|--------|---------|
| Adopt a medallion architecture | ✅ |
| Load directly into dimensional model without transformation | ❌ |
| Use Data Factory pipelines for transformation | ❌ |
| Use Dataflows Gen2 for transformation and cleaning | ✅ |

**Why:**
- **Medallion architecture** → organizes data into Bronze/Silver/Gold layers; supports incremental loading and quality gates at each stage
- **Dataflows Gen2** → Power Query-based visual transforms; cleans data before dimensional load

**Why not:**
- Direct load to dimensional model → skips cleansing → inconsistencies
- Data Factory → less efficient than Dataflows Gen2 for this pattern

---

## Q6 — Incremental load querying solution with minimal maintenance

**Scenario:** Lakehouse1 with Sales table. Incremental loads from CSV in `/files/sales/`. Minimize maintenance effort.

**Question:** What should you use?

| Action | Correct |
|--------|---------|
| A notebook | ✅ |
| A pipeline | ❌ |
| A stored procedure | ❌ |
| Auto Loader | ❌ |

**Why:**
- **Notebook** → flexible code-based incremental load patterns; low maintenance in Fabric lakehouse context

**Why not:**
- **Auto Loader** → not available in Microsoft Fabric
- **Stored procedures** → not a lakehouse querying solution
- **Pipeline** → orchestration tool, not a querying solution

> **Trap:** Auto Loader is an Azure Databricks feature — not present in Fabric.

---

## Q7 — Integrate warehouse + lakehouse data into single table, minimal effort

**Scenario:** Need to combine data from a warehouse and a lakehouse into one table for analysis.

**Question:** What should you use?

| Action | Correct |
|--------|---------|
| Azure Data Factory | ❌ |
| CREATE TABLE AS SELECT (CTAS) | ✅ |
| Dataflow Gen2 | ❌ |
| SELECT INTO | ❌ |

**Why:**
- **CTAS** → creates a new table from a SELECT across multiple sources in one statement; minimal code, minimal effort

**Why not:**
- Dataflow Gen2 → data prep/transform tool; doesn't directly create tables from combined sources
- SELECT INTO → can create tables but not designed for multi-source integration
- ADF → orchestration/integration service; doesn't directly create tables in-place

---

## Q8 — Data store for diverse formats + PySpark + SQL

**Scenario:** Ingesting structured, semi-structured, and unstructured data. Need PySpark and SQL support.

**Question:** Which two data stores? (each is a complete solution independently)

| Action | Correct |
|--------|---------|
| Azure Data Lake Storage Gen2 | ❌ |
| Azure Synapse Analytics | ✅ |
| Microsoft Fabric Eventhouse | ❌ |
| Microsoft Lakehouse | ✅ |

**Why:**
- **Lakehouse** → supports all data formats; native PySpark + SQL via Fabric
- **Synapse Analytics** → supports all formats; T-SQL + Spark pool operations

**Why not:**
- ADLS Gen2 → stores diverse formats but has no native PySpark/SQL execution
- Eventhouse → real-time analytics focus; not optimized for batch transforms with PySpark/SQL

---
