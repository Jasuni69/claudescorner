# DP-700 Study Guide — Practice Questions

Generated: dp700-study.md | 23 questions across 3 topics  
Study guide last updated: 2026-04-14 (verified against official MS study guide as of April 2026)

> Target: 80%+ on practice assessment

---

## Exam topic weightings (equal — 30–35% each)
1. Implement and manage an analytics solution
2. Ingest and transform data
3. Monitor and optimize an analytics solution

---

## Gap-fill questions (added 2026-04-14 from official study guide review)

### Implement and manage an analytics solution

---

**Q: You need to prevent analysts from seeing the full credit card number in a Fabric Warehouse table, while still allowing them to run queries. The last 4 digits should remain visible. What should you use?**

- A. Row-level security with a DAX filter
- B. Column-level security with DENY
- C. Dynamic data masking with a partial mask function
- D. Sensitivity labels with encryption

**Answer: C**

> Dynamic data masking (DDM) in Fabric Warehouse allows you to mask column values at query time. The `partial()` mask function exposes only specified characters (e.g., last 4 of a credit card). Analysts see masked data without needing schema changes or RLS roles.

---

**Q: A dataset owner wants to signal to other users that a semantic model has been reviewed and is approved for use across the organization. What Fabric feature should they use?**

- A. Workspace roles — set the model to Admin access
- B. Endorse the item using Certified or Promoted status
- C. Apply a sensitivity label with "Confidential" classification
- D. Share the item with organization-wide read access

**Answer: B**

> Fabric item endorsement has two levels: **Promoted** (owner self-attests quality) and **Certified** (requires capacity admin/designated certifier approval). Certification signals org-wide trustworthiness and surfaces items in search/discovery.

---

**Q: You want a Data Factory pipeline to trigger automatically when a new file lands in a OneLake folder. Which trigger type should you use?**

- A. Scheduled trigger — set to poll every 5 minutes
- B. Tumbling window trigger
- C. Storage event trigger
- D. Manual trigger with a Logic App upstream

**Answer: C**

> Storage event triggers (also called event-based triggers) fire when a file is created or deleted in a storage location. In Fabric, this covers OneLake and Azure Data Lake Gen2 paths. This is the correct pattern for file-arrival-driven pipelines.

---

### Ingest and transform data

---

**Q: You need to replicate an Azure SQL Database into Fabric with near-real-time updates, without writing any code. Which Fabric feature should you use?**

- A. Data Factory Copy Activity on a 15-minute schedule
- B. Dataflow Gen2 with incremental refresh
- C. Mirroring
- D. OneLake shortcut to Azure SQL

**Answer: C**

> Fabric Mirroring replicates supported sources (Azure SQL DB, Azure Cosmos DB, Snowflake, etc.) into OneLake continuously using change data capture. No pipeline code required. OneLake shortcuts provide read access but don't replicate data.

---

**Q: A real-time KQL query needs to calculate the maximum sensor reading in each 5-minute non-overlapping window. Which KQL function should you use?**

- A. `summarize ... by bin(Timestamp, 5m)`
- B. `mv-expand` with a 5-minute range
- C. `window ... partition by`
- D. `scan` with a step expression

**Answer: A**

> In KQL, `summarize max(Value) by bin(Timestamp, 5m)` creates non-overlapping (tumbling) 5-minute windows. `bin()` is the KQL equivalent of a tumbling window. For sliding windows, use `sliding_window_counts()`.

---

> 📌 *Full question set regenerated from scripts/dp700_quiz.py — run `python scripts/dp700_quiz.py --interactive` for a randomized scored quiz.*


## Implement and manage an analytics solution

### Q1: You need to store structured data that will be queried via T-SQL by BI tools. The data is updated frequently via MERGE operations. What should you use?

- A. Lakehouse
- B. Warehouse
- C. KQL Database
- D. Eventhouse

**Answer: B**

> Fabric Warehouse is optimized for T-SQL, supports DML (MERGE/UPDATE/DELETE), and is the right choice for BI workloads with frequent updates. Lakehouse is Delta-based and accessed via Spark or SQL endpoint (read-optimized).

### Q2: You are setting up CI/CD for a Fabric workspace. Which tool is the recommended Microsoft-native approach for deploying Fabric items from source control?

- A. Azure DevOps Pipelines with ARM templates
- B. fabric-cicd Python library
- C. Fabric Deployment Pipelines (UI-based)
- D. GitHub Actions with Power BI REST API

**Answer: C**

> Fabric Deployment Pipelines is the native UI-based tool for promoting content across Dev/Test/Prod stages. fabric-cicd is the code-based library for Git-integrated deployments. Both are valid, but Deployment Pipelines is the 'recommended Microsoft-native' approach in exam context.

### Q3: A Fabric workspace needs to be connected to a Git repo. A developer commits changes but they are not reflected in the workspace. What is the most likely cause?

- A. The workspace is not assigned to a Fabric capacity
- B. Git integration was not initialized — workspace was connected but never synced from Git
- C. The developer lacks Contributor role on the workspace
- D. The branch is not 'main'

**Answer: B**

> After connecting a workspace to Git, you must explicitly run 'Update workspace from Git' or 'Commit to Git' to sync. Connection alone does not sync content.

### Q4: You need to implement row-level security on a semantic model so that each salesperson only sees their own region's data. Where do you define the RLS rules?

- A. In the Lakehouse SQL endpoint using GRANT/DENY
- B. In the semantic model via DAX roles and filters
- C. In the Fabric workspace access settings
- D. In the Power BI report filter pane

**Answer: B**

> RLS on semantic models is defined as DAX roles with table filters (e.g., [Region] = USERPRINCIPALNAME()). This is enforced at query time regardless of what report is used.

### Q5: Which Fabric item type provides a SQL analytics endpoint that is automatically generated and updated when new Delta tables are created in a Lakehouse?

- A. Warehouse
- B. SQL Database
- C. Lakehouse SQL endpoint
- D. Eventhouse

**Answer: C**

> Every Lakehouse automatically gets a SQL analytics endpoint — a read-only T-SQL interface over the Delta tables. It updates automatically as tables are created/updated via Spark.

### Q6: You need to allow an external partner to read data from a specific Fabric Lakehouse without giving them workspace access. What is the correct approach?

- A. Share the workspace with the partner as a Viewer
- B. Use OneLake shortcuts to expose data to their tenant
- C. Grant item-level permissions directly on the Lakehouse
- D. Export the data to Azure Blob and share the SAS URL

**Answer: C**

> Fabric supports item-level sharing — you can share a specific Lakehouse or semantic model without granting workspace access. This is the least-privilege approach.


## Ingest and transform data

### Q1: You want to ingest streaming IoT sensor data into Fabric with sub-second latency and query it with KQL. What is the correct architecture?

- A. Event Hub → Data Factory pipeline → Lakehouse → KQL Database
- B. Event Hub → Eventstream → Eventhouse (KQL Database)
- C. Event Hub → Spark Structured Streaming → Delta Lake
- D. IoT Hub → Dataflow Gen2 → Warehouse

**Answer: B**

> Eventstream is the real-time data ingestion component in Fabric. It connects to Event Hub/IoT Hub and routes data directly into an Eventhouse (KQL Database) for low-latency analytics.

### Q2: A Dataflow Gen2 refresh is failing intermittently with gateway timeout errors. The source is an on-premises SQL Server. What should you check first?

- A. Increase the Fabric capacity size
- B. Check on-premises data gateway health and connectivity
- C. Switch from Dataflow Gen2 to a Data Factory pipeline
- D. Enable query folding on the Power Query steps

**Answer: B**

> On-premises sources require an on-premises data gateway. Gateway timeouts most commonly indicate the gateway machine is under load, has connectivity issues, or the gateway service needs restart.

### Q3: You are building a medallion architecture. The Silver layer should deduplicate rows and handle schema drift from the Bronze source. Which Fabric tool is best suited?

- A. Dataflow Gen2
- B. Spark notebook with Delta merge
- C. Data Factory Copy Activity
- D. Warehouse stored procedure

**Answer: B**

> Spark notebooks with Delta MERGE (upsert) handle deduplication and schema evolution natively. Delta Lake's schema evolution features (mergeSchema, overwriteSchema) address schema drift. Dataflow Gen2 is better for simpler transformations.

### Q4: A Data Factory pipeline needs to run daily at 06:00 Stockholm time (UTC+2 in summer). How do you configure the schedule?

- A. Set the trigger to run at 06:00 UTC+2 using the timezone offset
- B. Set the trigger to run at 04:00 UTC and document the offset
- C. Use a recurrence trigger with 04:00 UTC — Fabric schedules use UTC only
- D. Create a Logic App to trigger the pipeline at 06:00 local time

**Answer: C**

> Fabric pipeline schedules run in UTC. You must convert local time to UTC. Stockholm in CEST (summer) is UTC+2, so 06:00 local = 04:00 UTC.

### Q5: You use a Copy Activity to load data into a Lakehouse Delta table. The next day the table has duplicate rows. What is the most likely cause?

- A. Delta table auto-optimization caused row duplication
- B. The Copy Activity write mode was set to 'Append' instead of 'Upsert'
- C. The Lakehouse SQL endpoint cache was stale
- D. The pipeline ran in parallel with a Spark notebook

**Answer: B**

> Copy Activity defaults to Append for Delta tables. If the pipeline runs daily and appends the same records each time, duplicates accumulate. Use Upsert with a key column, or add a deduplication step.

### Q6: A KQL query against an Eventhouse returns data with a 5-minute lag behind the source Eventstream. What is the most likely explanation?

- A. The Eventstream batching interval is set to 5 minutes
- B. The Eventhouse ingestion queue is backed up
- C. KQL queries have a built-in 5-minute cache TTL
- D. The Event Hub consumer group is throttled

**Answer: A**

> Eventstream has configurable batching/micro-batch intervals. A 5-minute lag typically indicates the output to Eventhouse is batched at 5-minute intervals. Reduce the batch interval for lower latency.


## Monitor and optimize an analytics solution

### Q1: A Spark notebook in Fabric is running slowly. You suspect small file problems in a Delta table. What command should you run to fix this?

- A. VACUUM table_name
- B. OPTIMIZE table_name ZORDER BY (column)
- C. ALTER TABLE table_name SET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite'='true')
- D. ANALYZE TABLE table_name COMPUTE STATISTICS

**Answer: B**

> OPTIMIZE compacts small files into larger ones, improving read performance. ZORDER clusters data by a column for faster predicate pushdown. VACUUM removes old files but doesn't compact. AutoOptimize helps prevent the problem going forward.

### Q2: You need to monitor all scheduled Fabric pipeline and notebook jobs across a workspace and receive email alerts on failure. What is the correct approach?

- A. Set up Azure Monitor alerts on the Fabric capacity
- B. Enable failure notifications on each scheduled item in Fabric settings
- C. Query the Fabric Activity Log API via Power Automate
- D. Use the Fabric Admin Portal → Tenant Settings → Job monitoring

**Answer: B**

> Fabric supports per-item failure notifications (GA as of early 2026). Configure on each scheduled item (notebook, pipeline, semantic model refresh) under item settings → Schedule → Notify on failure.

### Q3: A semantic model refresh is taking 45 minutes. Historical refreshes took 10 minutes. No data volume change occurred. What should you investigate first?

- A. DirectQuery mode has been enabled on the model
- B. The source data query is no longer folding to the source — check Power Query steps
- C. The Fabric capacity is being throttled
- D. The model has too many relationships

**Answer: B**

> Query folding pushes transformation logic to the source database. If a new step breaks folding (e.g., a custom column, ToText), Power Query evaluates everything locally, dramatically increasing refresh time. Check the 'View native query' option in Power Query to confirm folding.

### Q4: You want to identify which DAX measures are causing slow report load times. What tool should you use?

- A. Fabric Monitoring Hub
- B. Performance Analyzer in Power BI Desktop
- C. DAX Studio with Server Timings
- D. Azure Log Analytics

**Answer: C**

> DAX Studio with Server Timings gives the most detailed breakdown: storage engine queries, formula engine time, cache hits. Performance Analyzer is useful for initial triage but DAX Studio gives actionable query-level detail.

### Q5: After enabling OPTIMIZE on a Delta table, you notice that historical time travel queries are failing. What is the likely cause and fix?

- A. OPTIMIZE deleted old versions — run RESTORE to recover
- B. VACUUM was run too aggressively, deleting files needed for time travel — increase retention period
- C. OPTIMIZE changes the table schema — revert with ALTER TABLE
- D. Time travel is not supported after OPTIMIZE

**Answer: B**

> VACUUM removes files older than the retention threshold (default 7 days). If VACUUM runs with a short retention (e.g., RETAIN 0 HOURS in testing), it deletes files needed for time travel. Fix: set delta.deletedFileRetentionDuration to at least your required time travel window before running VACUUM.

### Q6: A Fabric capacity is showing high CU (capacity unit) consumption during business hours, causing throttling. Which action will have the most immediate impact?

- A. Migrate all workloads to a higher SKU capacity
- B. Identify and reschedule non-urgent pipeline refreshes to off-peak hours
- C. Enable query caching on all semantic models
- D. Convert Dataflow Gen2 jobs to Spark notebooks

**Answer: B**

> Fabric smoothing spreads CU bursts over time, but peak contention during business hours is most effectively reduced by spreading scheduled workloads to off-peak. This is free and immediate. SKU upgrade is an escalation step, not a first response.

---

## Official Study Guide — Full Skills Breakdown (April 20, 2026 version)

*Sourced from learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/dp-700 — 2026-04-14*

**Score to pass: 700/1000**

All three sections are equally weighted at **30–35% each**.

### Implement and manage an analytics solution (30–35%)

**Configure Microsoft Fabric workspace settings**
- Configure Spark workspace settings
- Configure domain workspace settings
- Configure OneLake workspace settings
- Configure Dataflows Gen2 workspace settings

**Implement lifecycle management in Fabric**
- Configure version control
- Implement database projects
- Create and configure deployment pipelines

**Configure security and governance**
- Implement workspace-level access controls
- Implement item-level access controls
- Implement row-level, column-level, object-level, and folder/file-level access controls
- Implement dynamic data masking
- Apply sensitivity labels to items
- Endorse items
- Implement and use Microsoft Fabric audit logs
- Configure and implement OneLake security

**Orchestrate processes**
- Choose between Dataflow Gen2, a pipeline and a notebook
- Design and implement schedules and event-based triggers
- Implement orchestration patterns with notebooks and pipelines, including parameters and dynamic expressions

### Ingest and transform data (30–35%)

**Design and implement loading patterns**
- Design and implement full and incremental data loads
- Prepare data for loading into a dimensional model
- Design and implement a loading pattern for streaming data

**Ingest and transform batch data**
- Choose an appropriate data store
- Choose between Dataflows Gen2, notebooks, KQL, and T-SQL for data transformation
- Create and manage OneLake shortcuts
- Implement mirroring
- Ingest data by using pipelines
- Transform data by using PySpark, SQL, and KQL
- Denormalize data
- Group and aggregate data
- Handle duplicate, missing, and late-arriving data

**Ingest and transform streaming data**
- Choose an appropriate streaming engine
- Choose between native tables and OneLake shortcuts in Real-Time Intelligence
- Choose between Query acceleration for OneLake shortcuts and standard OneLake shortcuts in RTI
- Process data by using Eventstreams
- Process data by using Spark structured streaming
- Process data by using KQL
- Create windowing functions

### Monitor and optimize an analytics solution (30–35%)

**Monitor Fabric items**
- Monitor data ingestion
- Monitor data transformation
- Monitor semantic model refresh
- Configure alerts

**Identify and resolve errors**
- Identify and resolve pipeline errors
- Identify and resolve Dataflow Gen2 errors
- Identify and resolve notebook errors
- Identify and resolve Eventhouse errors
- Identify and resolve Eventstream errors
- Identify and resolve T-SQL errors
- Identify and resolve OneLake shortcut errors

**Optimize performance**
- Optimize a Lakehouse table
- Optimize a pipeline
- Optimize a data warehouse
- Optimize Eventstreams and Eventhouses
- Optimize Spark performance
- Optimize query performance

---

## Key gaps to study (based on 68% practice score + study guide review)

- **Mirroring** — what it is, when to use vs shortcuts vs copy
- **OneLake security** — folder/file-level access controls, how they differ from workspace/item-level
- **Audit logs** — what's logged, where to find them, how to query
- **Database projects** — what they are in Fabric context (SQL-based CI/CD for warehouse)
- **Spark structured streaming** — when to choose over Eventstream
- **Error identification** — each item type has specific error patterns (Eventhouse, Eventstream, T-SQL)
- **Dynamic expressions in pipelines** — `@` syntax, parameter passing between activities
- **Endorsement** — Promoted vs Certified, who can do each, effect on discoverability
