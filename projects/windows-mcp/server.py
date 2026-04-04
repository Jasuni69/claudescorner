#!/usr/bin/env python3
"""
windows-mcp/server.py — MCP server for Windows automation.

Tools:
  run_ps1            — execute a PowerShell script block, return stdout/stderr
  read_event_log     — fetch recent Windows event log entries
  list_scheduled_tasks — list Task Scheduler tasks and their last run status
  get_system_info    — CPU, memory, disk usage snapshot

Transport: stdio (Claude Desktop MCP config).
"""

import json
import subprocess
import sys
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

server = Server("windows-mcp")

# PowerShell executable — use full path for portability across shells
import shutil as _shutil
_PS = (
    _shutil.which("powershell")
    or _shutil.which("pwsh")
    or r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_powershell(command: str, timeout: int = 30) -> dict:
    """Run a PowerShell command, return {stdout, stderr, returncode}."""
    result = subprocess.run(
        [_PS, "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return {
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode,
    }


def ps1_to_json(command: str, timeout: int = 30) -> list | dict:
    """Run PowerShell command that outputs JSON, parse and return."""
    result = run_powershell(f"{command} | ConvertTo-Json -Depth 3", timeout=timeout)
    if result["returncode"] != 0:
        raise RuntimeError(result["stderr"] or "PowerShell error")
    raw = result["stdout"]
    if not raw:
        return []
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="run_ps1",
            description=(
                "Execute a PowerShell command or script block. "
                "Returns stdout, stderr, and exit code. "
                "WARNING: runs with current user privileges — don't run destructive commands."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "PowerShell command or script block to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default 30, max 120)",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
        ),
        types.Tool(
            name="read_event_log",
            description="Fetch recent Windows event log entries from System or Application log.",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_name": {
                        "type": "string",
                        "description": "Log to read: System, Application, or Security",
                        "enum": ["System", "Application", "Security"],
                        "default": "System",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of most recent entries to return (default 20, max 100)",
                        "default": 20,
                    },
                    "level": {
                        "type": "string",
                        "description": "Filter by level: Error, Warning, Information, or All",
                        "enum": ["Error", "Warning", "Information", "All"],
                        "default": "All",
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="list_scheduled_tasks",
            description="List Windows Task Scheduler tasks with their last run status and result.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "Task folder path (default: \\ for root, use \\Microsoft for system tasks)",
                        "default": "\\",
                    },
                    "include_disabled": {
                        "type": "boolean",
                        "description": "Include disabled tasks (default false)",
                        "default": False,
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get_system_info",
            description="Get CPU usage, memory usage, and top disk usage snapshot.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "run_ps1":
        command = arguments["command"]
        timeout = min(int(arguments.get("timeout", 30)), 120)
        try:
            result = run_powershell(command, timeout=timeout)
            output = (
                f"Exit code: {result['returncode']}\n"
                f"--- stdout ---\n{result['stdout'] or '(empty)'}\n"
                f"--- stderr ---\n{result['stderr'] or '(none)'}"
            )
        except subprocess.TimeoutExpired:
            output = f"ERROR: Command timed out after {timeout}s"
        return [types.TextContent(type="text", text=output)]

    elif name == "read_event_log":
        log_name = arguments.get("log_name", "System")
        count = min(int(arguments.get("count", 20)), 100)
        level = arguments.get("level", "All")

        level_filter = ""
        if level != "All":
            level_map = {"Error": 2, "Warning": 3, "Information": 4}
            level_num = level_map.get(level, 4)
            level_filter = f" | Where-Object {{$_.Level -eq {level_num}}}"

        ps_cmd = (
            f"Get-EventLog -LogName {log_name} -Newest {count}{level_filter} "
            f"| Select-Object TimeGenerated, EntryType, Source, EventID, Message "
            f"| ForEach-Object {{ [PSCustomObject]@{{ "
            f"  Time=$_.TimeGenerated.ToString('yyyy-MM-dd HH:mm:ss'); "
            f"  Level=$_.EntryType.ToString(); "
            f"  Source=$_.Source; "
            f"  EventID=$_.EventID; "
            f"  Message=($_.Message -split '`n')[0] }} }}"
        )

        try:
            data = ps1_to_json(ps_cmd, timeout=30)
            if isinstance(data, dict):
                data = [data]
            lines = [f"Event log: {log_name} | Level: {level} | Count: {len(data)}\n"]
            for e in data:
                lines.append(
                    f"[{e.get('Time','')}] {e.get('Level','?'):11s} "
                    f"src={e.get('Source','')} id={e.get('EventID','')} — "
                    f"{str(e.get('Message',''))[:120]}"
                )
            output = "\n".join(lines)
        except Exception as ex:
            output = f"ERROR reading event log: {ex}"

        return [types.TextContent(type="text", text=output)]

    elif name == "list_scheduled_tasks":
        folder = arguments.get("folder", "\\")
        include_disabled = arguments.get("include_disabled", False)

        enabled_filter = "" if include_disabled else " | Where-Object {$_.State -ne 'Disabled'}"
        ps_cmd = (
            f"Get-ScheduledTask -TaskPath '{folder}*'{enabled_filter} "
            f"| ForEach-Object {{ "
            f"  $info = $_ | Get-ScheduledTaskInfo; "
            f"  [PSCustomObject]@{{ "
            f"    Name=$_.TaskName; "
            f"    Path=$_.TaskPath; "
            f"    State=$_.State.ToString(); "
            f"    LastRun=if($info.LastRunTime){{$info.LastRunTime.ToString('yyyy-MM-dd HH:mm:ss')}}else{{'Never'}}; "
            f"    LastResult=$info.LastTaskResult; "
            f"    NextRun=if($info.NextRunTime){{$info.NextRunTime.ToString('yyyy-MM-dd HH:mm:ss')}}else{{'N/A'}} "
            f"  }} }}"
        )

        try:
            data = ps1_to_json(ps_cmd, timeout=45)
            if isinstance(data, dict):
                data = [data]
            lines = [f"Scheduled tasks in '{folder}' ({len(data)} tasks):\n"]
            for t in data:
                last_result = t.get("LastResult", 0)
                status = "OK" if last_result == 0 else f"ERR({last_result})"
                lines.append(
                    f"  [{t.get('State','?'):8s}] {t.get('Name','?'):<40s} "
                    f"LastRun: {t.get('LastRun','?')} {status:12s} "
                    f"Next: {t.get('NextRun','?')}"
                )
            output = "\n".join(lines)
        except Exception as ex:
            output = f"ERROR listing tasks: {ex}"

        return [types.TextContent(type="text", text=output)]

    elif name == "get_system_info":
        ps_cmd = r"""
$cpu = (Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
$os = Get-WmiObject Win32_OperatingSystem
$mem_total_gb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$mem_free_gb  = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$mem_used_pct = [math]::Round(100 * (1 - $os.FreePhysicalMemory / $os.TotalVisibleMemorySize), 1)
$disks = Get-WmiObject Win32_LogicalDisk -Filter "DriveType=3" |
    Select-Object DeviceID,
        @{n='TotalGB';e={[math]::Round($_.Size/1GB,1)}},
        @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB,1)}},
        @{n='UsedPct';e={[math]::Round(100*(1-$_.FreeSpace/$_.Size),1)}}
[PSCustomObject]@{
    CPU_Pct     = $cpu
    Mem_TotalGB = $mem_total_gb
    Mem_FreeGB  = $mem_free_gb
    Mem_UsedPct = $mem_used_pct
    Disks       = $disks
}
"""
        try:
            data = ps1_to_json(ps_cmd.strip(), timeout=20)
            if isinstance(data, list):
                data = data[0]
            disks = data.get("Disks", [])
            if isinstance(disks, dict):
                disks = [disks]
            disk_lines = "\n".join(
                f"  {d.get('DeviceID','?')} {d.get('TotalGB','?')} GB total, "
                f"{d.get('FreeGB','?')} GB free ({d.get('UsedPct','?')}% used)"
                for d in (disks or [])
            )
            output = (
                f"System snapshot — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"CPU:    {data.get('CPU_Pct', '?')}%\n"
                f"Memory: {data.get('Mem_UsedPct', '?')}% used "
                f"({data.get('Mem_FreeGB', '?')} GB free of {data.get('Mem_TotalGB', '?')} GB)\n"
                f"Disks:\n{disk_lines}"
            )
        except Exception as ex:
            output = f"ERROR getting system info: {ex}"

        return [types.TextContent(type="text", text=output)]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
