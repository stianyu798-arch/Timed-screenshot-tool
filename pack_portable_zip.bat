@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在生成 onedir 便携目录并压缩为 zip...
python -m pip install -q Pillow pyinstaller
python -m PyInstaller --onedir --noconsole --name ScreenReminder --clean --noconfirm --add-data "sounds/default_shutter.mp3;sounds" --add-data "sounds/ATTRIBUTION.txt;sounds" main.py
if errorlevel 1 (
  echo 失败。
  pause
  exit /b 1
)
python bundle_portable_runtime.py "%~dp0dist\ScreenReminder"
copy /Y "%~dp0pack_portable_README.txt" "%~dp0dist\ScreenReminder\使用说明.txt" >nul
set "ZIP=%USERPROFILE%\Desktop\ScreenReminder-portable-Win10-11-x64.zip"
powershell -NoProfile -Command "Compress-Archive -Path '%~dp0dist\ScreenReminder' -DestinationPath '%ZIP%' -Force"
echo.
echo 已生成: %ZIP%
pause
