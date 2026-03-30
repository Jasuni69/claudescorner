"""Generate 4 Fabric notebook definition JSON files for v2 gold notebooks."""

import json
import base64
from pathlib import Path

OUTPUT_DIR = Path(r"E:\2026\ClaudesCorner\projects\clementine")

NOTEBOOK_META = {
    "kernelspec": {
        "name": "synapse_pyspark",
        "display_name": "Synapse PySpark"
    },
    "language_info": {
        "name": "python"
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def make_code_cell(source: str, tags: list[str] | None = None) -> dict:
    meta = {}
    if tags:
        meta["tags"] = tags
    return {
        "cell_type": "code",
        "metadata": meta,
        "outputs": [],
        "execution_count": None,
        "source": source.strip(),
    }


def make_notebook(cells: list[dict]) -> dict:
    nb = dict(NOTEBOOK_META)
    nb["cells"] = cells
    return nb


def write_def(filename: str, notebook: dict) -> None:
    ipynb_json = json.dumps(notebook, indent=1)
    payload = base64.b64encode(ipynb_json.encode("utf-8")).decode("ascii")
    definition = {
        "parts": [
            {
                "path": "notebook-content.py",
                "payload": payload,
                "payloadType": "InlineBase64",
            }
        ]
    }
    out = OUTPUT_DIR / filename
    out.write_text(json.dumps(definition, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({len(payload)} bytes payload)")


# ---------------------------------------------------------------------------
# Shared code snippets
# ---------------------------------------------------------------------------

SAFE_DROP = '''\
def safe_drop(delta_table_path: str, deep: bool = False, table_name: str = None, verbosity: int = 0):
    """Drop delta table files and optionally the Spark catalog entry."""
    try:
        mssparkutils.fs.rm(delta_table_path, recurse=True)
        if verbosity > 0:
            print(f"Deleted files at {delta_table_path}")
    except Exception as e:
        if verbosity > 0:
            print(f"rm failed on {delta_table_path}: {e}")
    if deep and table_name:
        try:
            spark.sql(f"DROP TABLE IF EXISTS {table_name}")
            if verbosity > 0:
                print(f"Dropped catalog entry {table_name}")
        except Exception as e:
            if verbosity > 0:
                print(f"DROP TABLE failed for {table_name}: {e}")
'''

WRITE_DELTA_V2 = '''\
def write_delta_table_to_lakehouse(table_name: str, lakehouse_name: str, data_frame: DataFrame, drop_before_write: bool = False, force: bool = False, verbosity: int = 0):
    import sempy.fabric as fabric
    workspace_id = fabric.get_notebook_workspace_id()
    lakehouse_object = mssparkutils.lakehouse.get(lakehouse_name, workspace_id)
    delta_table_path = lakehouse_object['properties']['abfsPath'] + "/Tables/" + table_name

    if drop_before_write:
        if verbosity > 0:
            print(f"safe dropping table {delta_table_path}")
        full_table_name = f"`{lakehouse_name}`.`{table_name.replace('/', '.')}`"
        safe_drop(delta_table_path, True, table_name=full_table_name, verbosity=verbosity)

    if verbosity > 0:
        print(f"Schema BEFORE write ({table_name}):")
        data_frame.printSchema()

    try:
        if verbosity > 0:
            print(f"Trying to overwrite {table_name}")
        writer = data_frame.write.format("delta")
        if not drop_before_write:
            writer = writer.option("mergeSchema", "true")
        writer.mode("overwrite").save(delta_table_path)
    except Exception as e:
        print(f"Overwrite failed on {table_name} with message {str(e)}")
        if force and "DELTA_FAILED_TO_MERGE_FIELDS" in str(e):
            print(f"Attempting safe_drop on {table_name}")
            safe_drop(delta_table_path, True, verbosity=verbosity)
            print(f"Safe drop - trying to write {table_name}")
            data_frame.write.format("delta").mode("overwrite").save(delta_table_path)
        else:
            raise

    if verbosity > 0:
        print(f"Schema AFTER write ({table_name}):")
        spark.read.format("delta").load(delta_table_path).printSchema()
'''


# ---------------------------------------------------------------------------
# 1. Gold_Parameter_v2
# ---------------------------------------------------------------------------
def build_gold_param_v2():
    cells = [
        make_code_cell("%run Common_Functions"),
        make_code_cell("%run Common_Variables"),
        make_code_cell(
            '''\
silver_delta_table = ""
gold_delta_table = ""
drop_before_write = False
force = False
add_audit_columns = True
verbosity = 0
''',
            tags=["parameters"],
        ),
        make_code_cell(
            '''\
print(f"silver_delta_table = {silver_delta_table}")
print(f"gold_delta_table = {gold_delta_table}")
print(f"drop_before_write = {drop_before_write}")
print(f"force = {force}")
print(f"add_audit_columns = {add_audit_columns}")
print(f"verbosity = {verbosity}")
'''
        ),
        make_code_cell(SAFE_DROP + "\n\n" + WRITE_DELTA_V2),
        make_code_cell(
            '''\
from pyspark.sql.functions import col

silver_df = spark.read.format("delta").table(f"`{silver_lakehouse_name}`.`{silver_delta_table}`")

# Drop Silver-prefixed columns
cols_to_drop = [c for c in silver_df.columns if c.startswith("Silver")]
if cols_to_drop:
    silver_df = silver_df.drop(*cols_to_drop)

if add_audit_columns:
    silver_df = add_audit_cols(silver_df)

write_delta_table_to_lakehouse(
    table_name=gold_delta_table,
    lakehouse_name=gold_lakehouse_name,
    data_frame=silver_df,
    drop_before_write=drop_before_write,
    force=force,
    verbosity=verbosity,
)

if verbosity > 0:
    print(f"Done: {silver_delta_table} -> {gold_delta_table}")
'''
        ),
    ]
    nb = make_notebook(cells)
    write_def("gold_param_v2_def.json", nb)


# ---------------------------------------------------------------------------
# 2. Gold_Functions_v2
# ---------------------------------------------------------------------------
def build_gold_functions_v2():
    cells = [
        make_code_cell("%run Common_Variables"),
        make_code_cell("%run Silver_Functions"),
        make_code_cell(
            '''\
def create_dag_config(table_mappings, retry_count=5, retry_interval=10, timeout_seconds=360, concurrency_count=16, drop_before_write: bool = False, force: bool = False, verbosity: int = 0, add_audit_columns: bool = True):
    activities = []
    seen_names = set()
    for mapping in table_mappings:
        base_name = mapping.get("name", mapping["silver_table"])
        activity_name = base_name
        if activity_name in seen_names:
            activity_name = f"{base_name}__{mapping['gold_table']}"
            suffix = 2
            while activity_name in seen_names:
                activity_name = f"{base_name}__{mapping['gold_table']}__{suffix}"
                suffix += 1
        seen_names.add(activity_name)
        activity = {
            "name": activity_name,
            "path": "Gold_Parameter_v2",
            "timeoutPerCellInSeconds": timeout_seconds,
            "retry": retry_count,
            "retryIntervalInSeconds": retry_interval,
            "args": {
                "silver_delta_table": mapping["silver_table"],
                "gold_delta_table": mapping["gold_table"],
                "drop_before_write": drop_before_write,
                "add_audit_columns": add_audit_columns,
                "force": force,
                "verbosity": verbosity,
            },
            "dependencies": [],
        }
        activities.append(activity)
    dag = {
        "activities": activities,
        "timeoutInSeconds": 3600,
        "concurrency": concurrency_count,
    }
    return dag
'''
        ),
    ]
    nb = make_notebook(cells)
    write_def("gold_functions_v2_def.json", nb)


# ---------------------------------------------------------------------------
# 3. Gold_ExecutionBook_v2
# ---------------------------------------------------------------------------
def build_gold_executionbook_v2():
    cells = [
        make_code_cell("%run Gold_Functions_v2"),
        make_code_cell(SAFE_DROP + "\n\n" + WRITE_DELTA_V2),
        make_code_cell(
            '''\
drop_before_write = False
force = False
add_audit_columns = True
verbosity = 0
''',
            tags=["parameters"],
        ),
        make_code_cell(
            '''\
tables = [
    {"silver_table": "Account", "gold_table": "dAccount"},
    {"silver_table": "AccountCostCenterGroup", "gold_table": "dAccountCostCenterGroup"},
    {"silver_table": "Article", "gold_table": "dArticle"},
    {"silver_table": "CostCenter", "gold_table": "dCostCenter"},
    {"silver_table": "CostCenterGroup", "gold_table": "dCostCenterGroup"},
    {"silver_table": "CounterPart", "gold_table": "dCounterPart"},
    {"silver_table": "CounterPartGroup", "gold_table": "dCounterPartGroup"},
    {"silver_table": "ProjectGroup", "gold_table": "dProjectGroup"},
    {"silver_table": "InvoiceDate", "gold_table": "fInvoiceDate"},
    {"silver_table": "CustomerLedger", "gold_table": "fCustomerLedger"},
    {"silver_table": "Date", "gold_table": "_Date"},
    {"silver_table": "Forecast", "gold_table": "fForecast"},
    {"silver_table": "ForecastVersion", "gold_table": "dForecastVersion"},
    {"silver_table": "GeneralLedgerTransaction", "gold_table": "fGeneralLedgerTransaction"},
    {"silver_table": "Invoice", "gold_table": "dInvoice"},
    {"silver_table": "InvoicePayment", "gold_table": "fInvoicePayment"},
    {"silver_table": "InvoiceRow", "gold_table": "dInvoiceRow"},
    {"silver_table": "LastUpdated", "gold_table": "_LastUpdated"},
    {"silver_table": "LegalEntity", "gold_table": "dLegalEntity"},
    {"silver_table": "Project", "gold_table": "dProject"},
    {"silver_table": "Report", "gold_table": "dReport"},
    {"silver_table": "ReportMapping", "gold_table": "dReportMapping"},
    {"silver_table": "Voucher", "gold_table": "dVoucher"},
    {"silver_table": "DynamicColumns", "gold_table": "DynamicColumns"},
    {"silver_table": "DynamicColumnsDetailed", "gold_table": "DynamicColumnsDetailed"},
    {"silver_table": "DynamicMeasures", "gold_table": "DynamicMeasures"},
    {"silver_table": "DynamicMonth", "gold_table": "DynamicMonth"},
]

dag_config = create_dag_config(tables, retry_count=0, drop_before_write=drop_before_write, force=True, verbosity=verbosity, add_audit_columns=add_audit_columns)
'''
        ),
        make_code_cell(
            'mssparkutils.notebook.runMultiple(dag_config, {"displayDAGViaGraphviz": False})'
        ),
        make_code_cell("refresh_sql_endpoint(gold_lakehouse_name)"),
    ]
    nb = make_notebook(cells)
    write_def("gold_executionbook_v2_def.json", nb)


# ---------------------------------------------------------------------------
# 4. Silver_Gold_ExecutionBook_v2
# ---------------------------------------------------------------------------
def build_silver_gold_executionbook_v2():
    cells = [
        make_code_cell(
            '''\
retry_count = 0
drop_before_write = False
''',
            tags=["parameters"],
        ),
        make_code_cell(
            '''\
DAG = {
    "activities": [
        {
            "name": "Silver",
            "path": "Silver_ExecutionBook",
            "timeoutPerCellInSeconds": 360,
            "retry": retry_count,
            "retryIntervalInSeconds": 10,
            "args": {"drop_before_write": drop_before_write},
        },
        {
            "name": "Gold",
            "path": "Gold_ExecutionBook_v2",
            "timeoutPerCellInSeconds": 360,
            "retry": retry_count,
            "retryIntervalInSeconds": 10,
            "args": {"drop_before_write": drop_before_write},
            "dependencies": ["Silver"],
        },
    ],
    "timeoutInSeconds": 3600,
    "concurrency": 16,
}

mssparkutils.notebook.runMultiple(DAG, {"displayDAGViaGraphviz": True})
'''
        ),
    ]
    nb = make_notebook(cells)
    write_def("silver_gold_executionbook_v2_def.json", nb)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_gold_param_v2()
    build_gold_functions_v2()
    build_gold_executionbook_v2()
    build_silver_gold_executionbook_v2()
    print("\nAll 4 definition files generated.")
