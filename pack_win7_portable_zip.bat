@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PY38=%LocalAppData%\Programs\Python\Python38\python.exe"
if not exist "%PY38%" (
  echo [错误] 未找到 Python 3.8 64 位，路径应为:
  echo   %PY38%
  echo 请安装: https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
  echo 安装时可勾选 Add Python to PATH；装好后重新运行本脚本。
  pause
  exit /b 1
)

echo 使用: %PY38%
"%PY38%" -m pip install -r requirements-win7.txt -i https://pypi.org/simple/
if errorlevel 1 ( pause & exit /b 1 )

"%PY38%" -m PyInstaller --onedir --noconsole --name ScreenReminder --clean --noconfirm --add-data "sounds/default_shutter.mp3;sounds" --add-data "sounds/ATTRIBUTION.txt;sounds" main.py
if errorlevel 1 ( pause & exit /b 1 )

"%PY38%" "%~dp0bundle_portable_runtime.py" "%~dp0dist\ScreenReminder"
copy /Y "%~dp0pack_win7_README.txt" "%~dp0dist\ScreenReminder\使用说明.txt" >nul

set "ZIP=%USERPROFILE%\Desktop\ScreenReminder-portable-Win7-SP1-x64.zip"
powershell -NoProfile -Command "Compress-Archive -Path '%~dp0dist\ScreenReminder' -DestinationPath '%ZIP%' -Force"
echo.
echo 已生成: %ZIP%
pause
