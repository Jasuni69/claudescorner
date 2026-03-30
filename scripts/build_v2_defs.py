"""Build v2 notebook definitions for Fabric import."""
import json, base64

OUT = "E:/2026/ClaudesCorner/projects/clementine"

def make_def(nb_dict):
    payload = base64.b64encode(json.dumps(nb_dict).encode()).decode()
    return {"parts": [{"path": "notebook-content.py", "payload": payload, "payloadType": "InlineBase64"}]}

META = {
    "language_info": {"name": "python"},
    "kernel_info": {"name": "synapse_pyspark"},
    "a365ComputeOptions": None,
    "sessionKeepAliveTimeout": 0,
    "dependencies": {"lakehouse": None},
}

def cell(src, tags=None):
    m = {"microsoft": {"language": "python", "language_group": "synapse_pyspark"}}
    if tags:
        m["tags"] = tags
    return {"cell_type": "code", "metadata": m, "source": src if isinstance(src, list) else [src], "outputs": []}

# ── Gold_Parameter_v2 ──
gold_param = {
    "nbformat": 4, "nbformat_minor": 5, "metadata": META,
    "cells": [
        cell("%run Common_Functions"),  # was HTTP download
        cell("%run Common_Variables"),
        cell(
            'silver_delta_table = "Article"\n'
            'gold_delta_table = "dArticle"\n'
            'force = False\n'
            'add_audit_columns=False\n'
            'drop_before_write=False\n'
            'verbosity=0',
            tags=["parameters"],
        ),
        cell(
            'print(f"silver_delta_table: {silver_delta_table}")\n'
            'print(f"gold_delta_table: {gold_delta_table}")\n'
            'print(f"force: {force}")\n'
            'print(f"drop_before_write: {drop_before_write}")'
        ),
        cell(
            'def safe_drop(delta_table_path: str, recursive: bool, table_name: str = None, verbosity: int = 0):\n'
            '    if path_exists(delta_table_path):\n'
            '        mssparkutils.fs.rm(delta_table_path, recursive)\n'
            '        if verbosity > 0:\n'
            '            print(f"  [safe_drop] Removed files at {delta_table_path}")\n'
            '        if table_name:\n'
            '            try:\n'
            '                spark.sql(f"DROP TABLE IF EXISTS {table_name}")\n'
            '                if verbosity > 0:\n'
            '                    print(f"  [safe_drop] Dropped metastore entry via SQL for {table_name}")\n'
            '            except Exception as e:\n'
            '                if verbosity > 0:\n'
            '                    print(f"  [safe_drop] SQL drop failed for {table_name}: {e}")\n'
            '                try:\n'
            '                    spark.catalog.dropTable(table_name)\n'
            '                    if verbosity > 0:\n'
            '                        print(f"  [safe_drop] Dropped metastore entry via catalog API for {table_name}")\n'
            '                except Exception as e2:\n'
            '                    print(f"  [safe_drop] Warning: Both metastore drop attempts failed for {table_name}: {e2}")\n'
            '        if path_exists(delta_table_path):\n'
            '            raise RuntimeError(f"  [safe_drop] FAILED: Path still exists after drop: {delta_table_path}")\n'
            '        elif verbosity > 0:\n'
            '            print(f"  [safe_drop] Verified: path no longer exists.")\n'
            '    else:\n'
            '        if verbosity > 0:\n'
            '            print(f"  [safe_drop] Path did not exist, nothing to drop: {delta_table_path}")\n'
            '\n\n'
            'def write_delta_table_to_lakehouse(table_name: str, lakehouse_name: str, data_frame, drop_before_write: bool = False, force: bool = False, verbosity: int = 0):\n'
            '    import sempy.fabric as fabric\n'
            '    workspace_id = fabric.get_notebook_workspace_id()\n'
            '    lakehouse_object = mssparkutils.lakehouse.get(lakehouse_name, workspace_id)\n'
            '    delta_table_path = lakehouse_object[\'properties\'][\'abfsPath\'] + "/Tables/" + table_name\n'
            '    if drop_before_write:\n'
            '        if verbosity > 0:\n'
            '            print(f"safe dropping table {delta_table_path}")\n'
            '        full_table_name = f"`{lakehouse_name}`.`{table_name.replace(chr(47), chr(46))}`"\n'
            '        safe_drop(delta_table_path, True, table_name=full_table_name, verbosity=verbosity)\n'
            '    if verbosity > 0:\n'
            '        print(f"Schema BEFORE write ({table_name}):")\n'
            '        data_frame.printSchema()\n'
            '    try:\n'
            '        if verbosity > 0:\n'
            '            print(f"Trying to overwrite {table_name}")\n'
            '        writer = data_frame.write.format("delta").mode("overwrite")\n'
            '        if not drop_before_write:\n'
            '            writer = writer.option("mergeSchema", "true")\n'
            '        writer.save(delta_table_path)\n'
            '    except Exception as e:\n'
            '        print(f"Overwrite failed on {table_name} with message {str(e)}")\n'
            '        if force and "DELTA_FAILED_TO_MERGE_FIELDS" in str(e):\n'
            '            print(f"Attempting safe_drop on {table_name}")\n'
            '            safe_drop(delta_table_path, True, verbosity=verbosity)\n'
            '            print(f"Safe drop - trying to write {table_name}")\n'
            '            data_frame.write.format("delta").mode("overwrite").save(delta_table_path)\n'
            '        else:\n'
            '            raise\n'
            '    if verbosity > 0:\n'
            '        print(f"Schema AFTER write ({table_name}):")\n'
            '        spark.read.format("delta").load(delta_table_path).printSchema()'
        ),
        cell(
            '# Load the delta table\n'
            'df_silver = load_delta_table_from_lakehouse(f"{silver_schema}/{silver_delta_table}", silver_lakehouse_name)\n'
            '\n'
            '# Drop all columns starting with "Silver"\n'
            'columns_to_drop = [c for c in df_silver.columns if c.startswith("Silver")]\n'
            'df_gold = df_silver.drop(*columns_to_drop)\n'
            '\n'
            '# Add Gold timestamp columns\n'
            'if add_audit_columns :\n'
            '    df_final = add_audit_columns(df_gold, "Gold")\n'
            'else :\n'
            '    df_final = df_gold\n'
            '\n'
            '# Write the modified dataframe\n'
            'write_delta_table_to_lakehouse(f"{gold_schema}/{gold_delta_table}", gold_lakehouse_name, df_final, drop_before_write=drop_before_write, force=force, verbosity=verbosity)'
        ),
    ],
}

# ── Gold_Functions_v2 ──
gold_funcs = {
    "nbformat": 4, "nbformat_minor": 5, "metadata": META,
    "cells": [
        cell("%run Common_Variables"),
        cell("%run Silver_Functions"),
        cell(
            'def create_dag_config(table_mappings, retry_count=5, retry_interval=10, timeout_seconds=360, concurrency_count=16, drop_before_write: bool = False, force: bool = False, verbosity: int = 0, add_audit_columns: bool = True):\n'
            '    """v2: concurrency default 16, path -> Gold_Parameter_v2"""\n'
            '    activities = []\n'
            '    seen_names = set()\n'
            '    for mapping in table_mappings:\n'
            '        base_name = mapping.get("name", mapping["silver_table"])\n'
            '        activity_name = base_name\n'
            '        if activity_name in seen_names:\n'
            '            activity_name = f"{base_name}__{mapping[\'gold_table\']}"\n'
            '            suffix = 2\n'
            '            while activity_name in seen_names:\n'
            '                activity_name = f"{base_name}__{mapping[\'gold_table\']}__{suffix}"\n'
            '                suffix += 1\n'
            '        seen_names.add(activity_name)\n'
            '        activity = {\n'
            '            "name": activity_name,\n'
            '            "path": "Gold_Parameter_v2",\n'
            '            "timeoutPerCellInSeconds": timeout_seconds,\n'
            '            "retry": retry_count,\n'
            '            "retryIntervalInSeconds": retry_interval,\n'
            '            "args": {\n'
            '                "silver_delta_table": mapping["silver_table"],\n'
            '                "gold_delta_table": mapping["gold_table"],\n'
            '                "drop_before_write": drop_before_write,\n'
            '                "add_audit_columns": add_audit_columns,\n'
            '                "force": force,\n'
            '                "verbosity": verbosity,\n'
            '            },\n'
            '            "dependencies": [],\n'
            '        }\n'
            '        activities.append(activity)\n'
            '    dag = {"activities": activities, "timeoutInSeconds": 3600, "concurrency": concurrency_count}\n'
            '    return dag'
        ),
    ],
}

# ── Gold_ExecutionBook_v2 ──
TABLES_SRC = '''tables = [
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

dag_config = create_dag_config(tables, retry_count=0, drop_before_write=drop_before_write, force=True, verbosity=verbosity, add_audit_columns=add_audit_columns)'''

gold_exec = {
    "nbformat": 4, "nbformat_minor": 5, "metadata": META,
    "cells": [
        cell("%run Gold_Functions_v2"),
        cell(
            'drop_before_write=False\n'
            'force=False\n'
            'verbosity = 1\n'
            'add_audit_columns=False'
        ),
        cell(TABLES_SRC),
        cell('mssparkutils.notebook.runMultiple(dag_config, {"displayDAGViaGraphviz": False})'),
        cell('refresh_sql_endpoint(gold_lakehouse_name)'),
    ],
}

# ── Silver_Gold_ExecutionBook_v2 ──
sg_exec = {
    "nbformat": 4, "nbformat_minor": 5, "metadata": META,
    "cells": [
        cell(
            'retry_count = 0\n'
            'drop_before_write = False'
        ),
        cell(
            'DAG = {\n'
            '    "activities": [\n'
            '        {\n'
            '            "name": "Silver",\n'
            '            "path": "Silver_ExecutionBook",\n'
            '            "timeoutPerCellInSeconds": 360,\n'
            '            "retry": retry_count,\n'
            '            "retryIntervalInSeconds": 10,\n'
            '            "args": { "drop_before_write" : drop_before_write},\n'
            '        },\n'
            '        {\n'
            '            "name": "Gold",\n'
            '            "path": "Gold_ExecutionBook_v2",\n'
            '            "timeoutPerCellInSeconds": 360,\n'
            '            "retry": retry_count,\n'
            '            "retryIntervalInSeconds": 10,\n'
            '            "args": { "drop_before_write" : drop_before_write},\n'
            '            "dependencies" : ["Silver"]\n'
            '        }\n'
            '    ],\n'
            '    "timeoutInSeconds": 3600,\n'
            '    "concurrency": 16\n'
            '}\n'
            'mssparkutils.notebook.runMultiple(DAG, {"displayDAGViaGraphviz": True})'
        ),
    ],
}

# Write all definitions
for name, nb in [
    ("gold_param_v2_def", gold_param),
    ("gold_functions_v2_def", gold_funcs),
    ("gold_executionbook_v2_def", gold_exec),
    ("silver_gold_executionbook_v2_def", sg_exec),
]:
    defn = make_def(nb)
    path = f"{OUT}/{name}.json"
    with open(path, "w") as f:
        json.dump(defn, f)
    print(f"  {name}.json OK")
