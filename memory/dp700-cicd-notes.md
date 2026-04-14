# DP-700 Cheat Sheet: CI/CD in Microsoft Fabric

Sourced from official Microsoft Learn docs, 2026-04-14.

---

## Two separate CI/CD tools — know the difference

| | **Git Integration** | **Deployment Pipelines** |
|---|---|---|
| **Purpose** | Version control (source of truth) | Environment promotion (Dev→Test→Prod) |
| **Direction** | Workspace ↔ Git repo | Stage → Stage (copy content) |
| **Analogy** | Git commit/push/pull | CD pipeline / release pipeline |
| **Admin setup** | Only workspace admin can connect/disconnect | Pipeline creator assigns workspaces to stages |
| **Automation** | Commit/update via REST API or fabric-cicd | Deploy via Deployment Pipelines REST API |

---

## Git Integration — key facts for the exam

### How to connect
1. Workspace admin goes to Workspace Settings → Git integration
2. Select provider: **Azure DevOps** (cloud only) or **GitHub** / **GitHub Enterprise** (cloud only)
3. Choose repo, branch, and subfolder (optional)
4. Click **Connect and Sync** — this initializes the connection
5. First sync: choose "Update workspace" (pull from Git) or "Commit to workspace" (push to Git)

### Permissions
- **Only workspace Admin** can connect, disconnect, or change the branch
- Contributors and above can commit/update items

### What's supported (exam-relevant items)
- Lakehouse, Notebooks, Spark Job Definitions, Environment
- Dataflow Gen2, Pipelines, Mirrored Database
- Eventhouse, Eventstream, KQL Database, KQL Queryset
- Semantic models, Reports (Power BI items — **preview**)
- Warehouse (**preview**)
- **NOT supported:** MyWorkspace, workspaces with template apps, push datasets, live connections to Analysis Services

### Key behaviors
- **Unsupported items are ignored** — not synced, not deleted
- Items are stored as folders in Git repo; workspace folder structure preserved up to 10 levels
- Can only sync **one direction at a time** — can't commit and update simultaneously
- Sensitivity labels block sync by default (admin must enable export)
- Submodules not supported
- Max 1,000 items per workspace

### Branching out (branch-per-feature)
- Creates a new workspace from a Git branch
- New workspace requires available capacity
- Settings from original branch are **NOT copied** — must reconfigure
- Uncommitted items in source workspace can be lost — **commit before branching out**

### Limitations to remember
- Azure DevOps: commit limit 25 MB (Service Principal) / 125 MB (SSO)
- GitHub: total commit size limit 50 MB
- Can't export if cross-geo exports disabled by tenant admin
- Conflict resolution is partially done in Git

---

## Deployment Pipelines — key facts for the exam

### Structure
- 2 to 10 stages (default: Development → Test → Production)
- Each stage is mapped to a **Fabric workspace**
- Content is **copied** (cloned) from source stage to target stage

### Item pairing
- Pairing links the same item across adjacent stages
- Items pair automatically on first clean deploy or when workspace is assigned
- Items added to a workspace **after** assignment are **not automatically paired**
- Paired items remain paired even if renamed
- Unpaired items with same name/type **do NOT overwrite** — they create a duplicate

### Deployment rules
- Rules let you configure stage-specific settings (e.g., different data source for Prod)
- Example: Lakehouse in Dev points to dev data, rule overrides connection string in Prod

### Permissions
- Need to be a **pipeline admin** or have deploy permissions on the pipeline
- Also need appropriate workspace permissions on both source and target stages

### Automation
- Deploy programmatically via **Deployment Pipelines REST API**
- Or use **fabric-cicd** Python library for Git-based automation

### Key limitation: item pairing gotcha
> If you add an item AFTER assigning a workspace to a pipeline, it won't be paired. You must manually pair it or do a clean deploy. This is a common exam trap.

---

## fabric-cicd library (automation)

- Microsoft-official Python library for deploying Fabric items from source control
- Used in Azure DevOps Pipelines / GitHub Actions for automated CI/CD
- Reads item definitions from Git, deploys to target workspace via Fabric REST API
- Key for: automated promotion, integration with external CI systems

---

## Common exam scenarios

**Q: You need to promote a notebook from Dev to Prod automatically when code is merged to main.**
→ Git Integration (connect workspace to Git branch) + GitHub Actions/Azure DevOps pipeline using fabric-cicd

**Q: A developer added a new report after assigning the workspace to a pipeline. The report doesn't appear in the Test stage after deployment.**
→ New items added after workspace assignment aren't automatically paired. Must manually pair or redeploy.

**Q: You want different data sources in Dev vs Prod without changing notebook code.**
→ Deployment rules — configure stage-specific parameter overrides in the pipeline.

**Q: A workspace admin leaves the company. Git integration stops working.**
→ Another workspace admin must reconnect Git (only admins can manage the Git connection).

**Q: You want to ensure no one can commit directly to the production Git branch.**
→ Configure branch policies in Azure DevOps / GitHub to require PRs + approvals on the production branch. Fabric respects standard Git provider protections.

**Q: Sensitivity labels are applied to items in a workspace. Committing to Git fails.**
→ Tenant admin must enable "Users can export workspace items with applied sensitivity labels to Git repositories" in admin settings.

---

## Quick memory aids

- **Git integration = version control** (who changed what, rollback, collaboration)
- **Deployment pipelines = environment promotion** (Dev→Test→Prod copy)
- **Both can be automated** — Git via fabric-cicd, Pipelines via REST API
- **Pairing is everything** in deployment pipelines — if items aren't paired, you get duplicates, not overwrites
- **Only admin can connect Git** — not Contributor, not Member
- **Branch out = new workspace** per feature branch, but settings don't copy
