@echo off
chcp 65001 >nul
setlocal
set "REPO_URL=https://github.com/stianyu798-arch/Timed-screenshot-tool.git"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SRC_README=%~dp0README.md"
set "CLONE_DIR=%DESKTOP%\Timed-screenshot-tool"

echo.
echo === Upload README to GitHub ===
echo Repo: %REPO_URL%
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo [错误] 未找到 git。请先安装 Git for Windows: https://git-scm.com/download/win
  pause
  exit /b 1
)

if not exist "%SRC_README%" (
  echo [错误] 找不到 README.md: %SRC_README%
  pause
  exit /b 1
)

cd /d "%DESKTOP%"
if exist "%CLONE_DIR%" (
  echo 已存在文件夹，更新仓库: %CLONE_DIR%
  cd /d "%CLONE_DIR%"
  git pull
  if errorlevel 1 (
    echo git pull 失败，请检查网络或手动删除文件夹后重试。
    pause
    exit /b 1
  )
) else (
  echo 正在克隆到: %CLONE_DIR%
  git clone "%REPO_URL%" "%CLONE_DIR%"
  if errorlevel 1 (
    echo [错误] git clone 失败。请检查网络、代理，以及是否已登录 GitHub（HTTPS 需 Personal Access Token）。
    pause
    exit /b 1
  )
  cd /d "%CLONE_DIR%"
)

copy /Y "%SRC_README%" "%CLONE_DIR%\README.md"
git add README.md
git status
git commit -m "docs: add bilingual README (EN/ZH), download and Win7 notes"
if errorlevel 1 (
  echo 若无变更可提交，可能 README 已相同。正在尝试 push...
)

git push origin main 2>nul
if errorlevel 1 (
  echo 尝试分支 master...
  git push origin master
)

if errorlevel 1 (
  echo.
  echo [错误] git push 失败。请在本机用 GitHub 账号登录（或配置 SSH），HTTPS 密码需使用 Personal Access Token。
  echo 说明: https://docs.github.com/en/authentication
  pause
  exit /b 1
)

echo.
echo 完成。请在浏览器打开仓库查看: https://github.com/stianyu798-arch/Timed-screenshot-tool
echo.
pause
