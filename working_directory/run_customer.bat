@echo off
setlocal

REM Create a new PowerShell terminal window and run each script in a separate window
start powershell.exe -NoExit -Command "$Host.UI.RawUI.WindowTitle = 'Gateway'; python gateway.py"
start powershell.exe -NoExit -Command "$Host.UI.RawUI.WindowTitle = 'Bank1'; python bank1.py"
start powershell.exe -NoExit -Command "$Host.UI.RawUI.WindowTitle = 'Bank2'; python bank2.py"
start powershell.exe -NoExit -Command "$Host.UI.RawUI.WindowTitle = 'Customer'; python customer.py"

echo Programs executing...
exit