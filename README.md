# Timed-screenshot-tool / 屏幕定时提醒

<p align="center">
<b>Language / 语言</b><br>
<a href="#lang-en">English</a> &nbsp;|&nbsp; <a href="#lang-zh">简体中文</a>
</p>

**EN:** Reminds you on a timer and takes **full-screen screenshots** on Windows. You can limit captures to certain hours, get a short countdown before each shot, and hear an optional shutter sound. The window supports **中文 / English** (radio buttons at the top-right).  
**中文：** 在 Windows 上**按间隔提醒并全屏截图**；可设置仅在某时段内截图，截屏前有倒计时，并可播放提示音。界面右上角可切换 **中文 / English**。

---

<a id="lang-en"></a>

## English

### What it does

- Repeats every **N** seconds, minutes, or hours (you choose).
- Optionally **only between a start and end time** (e.g. only during work hours).
- Shows a **short countdown** before capturing so it does not surprise you.
- Optional **sound** after a successful capture.
- **No installer:** unpack the zip and run **`ScreenReminder.exe`**. Keep the **whole folder** (do not copy only the exe).

### Download

1. Open **[Releases](https://github.com/stianyu798-arch/Timed-screenshot-tool/releases)**.
2. Download the zip that matches your PC:
   - **`ScreenReminder-portable-Win7-SP1-x64.zip`** — **Windows 7 (64-bit)** and newer.
   - **`ScreenReminder-portable-Win10-11-x64.zip`** — **Windows 10 / 11 (64-bit)** (recommended on newer PCs).
3. **Extract the entire folder** anywhere you like.
4. Double-click **`ScreenReminder.exe`**.

If there is no Release yet, use **Code → Download ZIP** on the repo page to get the source, then run from Python (see **For developers** below).

### How to use

1. Choose a **save folder** (required).
2. Set the **interval** and, if needed, turn on **only within the time range** and set start/end times.
3. Click **Start**. Use **Capture now** for one immediate screenshot.

Settings are saved in **`screen_reminder_config.json`** next to the program.

### If the app does not start (missing DLL)

- **Old Windows 7:** If you see **`api-ms-win-crt-*.dll`** errors, install Windows update **[KB2999226](https://support.microsoft.com/kb/2999226)** or run **Windows Update**.
- **`VCRUNTIME140.dll` missing:** Install **[Microsoft VC++ 2015–2022 x64](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)** (“Visual C++ Redistributable”).

---

### For developers

Run from source:

```bat
pip install -r requirements.txt
python main.py
```

Build scripts (`build_onefile.bat`, `pack_win7_portable_zip.bat`, etc.) and `requirements-win7.txt` are for creating your own exe/portable zip on a Windows machine with Python installed.

---

<a id="lang-zh"></a>

## 简体中文

### 能做什么

- 按 **秒 / 分钟 / 小时** 间隔自动**全屏截图**。
- 可勾选 **仅在指定时间段内** 截图（例如只在工作时间）。
- 每次截图前有 **倒计时**，避免突然截屏。
- 可开启 **截屏成功提示音**。
- **无需安装程序**：下载 zip 后**整夹解压**，运行 **`ScreenReminder.exe`**。**请勿只复制 exe**，须保留同目录下所有文件（含 `_internal` 等）。

### 下载方式

1. 打开本仓库的 **[Releases（发行版）](https://github.com/stianyu798-arch/Timed-screenshot-tool/releases)**。
2. 按你的系统选择压缩包：
   - **`ScreenReminder-portable-Win7-SP1-x64.zip`** — 适合 **64 位 Windows 7** 及更高版本。
   - **`ScreenReminder-portable-Win10-11-x64.zip`** — 适合 **Windows 10 / 11（64 位）**（新系统建议用这个）。
3. **解压整个文件夹**到任意位置。
4. 双击 **`ScreenReminder.exe`** 运行。

若暂时没有 Release，可在仓库页面点击 **Code → Download ZIP** 下载源码，安装 Python 后自行运行（见文末 **开发者**）。

### 使用步骤

1. 填写 **保存位置**（必填），截图会保存在该文件夹。
2. 设置 **时间间隔**；如需限制时段，勾选 **仅在以下时间段内** 并填写起止时间。
3. 点击 **开始**；需要时可点 **立即截图一次**。

设置保存在程序同目录下的 **`screen_reminder_config.json`**。

### 无法运行或提示缺 DLL

- **Win7 较旧：** 若提示 **`api-ms-win-crt-*.dll`**，请安装系统更新 **[KB2999226](https://support.microsoft.com/kb/2999226)** 或通过 **Windows 更新** 安装补丁。
- 若提示 **`VCRUNTIME140.dll`**：请安装 **[微软 VC++ 2015–2022 运行库（x64）](https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vc-redist)**。

---

### 开发者

从源码运行：

```bat
pip install -r requirements.txt
python main.py
```

仓库内另有打包脚本（如 `build_onefile.bat`、`pack_win7_portable_zip.bat`）与 `requirements-win7.txt`，供在本机安装 Python 后自行生成 exe / 便携包。

---

<p align="center">
<sub>摸鱼摸出来的小工具 · A small side-project</sub>
</p>
