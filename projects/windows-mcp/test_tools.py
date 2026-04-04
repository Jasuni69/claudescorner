#!/usr/bin/env python3
"""Smoke test for windows-mcp tools (no MCP transport needed)."""
import sys
import json
import subprocess
import shutil

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))

# Replicate helper without MCP dependency
_PS = (
    shutil.which("powershell")
    or shutil.which("pwsh")
    or r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
)

def run_powershell(command: str, timeout: int = 30) -> dict:
    result = subprocess.run(
        [_PS, "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, text=True, timeout=timeout,
    )
    return {"stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "returncode": result.returncode}

print(f"Using PowerShell: {_PS}")

def test_run_ps1():
    result = run_powershell("Write-Output 'hello from ps1'")
    assert result["returncode"] == 0, f"Non-zero exit: {result}"
    assert "hello from ps1" in result["stdout"], f"Unexpected output: {result['stdout']}"
    print(f"[PASS] run_ps1: {result['stdout']!r}")

def test_event_log():
    # Just check we can parse JSON from PS
    result = run_powershell(
        "Get-EventLog -LogName System -Newest 3 "
        "| Select-Object EntryType, Source | ConvertTo-Json -Depth 1"
    )
    assert result["returncode"] == 0, f"Event log error: {result['stderr']}"
    import json
    data = json.loads(result["stdout"])
    if isinstance(data, dict):
        data = [data]
    assert len(data) > 0
    print(f"[PASS] read_event_log: got {len(data)} entries, first source={data[0].get('Source')}")

def test_scheduled_tasks():
    result = run_powershell(
        "Get-ScheduledTask | Select-Object -First 3 | ConvertTo-Json -Depth 1"
    )
    assert result["returncode"] == 0, f"Task error: {result['stderr']}"
    import json
    data = json.loads(result["stdout"])
    if isinstance(data, dict):
        data = [data]
    print(f"[PASS] list_scheduled_tasks: got {len(data)} sample tasks")

def test_system_info():
    result = run_powershell(
        "$cpu = (Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; "
        "Write-Output $cpu"
    )
    assert result["returncode"] == 0, f"Sys info error: {result['stderr']}"
    print(f"[PASS] get_system_info: CPU={result['stdout'].strip()}%")

if __name__ == "__main__":
    tests = [test_run_ps1, test_event_log, test_scheduled_tasks, test_system_info]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
    print(f"\n{'All tests passed' if not failed else f'{failed} test(s) failed'}")
    sys.exit(failed)
