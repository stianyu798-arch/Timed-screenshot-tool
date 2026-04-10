# Upload README / 上传到 GitHub

This file explains how to push the bilingual `README.md` to  
`https://github.com/stianyu798-arch/Timed-screenshot-tool`

（本机需能访问 GitHub，并已配置 `git` 登录：HTTPS 密码/PAT 或 SSH。）

---

## Option A — Repo already exists on GitHub（仓库里已有内容）

```bat
cd %USERPROFILE%\Desktop
git clone https://github.com/stianyu798-arch/Timed-screenshot-tool.git
cd Timed-screenshot-tool
copy /Y "C:\Users\qings\Desktop\ScreenReminder\README.md" README.md
git add README.md
git commit -m "docs: add bilingual README (EN/ZH), download and Win7 notes"
git push origin main
```

If your default branch is `master`, use: `git push origin master`

---

## Option B — Push the whole project（把整个 ScreenReminder 工程推上去，方便别人下源码）

在资源管理器中把 `ScreenReminder` 目录里除 `build`、`dist`、`__pycache__` 外的文件复制到克隆下来的仓库目录，然后：

```bat
cd %USERPROFILE%\Desktop\Timed-screenshot-tool
git add -A
git status
git commit -m "feat: ScreenReminder source and bilingual README"
git push origin main
```

建议在 **Releases** 里再上传打好的 zip / exe，见 README 文末「Maintainer note」。

---

## Releases（给下载的人）

在 GitHub 网页：**Releases → Create a new release**，上传例如：

- `ScreenReminder-portable-Win7-SP1-x64.zip`
- `ScreenReminder-portable-Win10-11-x64.zip`

并在 Release 说明里写清适用的 Windows 版本。
