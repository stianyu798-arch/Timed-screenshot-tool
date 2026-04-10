# -*- coding: utf-8 -*-
"""（可选）从维基共享资源下载相机快门 WAV 并截取前几秒，生成 sounds/default_shutter.wav。

当前默认音效为 sounds/default_shutter.mp3；若改用本脚本生成的 WAV，请放入 sounds/ 并按需调整打包列表。"""
from __future__ import print_function

import io
import os
import sys
import wave

from urllib.request import Request, urlopen

# CC BY-SA 3.0 — 见 sounds/ATTRIBUTION.txt
SRC = (
    "https://upload.wikimedia.org/wikipedia/commons/7/74/"
    "D7100_shot_sound_at_Continous_High%287fps%29.wav"
)
# 截取时长（秒），控制体积；连拍声前几帧即一次快门感
TRIM_SEC = 0.28


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out = os.path.join(root, "sounds", "default_shutter.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    print("Downloading:", SRC)
    req = Request(
        SRC,
        headers={
            "User-Agent": "ScreenReminder/1.0 (sound fetch; Wikimedia Commons CC BY-SA)",
        },
    )
    data = urlopen(req, timeout=120).read()
    bio = io.BytesIO(data)
    with wave.open(bio, "rb") as w:
        nch = w.getnchannels()
        sw = w.getsampwidth()
        fr = w.getframerate()
        n = int(fr * TRIM_SEC) * nch
        if n <= 0:
            print("Bad params", file=sys.stderr)
            return 1
        frames = w.readframes(n)

    with wave.open(out, "wb") as o:
        o.setnchannels(nch)
        o.setsampwidth(sw)
        o.setframerate(fr)
        o.writeframes(frames)

    print("Wrote:", out, "(%d bytes)" % os.path.getsize(out))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
