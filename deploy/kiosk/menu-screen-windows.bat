@echo off
rem Shows the menu full screen on a Windows PC or mini PC.
rem 1. Change the address below (your shop + /tv, or a screen's own address).
rem 2. Press Win+R, type  shell:startup  and copy this file into that folder.
rem    The menu then starts every time the PC starts. Alt+F4 closes it.
set URL=https://backlover.de/tv
set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist %CHROME% set CHROME="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
start "" %CHROME% --kiosk --noerrdialogs --disable-session-crashed-bubble --autoplay-policy=no-user-gesture-required --user-data-dir="%LOCALAPPDATA%\MenuScreen" %URL%
