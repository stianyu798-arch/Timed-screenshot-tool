@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 正在打包单文件 ScreenReminder.exe ...
python -m PyInstaller ScreenReminder.spec --clean --noconfirm
if errorlevel 1 (
  echo 失败。请确认已安装: pip install pyinstaller pillow
  pause
  exit /b 1
)

echo.
echo 完成: %~dp0dist\ScreenReminder.exe
if exist "%USERPROFILE%\Desktop\" (
  copy /Y "%~dp0dist\ScreenReminder.exe" "%USERPROFILE%\Desktop\ScreenReminder.exe"
  echo 已复制到桌面: ScreenReminder.exe
)
echo.
pause
