屏幕定时提醒 — Windows 7 便携版（64 位）
========================================

使用方法
--------
1. 解压本压缩包到任意文件夹（须保留同目录全部文件与 _internal 文件夹，勿只复制 ScreenReminder.exe）。
2. 双击 ScreenReminder.exe 运行。

系统要求
--------
- Windows 7 SP1 或更高版本，64 位。
- 若启动时提示缺少 api-ms-win-crt-*.dll：请安装微软更新 KB2999226（通用 C 运行库 / UCRT），或通过 Windows Update 安装系统补丁。
- 若仍提示缺少 VCRUNTIME140.dll：请安装「Microsoft Visual C++ 2015-2022 可再发行组件」x64 版（本包已尽量附带部分运行库 DLL，多数电脑无需再装）。

本压缩包使用 Python 3.8 + PyInstaller 在本机打包，面向旧版 Windows 兼容。
