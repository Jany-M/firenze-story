@echo off
rem Firenze Story - rebuild anything stale (textures, Blender props, city data), then start the local web app.
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
where python >nul 2>nul && (python pipeline\prepare.py) || echo [prepare] Python not found - using the assets already in web\public
cd web
if not exist node_modules call npm.cmd install --include=dev --no-audit --no-fund
call npm.cmd run dev
