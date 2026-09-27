' Start the Bakery Tracker server in the background with NO console window.
'
'   Double-click this file. Then open http://localhost:3000 as usual.
'   To stop the server, double-click stop-server.bat next to this file.
'
' If you put a shortcut to this file in your Startup folder so it runs at
' boot, delete the last line (the WScript.Echo) so no message box appears.

Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")

' This file lives in <bakery>\windows, so the bakery folder is one level up.
bakery = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
sh.CurrentDirectory = bakery

' 0 = hidden window, False = do not wait for it to finish.
sh.Run "node --disable-warning=ExperimentalWarning server/index.js", 0, False

WScript.Echo "Bakery Tracker is running in the background." & vbCrLf & _
             "Open http://localhost:3000 in your browser."
