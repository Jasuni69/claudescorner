# Pipelines

## Q1 — Custom error message on pipeline failure

**Scenario:** Pipeline failed due to script activity error. Need custom error message and code on failure.

**Question:** Which two actions should you perform?

| Action | Correct |
|--------|---------|
| Add a Fail activity | ✅ |
| Configure custom error settings in the Fail activity | ✅ |
| Enable logging for pipeline activities | ❌ |
| Use a Try-Catch activity | ❌ |

**Why:**
- **Fail activity** → designed specifically to surface custom error messages and codes
- **Configure Fail activity settings** → sets the desired message/code

**Why not:**
- Try-Catch is not applicable in Fabric pipelines
- Logging doesn't address error reporting/customization

---

## Q2 — ETL process for dimensional model from ADLS Gen2 and SQL Server

**Scenario:** Data warehouse integrating ADLS Gen2 + SQL Server. Need efficient ETL into dimensional model tables for reporting.

**Question:** Which three actions?

| Action | Correct |
|--------|---------|
| Load data directly without staging | ❌ |
| Proceed without verifying data quality | ❌ |
| Stage data before loading | ✅ |
| Transform data to match the model | ✅ |
| Use a basic ETL tool without automation | ❌ |
| Use Data Factory pipelines | ✅ |

**Why:**
- **Stage data first** → decouples source systems, enables quality checks
- **Transform to match model** → ensures cleansed, conformed data for accurate reporting
- **Data Factory pipelines** → orchestrates complex workflows, automation built-in

**Why not:**
- Direct load → data quality issues
- No quality verification → inaccurate reports
- Basic ETL tool → lacks automation, inefficient at scale

---
