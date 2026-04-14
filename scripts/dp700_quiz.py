#!/usr/bin/env python3
"""
dp700_quiz.py — DP-700 practice quiz generator.
Outputs a study guide to memory/dp700-study.md.
Run: python dp700_quiz.py
Run interactively: python dp700_quiz.py --interactive
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

BASE = Path(__file__).parent.parent
OUT = BASE / "memory" / "dp700-study.md"

QUESTIONS: list[dict] = [
    # ── Implement and manage an analytics solution ────────────────────────────
    {
        "topic": "Implement and manage an analytics solution",
        "q": "You need to store structured data that will be queried via T-SQL by BI tools. The data is updated frequently via MERGE operations. What should you use?",
        "options": ["A. Lakehouse", "B. Warehouse", "C. KQL Database", "D. Eventhouse"],
        "answer": "B",
        "explanation": "Fabric Warehouse is optimized for T-SQL, supports DML (MERGE/UPDATE/DELETE), and is the right choice for BI workloads with frequent updates. Lakehouse is Delta-based and accessed via Spark or SQL endpoint (read-optimized).",
    },
    {
        "topic": "Implement and manage an analytics solution",
        "q": "You are setting up CI/CD for a Fabric workspace. Which tool is the recommended Microsoft-native approach for deploying Fabric items from source control?",
        "options": ["A. Azure DevOps Pipelines with ARM templates", "B. fabric-cicd Python library", "C. Fabric Deployment Pipelines (UI-based)", "D. GitHub Actions with Power BI REST API"],
        "answer": "C",
        "explanation": "Fabric Deployment Pipelines is the native UI-based tool for promoting content across Dev/Test/Prod stages. fabric-cicd is the code-based library for Git-integrated deployments. Both are valid, but Deployment Pipelines is the 'recommended Microsoft-native' approach in exam context.",
    },
    {
        "topic": "Implement and manage an analytics solution",
        "q": "A Fabric workspace needs to be connected to a Git repo. A developer commits changes but they are not reflected in the workspace. What is the most likely cause?",
        "options": [
            "A. The workspace is not assigned to a Fabric capacity",
            "B. Git integration was not initialized — workspace was connected but never synced from Git",
            "C. The developer lacks Contributor role on the workspace",
            "D. The branch is not 'main'",
        ],
        "answer": "B",
        "explanation": "After connecting a workspace to Git, you must explicitly run 'Update workspace from Git' or 'Commit to Git' to sync. Connection alone does not sync content.",
    },
    {
        "topic": "Implement and manage an analytics solution",
        "q": "You need to implement row-level security on a semantic model so that each salesperson only sees their own region's data. Where do you define the RLS rules?",
        "options": [
            "A. In the Lakehouse SQL endpoint using GRANT/DENY",
            "B. In the semantic model via DAX roles and filters",
            "C. In the Fabric workspace access settings",
            "D. In the Power BI report filter pane",
        ],
        "answer": "B",
        "explanation": "RLS on semantic models is defined as DAX roles with table filters (e.g., [Region] = USERPRINCIPALNAME()). This is enforced at query time regardless of what report is used.",
    },
    {
        "topic": "Implement and manage an analytics solution",
        "q": "Which Fabric item type provides a SQL analytics endpoint that is automatically generated and updated when new Delta tables are created in a Lakehouse?",
        "options": ["A. Warehouse", "B. SQL Database", "C. Lakehouse SQL endpoint", "D. Eventhouse"],
        "answer": "C",
        "explanation": "Every Lakehouse automatically gets a SQL analytics endpoint — a read-only T-SQL interface over the Delta tables. It updates automatically as tables are created/updated via Spark.",
    },
    {
        "topic": "Implement and manage an analytics solution",
        "q": "You need to allow an external partner to read data from a specific Fabric Lakehouse without giving them workspace access. What is the correct approach?",
        "options": [
            "A. Share the workspace with the partner as a Viewer",
            "B. Use OneLake shortcuts to expose data to their tenant",
            "C. Grant item-level permissions directly on the Lakehouse",
            "D. Export the data to Azure Blob and share the SAS URL",
        ],
        "answer": "C",
        "explanation": "Fabric supports item-level sharing — you can share a specific Lakehouse or semantic model without granting workspace access. This is the least-privilege approach.",
    },

    # ── Ingest and transform data ─────────────────────────────────────────────
    {
        "topic": "Ingest and transform data",
        "q": "You want to ingest streaming IoT sensor data into Fabric with sub-second latency and query it with KQL. What is the correct architecture?",
        "options": [
            "A. Event Hub → Data Factory pipeline → Lakehouse → KQL Database",
            "B. Event Hub → Eventstream → Eventhouse (KQL Database)",
            "C. Event Hub → Spark Structured Streaming → Delta Lake",
            "D. IoT Hub → Dataflow Gen2 → Warehouse",
        ],
        "answer": "B",
        "explanation": "Eventstream is the real-time data ingestion component in Fabric. It connects to Event Hub/IoT Hub and routes data directly into an Eventhouse (KQL Database) for low-latency analytics.",
    },
    {
        "topic": "Ingest and transform data",
        "q": "A Dataflow Gen2 refresh is failing intermittently with gateway timeout errors. The source is an on-premises SQL Server. What should you check first?",
        "options": [
            "A. Increase the Fabric capacity size",
            "B. Check on-premises data gateway health and connectivity",
            "C. Switch from Dataflow Gen2 to a Data Factory pipeline",
            "D. Enable query folding on the Power Query steps",
        ],
        "answer": "B",
        "explanation": "On-premises sources require an on-premises data gateway. Gateway timeouts most commonly indicate the gateway machine is under load, has connectivity issues, or the gateway service needs restart.",
    },
    {
        "topic": "Ingest and transform data",
        "q": "You are building a medallion architecture. The Silver layer should deduplicate rows and handle schema drift from the Bronze source. Which Fabric tool is best suited?",
        "options": [
            "A. Dataflow Gen2",
            "B. Spark notebook with Delta merge",
            "C. Data Factory Copy Activity",
            "D. Warehouse stored procedure",
        ],
        "answer": "B",
        "explanation": "Spark notebooks with Delta MERGE (upsert) handle deduplication and schema evolution natively. Delta Lake's schema evolution features (mergeSchema, overwriteSchema) address schema drift. Dataflow Gen2 is better for simpler transformations.",
    },
    {
        "topic": "Ingest and transform data",
        "q": "A Data Factory pipeline needs to run daily at 06:00 Stockholm time (UTC+2 in summer). How do you configure the schedule?",
        "options": [
            "A. Set the trigger to run at 06:00 UTC+2 using the timezone offset",
            "B. Set the trigger to run at 04:00 UTC and document the offset",
            "C. Use a recurrence trigger with 04:00 UTC — Fabric schedules use UTC only",
            "D. Create a Logic App to trigger the pipeline at 06:00 local time",
        ],
        "answer": "C",
        "explanation": "Fabric pipeline schedules run in UTC. You must convert local time to UTC. Stockholm in CEST (summer) is UTC+2, so 06:00 local = 04:00 UTC.",
    },
    {
        "topic": "Ingest and transform data",
        "q": "You use a Copy Activity to load data into a Lakehouse Delta table. The next day the table has duplicate rows. What is the most likely cause?",
        "options": [
            "A. Delta table auto-optimization caused row duplication",
            "B. The Copy Activity write mode was set to 'Append' instead of 'Upsert'",
            "C. The Lakehouse SQL endpoint cache was stale",
            "D. The pipeline ran in parallel with a Spark notebook",
        ],
        "answer": "B",
        "explanation": "Copy Activity defaults to Append for Delta tables. If the pipeline runs daily and appends the same records each time, duplicates accumulate. Use Upsert with a key column, or add a deduplication step.",
    },
    {
        "topic": "Ingest and transform data",
        "q": "A KQL query against an Eventhouse returns data with a 5-minute lag behind the source Eventstream. What is the most likely explanation?",
        "options": [
            "A. The Eventstream batching interval is set to 5 minutes",
            "B. The Eventhouse ingestion queue is backed up",
            "C. KQL queries have a built-in 5-minute cache TTL",
            "D. The Event Hub consumer group is throttled",
        ],
        "answer": "A",
        "explanation": "Eventstream has configurable batching/micro-batch intervals. A 5-minute lag typically indicates the output to Eventhouse is batched at 5-minute intervals. Reduce the batch interval for lower latency.",
    },

    # ── Monitor and optimize an analytics solution ────────────────────────────
    {
        "topic": "Monitor and optimize an analytics solution",
        "q": "A Spark notebook in Fabric is running slowly. You suspect small file problems in a Delta table. What command should you run to fix this?",
        "options": [
            "A. VACUUM table_name",
            "B. OPTIMIZE table_name ZORDER BY (column)",
            "C. ALTER TABLE table_name SET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite'='true')",
            "D. ANALYZE TABLE table_name COMPUTE STATISTICS",
        ],
        "answer": "B",
        "explanation": "OPTIMIZE compacts small files into larger ones, improving read performance. ZORDER clusters data by a column for faster predicate pushdown. VACUUM removes old files but doesn't compact. AutoOptimize helps prevent the problem going forward.",
    },
    {
        "topic": "Monitor and optimize an analytics solution",
        "q": "You need to monitor all scheduled Fabric pipeline and notebook jobs across a workspace and receive email alerts on failure. What is the correct approach?",
        "options": [
            "A. Set up Azure Monitor alerts on the Fabric capacity",
            "B. Enable failure notifications on each scheduled item in Fabric settings",
            "C. Query the Fabric Activity Log API via Power Automate",
            "D. Use the Fabric Admin Portal → Tenant Settings → Job monitoring",
        ],
        "answer": "B",
        "explanation": "Fabric supports per-item failure notifications (GA as of early 2026). Configure on each scheduled item (notebook, pipeline, semantic model refresh) under item settings → Schedule → Notify on failure.",
    },
    {
        "topic": "Monitor and optimize an analytics solution",
        "q": "A semantic model refresh is taking 45 minutes. Historical refreshes took 10 minutes. No data volume change occurred. What should you investigate first?",
        "options": [
            "A. DirectQuery mode has been enabled on the model",
            "B. The source data query is no longer folding to the source — check Power Query steps",
            "C. The Fabric capacity is being throttled",
            "D. The model has too many relationships",
        ],
        "answer": "B",
        "explanation": "Query folding pushes transformation logic to the source database. If a new step breaks folding (e.g., a custom column, ToText), Power Query evaluates everything locally, dramatically increasing refresh time. Check the 'View native query' option in Power Query to confirm folding.",
    },
    {
        "topic": "Monitor and optimize an analytics solution",
        "q": "You want to identify which DAX measures are causing slow report load times. What tool should you use?",
        "options": [
            "A. Fabric Monitoring Hub",
            "B. Performance Analyzer in Power BI Desktop",
            "C. DAX Studio with Server Timings",
            "D. Azure Log Analytics",
        ],
        "answer": "C",
        "explanation": "DAX Studio with Server Timings gives the most detailed breakdown: storage engine queries, formula engine time, cache hits. Performance Analyzer is useful for initial triage but DAX Studio gives actionable query-level detail.",
    },
    {
        "topic": "Monitor and optimize an analytics solution",
        "q": "After enabling OPTIMIZE on a Delta table, you notice that historical time travel queries are failing. What is the likely cause and fix?",
        "options": [
            "A. OPTIMIZE deleted old versions — run RESTORE to recover",
            "B. VACUUM was run too aggressively, deleting files needed for time travel — increase retention period",
            "C. OPTIMIZE changes the table schema — revert with ALTER TABLE",
            "D. Time travel is not supported after OPTIMIZE",
        ],
        "answer": "B",
        "explanation": "VACUUM removes files older than the retention threshold (default 7 days). If VACUUM runs with a short retention (e.g., RETAIN 0 HOURS in testing), it deletes files needed for time travel. Fix: set delta.deletedFileRetentionDuration to at least your required time travel window before running VACUUM.",
    },
    {
        "topic": "Monitor and optimize an analytics solution",
        "q": "A Fabric capacity is showing high CU (capacity unit) consumption during business hours, causing throttling. Which action will have the most immediate impact?",
        "options": [
            "A. Migrate all workloads to a higher SKU capacity",
            "B. Identify and reschedule non-urgent pipeline refreshes to off-peak hours",
            "C. Enable query caching on all semantic models",
            "D. Convert Dataflow Gen2 jobs to Spark notebooks",
        ],
        "answer": "B",
        "explanation": "Fabric smoothing spreads CU bursts over time, but peak contention during business hours is most effectively reduced by spreading scheduled workloads to off-peak. This is free and immediate. SKU upgrade is an escalation step, not a first response.",
    },
]


def write_study_guide() -> None:
    by_topic: dict[str, list[dict]] = {}
    for q in QUESTIONS:
        by_topic.setdefault(q["topic"], []).append(q)

    lines = ["# DP-700 Study Guide — Practice Questions\n",
             f"Generated: {Path(OUT).name} | {len(QUESTIONS)} questions across {len(by_topic)} topics\n",
             "> Target: 80%+ on practice assessment\n"]

    for topic, qs in by_topic.items():
        lines.append(f"\n## {topic}\n")
        for i, q in enumerate(qs, 1):
            lines.append(f"### Q{i}: {q['q']}\n")
            for opt in q["options"]:
                lines.append(f"- {opt}")
            lines.append(f"\n**Answer: {q['answer']}**\n")
            lines.append(f"> {q['explanation']}\n")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[dp700_quiz] written {len(QUESTIONS)} questions to {OUT}")


def interactive_quiz() -> None:
    qs = random.sample(QUESTIONS, len(QUESTIONS))
    score = 0
    for i, q in enumerate(qs, 1):
        print(f"\n[{i}/{len(qs)}] ({q['topic']})")
        print(f"Q: {q['q']}\n")
        for opt in q["options"]:
            print(f"  {opt}")
        answer = input("\nYour answer (A/B/C/D): ").strip().upper()
        if answer == q["answer"]:
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Wrong. Answer: {q['answer']}")
        print(f"  {q['explanation']}")
    pct = round(score / len(qs) * 100)
    print(f"\nResult: {score}/{len(qs)} = {pct}%")
    if pct >= 80:
        print("Ready for the exam!")
    else:
        print("Keep studying — target is 80%+")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", action="store_true", help="Run as interactive quiz")
    args = parser.parse_args()
    if args.interactive:
        interactive_quiz()
    else:
        write_study_guide()


if __name__ == "__main__":
    main()
