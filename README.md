# Timed-screenshot-tool / 屏幕定时提醒

**EN:** A small Windows desktop utility for **scheduled reminders and full-screen screenshots**—with optional time windows, a pre-capture countdown, and shutter sound feedback.  
**中文：** 一款 Windows 桌面小工具：**定时提醒 + 全屏截图**，可限制在指定时段运行，截屏前有倒计时，并支持快门提示音。

> *摸鱼摸出来的小工具 · A side-project born from “productive procrastination”.*

---

## English

### Features

- **Interval capture** — Run every *N* seconds / minutes / hours.
- **Time window (optional)** — Only capture between a start and end time (e.g. work hours).
- **Countdown** — Short countdown bar before capture so you know a shot is coming.
- **Sound** — Optional shutter sound after a successful capture (uses `sounds/default_shutter.mp3` or `.wav` if present).
- **Portable** — No installer required; unzip the folder and run `ScreenReminder.exe` (keep **all** files next to the exe).

### System requirements

| Build | OS | Notes |
|--------|-----|--------|
| **Win7 portable zip** | Windows 7 SP1 **64-bit** and newer | Built with Python 3.8 for older systems. |
| **Win10/11 portable zip** | Windows 10 / 11 **64-bit** | Built with a newer Python runtime. |
| **Single-file exe** | Same as the machine used to build | One `ScreenReminder.exe`; larger file, easy to copy. |

If Windows reports missing **UCRT** (`api-ms-win-crt-*.dll`) on old Win7, install Microsoft update **KB2999226** or use Windows Update. If **VCRUNTIME140.dll** is missing, install **VC++ 2015–2022 x64** redistributable.

### Download (for end users)

**Please use [GitHub Releases](https://github.com/stianyu798-arch/Timed-screenshot-tool/releases)** when available:

- **`ScreenReminder-portable-Win7-SP1-x64.zip`** — For **Windows 7 (64-bit)**: extract the **entire folder**, then run **`ScreenReminder.exe`**. Do **not** copy only the exe.
- **`ScreenReminder-portable-Win10-11-x64.zip`** — For **Windows 10/11 (64-bit)**: same usage.

Until releases are published, clone this repository and build from source (see below), or ask the maintainer to attach the zip files to a Release.

### Quick usage

1. Set **save folder** (required).
2. Set **interval** and optional **time range**.
3. Click **Start**. Use **Capture now** for an immediate screenshot.

Config is stored next to the app: `screen_reminder_config.json`.

### Build from source

- **Run from source:** `pip install -r requirements.txt` then `python main.py`.
- **Single exe (Win10/11 dev machine):** `python -m PyInstaller ScreenReminder.spec --clean --noconfirm` or run `build_onefile.bat`.
- **Portable folder + Win7-oriented zip:** Python **3.8 x64** + `pack_win7_portable_zip.bat` (see `requirements-win7.txt`).

---

## 简体中文

### 功能概览

- **定时截图**：按秒 / 分 / 小时间隔自动全屏截图。
- **可选时间段**：例如仅在 09:00–18:00 内自动截图。
- **截屏前倒计时**：避免毫无征兆地截屏。
- **提示音**：截屏成功后可播放快门音效（`sounds/default_shutter.mp3` 或 `.wav`）。
- **绿色免安装**：解压整个文件夹后运行 **`ScreenReminder.exe`**，**不要只复制 exe**，需保留同目录及 `_internal` 等文件。

### 系统要求

| 版本 | 系统 | 说明 |
|------|------|------|
| **Win7 便携 zip** | **Windows 7 SP1 及以上，64 位** | 使用 Python 3.8 构建，面向旧系统。 |
| **Win10/11 便携 zip** | **Windows 10 / 11，64 位** | 使用较新 Python 构建。 |

若 Win7 提示缺少 **api-ms-win-crt-*.dll**，请安装系统补丁 **KB2999226** 或通过 Windows Update 更新。若缺少 **VCRUNTIME140.dll**，可安装 **Microsoft Visual C++ 2015–2022（x64）** 运行库。

### 下载（给最终用户）

**请优先在 [GitHub Releases](https://github.com/stianyu798-arch/Timed-screenshot-tool/releases) 下载**（发布者上传 zip 后）：

- **`ScreenReminder-portable-Win7-SP1-x64.zip`** — 给 **64 位 Win7**：**整包解压**，运行 **`ScreenReminder.exe`**。
- **`ScreenReminder-portable-Win10-11-x64.zip`** — 给 **Win10/11 64 位**：用法同上。

若尚未发布 Release，可克隆本仓库自行按下方说明打包，或联系维护者将 zip 挂到 Release。

### 使用步骤

1. **保存位置**（必填）：截图输出目录。  
2. 设置 **时间间隔**，按需勾选 **仅在以下时间段内**。  
3. 点击 **开始**；需要时可 **立即截图一次**。

配置文件：`screen_reminder_config.json`（与程序同目录）。

### 从源码打包

- **直接运行：** `pip install -r requirements.txt`，再 `python main.py`。
- **单文件 exe：** `python -m PyInstaller ScreenReminder.spec --clean --noconfirm` 或运行 `build_onefile.bat`（适合在 Win10/11 开发机）。
- **Win7 便携 zip：** 安装 **Python 3.8 64 位** 后运行 `pack_win7_portable_zip.bat`，依赖见 `requirements-win7.txt`（注释为英文，避免中文系统下 pip 编码问题）。

---

## Repository / 仓库

- **GitHub:** [https://github.com/stianyu798-arch/Timed-screenshot-tool](https://github.com/stianyu798-arch/Timed-screenshot-tool)
- **License:** Not specified — add a `LICENSE` file if you redistribute publicly.

---

## Maintainer note / 维护说明

To ship binaries for others: attach **`ScreenReminder-portable-Win7-SP1-x64.zip`** and **`ScreenReminder-portable-Win10-11-x64.zip`** (or the single `ScreenReminder.exe`) to **GitHub → Releases → New release**, and describe the target OS in the release notes.

向他人分发时：请将上述 zip 或单文件 exe 上传到 **GitHub Releases**，并在说明里写清适用的 Windows 版本。
