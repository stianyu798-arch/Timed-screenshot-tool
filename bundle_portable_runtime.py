# -*- coding: utf-8 -*-
"""
将当前 Python 3.8 安装目录下的 MSVC 运行库 DLL 复制到 PyInstaller 输出目录，
使旧电脑无需单独运行「Visual C++ 可再发行组件」安装程序（DLL 与 exe 同目录即可加载）。

说明：若目标 Win7 从未安装过系统更新，可能仍缺少「通用 C 运行库」(UCRT)，
此时需安装微软补丁 KB2999226（属系统组件，不是 VC++ 安装包）。无法在完全裸机的 Win7 上百分之百保证。
"""
import os
import shutil
import sys

# 与官方 Python 3.8 Windows 安装包一并提供的可再发行 DLL（与程序同目录即可）
NAMES = (
    "vcruntime140.dll",
    "vcruntime140_1.dll",
    "msvcp140.dll",
    "concrt140.dll",
)


def candidate_dirs():
    roots = []
    exe = sys.executable
    if exe:
        roots.append(os.path.dirname(os.path.abspath(exe)))
    if getattr(sys, "prefix", None):
        roots.append(sys.prefix)
    if getattr(sys, "base_prefix", None) and sys.base_prefix != sys.prefix:
        roots.append(sys.base_prefix)
    # 去重且保留顺序
    seen = set()
    out = []
    for r in roots:
        r = os.path.abspath(r)
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def main():
    if len(sys.argv) < 2:
        print("用法: python bundle_portable_runtime.py <PyInstaller 输出目录>")
        return 2
    dest = os.path.abspath(sys.argv[1])
    if not os.path.isdir(dest):
        print("错误: 目录不存在:", dest)
        return 1

    copied = []
    missing = []
    for name in NAMES:
        src = None
        for d in candidate_dirs():
            p = os.path.join(d, name)
            if os.path.isfile(p):
                src = p
                break
        if not src:
            missing.append(name)
            continue
        dst = os.path.join(dest, name)
        shutil.copy2(src, dst)
        copied.append(name)

    print("已复制到:", dest)
    for n in copied:
        print(" +", n)
    if missing:
        print("未找到（可忽略，若目标机已含系统 DLL）:", ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
