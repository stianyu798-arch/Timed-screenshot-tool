@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 生成可在 Windows 7 SP1+ 上「免装 VC++ 安装包」的便携版
echo ========================================
echo 说明：使用 onedir 打包，并把运行库 DLL 拷进同一目录；
echo       旧电脑只需复制整个输出文件夹，无需运行 VC++ 安装程序。
echo.
echo 要求：本机已安装 Python 3.8（与目标系统同为 32/64 位）
echo 下载： https://www.python.org/downloads/release/python-3810/
echo.

py -3.8 -m pip install -r requirements-win7.txt -i https://pypi.org/simple/
if errorlevel 1 (
  echo.
  echo 若提示找不到 Python 3.8，请将下面命令中的 py -3.8 改为你的 python.exe 路径。
  pause
  exit /b 1
)

echo 正在 PyInstaller ^(onedir，便于附带 DLL 与快门音效 MP3^)...
py -3.8 -m PyInstaller --onedir --noconsole --name ScreenReminder --clean --add-data "sounds/default_shutter.mp3;sounds" --add-data "sounds/ATTRIBUTION.txt;sounds" main.py
if errorlevel 1 (
  pause
  exit /b 1
)

set "OUTDIR=%~dp0dist\ScreenReminder"
echo.
echo 正在把 MSVC 运行库 DLL 复制到输出目录（与 exe 同目录，无需在目标机安装 VC++）...
py -3.8 "%~dp0bundle_portable_runtime.py" "%OUTDIR%"
if errorlevel 1 (
  pause
  exit /b 1
)

echo.
echo ========================================
echo 完成。
echo 请将整个文件夹复制到 Win7 电脑：
echo   %OUTDIR%
echo 在其中运行 ScreenReminder.exe
echo.
echo 若极旧 Win7 仍提示缺 api-ms-win-crt-*.dll，需安装系统补丁 KB2999226（通用 C 运行库），
echo 这不是「VC++ 安装包」，属于 Windows 更新；完全未打补丁的 Win7 可能无法运行 Python 程序。
echo ========================================
pause
