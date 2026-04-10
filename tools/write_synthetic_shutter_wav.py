# -*- coding: utf-8 -*-
"""（可选）离线生成简易快门风格 WAV。

默认发行版已使用 sounds/default_shutter.mp3，一般无需运行本脚本。
仅在需要纯 WAV 占位或离线测试时可执行。"""
from __future__ import print_function

import math
import os
import random
import struct
import sys
import wave


def write_shutter(path):
    sr = 44100
    duration = 0.16
    n = int(sr * duration)
    random.seed(42)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        for i in range(n):
            t = i / float(sr)
            env = math.exp(-t * 32.0)
            nse = random.random() * 2.0 - 1.0
            p1 = math.exp(-((t - 0.0025) ** 2) / (2 * 0.00055 ** 2))
            p2 = 0.42 * math.exp(-((t - 0.011) ** 2) / (2 * 0.0012 ** 2))
            v = nse * (p1 + p2) * env * 0.95
            v = max(-1.0, min(1.0, v))
            w.writeframes(struct.pack("<h", int(v * 32700)))


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out = os.path.join(root, "sounds", "default_shutter.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    write_shutter(out)
    print("Wrote:", out, "(%d bytes)" % os.path.getsize(out))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
