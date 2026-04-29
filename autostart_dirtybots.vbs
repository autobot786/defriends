Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "E:\Pros\secmesh_scaffold\"
WshShell.Environment("Process").Item("DIRTYBOT_MAPPING_PACK") = "E:\Pros\secmesh_scaffold\rules\mapping\mitre_cwe_context.v1.yaml"
WshShell.Environment("Process").Item("DIRTYBOT_REPORT_SCHEMA") = "E:\Pros\secmesh_scaffold\schemas\report.schema.json"
WshShell.Environment("Process").Item("DIRTYBOT_ORG_ID") = "demo-org"
WshShell.Environment("Process").Item("PORT") = "8080"
WshShell.Run """C:\Users\venka\.venv\Scripts\python.exe"" -m uvicorn app_unified:app --host 127.0.0.1 --port 8080", 0, False
