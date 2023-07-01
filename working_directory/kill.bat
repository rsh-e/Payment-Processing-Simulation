@echo off

REM Close PowerShell windows with specified titles
taskkill /F /FI "WINDOWTITLE eq Gateway" /T > nul
taskkill /F /FI "WINDOWTITLE eq Bank1" /T > nul
taskkill /F /FI "WINDOWTITLE eq Bank2" /T > nul
taskkill /F /FI "WINDOWTITLE eq Customer" /T > nul
taskkill /F /FI "WINDOWTITLE eq Merchant" /T > nul


echo All windows closed.
