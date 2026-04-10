# -*- coding: utf-8 -*-
"""定时桌面提醒并全屏截图：开始/停止、间隔、时间段、须先指定保存路径。

截屏提示音默认使用 sounds/default_shutter.mp3（Windows MCI）；可选 default_shutter.wav（winsound）。
若在 Windows 7 上使用：请用 Python 3.8 64 位 + requirements-win7.txt（见 build_win7.bat）。
"""

import ctypes
import json
import math
import os
import re
import subprocess
import sys
import time as time_mod
import tkinter as tk
from datetime import datetime, time
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional, Tuple

from PIL import ImageGrab

try:
    import winsound
except ImportError:
    winsound = None  # type: ignore

try:
    import winreg  # Windows：读取 Steam 安装路径
except ImportError:
    winreg = None  # type: ignore

CONFIG_NAME = "screen_reminder_config.json"
# Steam 客户端内游戏截图提示音（与 F12 截图相同），通常在 resource 目录
STEAM_SCREENSHOT_WAV_CANDIDATES = ("camera1.wav",)

# 时间间隔：单位 -> (最小值, 最大值)；小时按 1～24 小时
INTERVAL_UNIT_LIMITS = {
    "seconds": (1, 86400),  # 1 秒～24 小时
    "minutes": (1, 1440),
    "hours": (1, 24),
}  # type: Dict[str, Tuple[int, int]]
INTERVAL_UNIT_CN = {"seconds": "秒", "minutes": "分钟", "hours": "小时"}
CN_TO_INTERVAL_UNIT = {v: k for k, v in INTERVAL_UNIT_CN.items()}

# 界面语言对应的间隔单位显示（配置里仍存 seconds/minutes/hours）
INTERVAL_BY_LANG = {
    "zh": {"seconds": "秒", "minutes": "分钟", "hours": "小时"},
    "en": {"seconds": "seconds", "minutes": "minutes", "hours": "hours"},
}


def unit_en_from_interval_display(lang, display_text):
    display_text = (display_text or "").strip()
    for u_en, lab in INTERVAL_BY_LANG.get(lang, INTERVAL_BY_LANG["zh"]).items():
        if lab == display_text:
            return u_en
    return "minutes"


def interval_display_for_unit(lang, unit_en):
    m = INTERVAL_BY_LANG.get(lang, INTERVAL_BY_LANG["zh"])
    return m.get(unit_en, m["minutes"])


STRINGS = {
    "zh": {
        "title": "屏幕定时提醒",
        "save_hint": "保存位置（必填，请先填写路径或点击「浏览…」）",
        "browse": "浏览…",
        "interval_title": "时间间隔（定时自动截图的频率）",
        "interval_suffix": "后提醒并截图一次",
        "range_only": "仅在以下时间段内自动提醒并截图",
        "from_lbl": "从",
        "to_lbl": "到",
        "sound_on": "截屏成功时播放提示音",
        "status_stopped": "状态：已停止",
        "status_running": "状态：运行中",
        "btn_start": "开始",
        "btn_stop": "停止",
        "capture_now": "立即截图一次",
        "quit": "退出",
        "countdown_title": "即将截屏",
        "countdown_sec": "{0} 秒",
        "countdown_zero": "0 秒",
        "lang_label": "语言 / Language:",
        "msg_need_folder": "请先指定截图保存文件夹（可输入完整路径或点击「浏览…」选择）。",
        "warn_no_folder": "未设置保存位置",
        "err_folder": "无法创建或使用该文件夹：{0}",
        "err_folder_title": "保存路径无效",
        "warn_time_title": "时间格式错误",
        "warn_time_msg": "请填写正确的时间段，例如 09:00 和 18:00。",
        "skip_window": "当前 {0} 不在设定时间段内，已跳过（{1}）",
        "capture_fail": "截图失败：{0}",
        "toast_fail": "截图失败，请查看窗口说明。",
        "last_time": "上次：{0}",
        "toast_done": "已截图：{0}",
        "toast_title": "提醒",
        "cfg_save_fail": "保存设置失败",
    },
    "en": {
        "title": "Screen Reminder",
        "save_hint": "Save folder (required; enter a path or click Browse…)",
        "browse": "Browse…",
        "interval_title": "Interval (how often to remind & capture)",
        "interval_suffix": "between each reminder & capture",
        "range_only": "Only remind & capture within the time range below",
        "from_lbl": "From",
        "to_lbl": "to",
        "sound_on": "Play sound after capture",
        "status_stopped": "Status: Stopped",
        "status_running": "Status: Running",
        "btn_start": "Start",
        "btn_stop": "Stop",
        "capture_now": "Capture now",
        "quit": "Exit",
        "countdown_title": "Capturing soon",
        "countdown_sec": "{0} s",
        "countdown_zero": "0 s",
        "lang_label": "语言 / Language:",
        "msg_need_folder": "Please set a save folder (path or Browse…).",
        "warn_no_folder": "No save folder",
        "err_folder": "Cannot create or use this folder: {0}",
        "err_folder_title": "Invalid path",
        "warn_time_title": "Invalid time range",
        "warn_time_msg": "Use times like 09:00 and 18:00.",
        "skip_window": "Now {0} is outside the allowed window, skipped ({1})",
        "capture_fail": "Capture failed: {0}",
        "toast_fail": "Capture failed; see the main window.",
        "last_time": "Last: {0}",
        "toast_done": "Saved: {0}",
        "toast_title": "Notice",
        "cfg_save_fail": "Failed to save settings",
    },
}
# 主窗口隐藏后等待若干毫秒再截图，避免仍拍到窗口残影
SCREENSHOT_HIDE_DELAY_MS = 220
# 截屏前倒计时（秒）与刷新间隔（毫秒）
COUNTDOWN_SECONDS = 5
COUNTDOWN_TICK_MS = 50


def resource_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def bundle_asset_dir():
    """打包内置资源目录（PyInstaller onefile/onedir 下为 sys._MEIPASS）。"""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def config_path():
    return os.path.join(resource_dir(), CONFIG_NAME)


def default_save_dir():
    return os.path.join(resource_dir(), "screenshots")


def get_steam_install_folder():
    """返回 Steam 根目录，例如 C:\\Program Files (x86)\\Steam。"""
    if sys.platform != "win32" or winreg is None:
        return None
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        try:
            path, _ = winreg.QueryValueEx(key, "SteamPath")
        finally:
            winreg.CloseKey(key)
        if path and os.path.isdir(path):
            return path
    except OSError:
        pass
    for env in ("ProgramFiles(x86)", "ProgramFiles"):
        base = os.environ.get(env)
        if not base:
            continue
        p = os.path.join(base, "Steam")
        if os.path.isdir(p):
            return p
    return None


def find_capture_sound_path():
    """
    优先：sounds/default_shutter.mp3 或 default_shutter.wav（与 exe 同目录或打包资源）。
    其次：sounds/camera1.wav、Steam resource\\camera1.wav。
    """
    candidates = (
        ("sounds", "default_shutter.mp3"),
        ("sounds", "default_shutter.wav"),
    )
    bd = bundle_asset_dir()
    for sub in candidates:
        p = os.path.join(bd, *sub)
        if os.path.isfile(p):
            return p
    rd = resource_dir()
    for sub in candidates:
        p = os.path.join(rd, *sub)
        if os.path.isfile(p):
            return p
    bundled = os.path.join(rd, "sounds", "camera1.wav")
    if os.path.isfile(bundled):
        return bundled
    bundled2 = os.path.join(rd, "camera1.wav")
    if os.path.isfile(bundled2):
        return bundled2
    root = get_steam_install_folder()
    if not root:
        return None
    for sub in ("resource", "Resource"):
        for name in STEAM_SCREENSHOT_WAV_CANDIDATES:
            fp = os.path.join(root, sub, name)
            if os.path.isfile(fp):
                return fp
    return None


def play_sound_mci(path):
    """用 winmm MCI 播放 MP3（winsound 仅支持 WAV）。同步播放直至结束。"""
    if sys.platform != "win32":
        return False
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return False
    mci = ctypes.windll.winmm.mciSendStringW
    err_buf = ctypes.create_unicode_buffer(512)
    alias = "sr_cap_snd"

    def cmd(s):
        return mci(s, err_buf, 512, None)

    cmd("close {0}".format(alias))
    ext = os.path.splitext(path)[1].lower()
    if ext == ".mp3":
        open_cmd = 'open "{0}" type mpegvideo alias {1}'.format(path, alias)
    elif ext == ".wav":
        open_cmd = 'open "{0}" type waveaudio alias {1}'.format(path, alias)
    else:
        return False
    if cmd(open_cmd) != 0:
        return False
    ok = cmd("play {0} wait".format(alias)) == 0
    cmd("close {0}".format(alias))
    return ok


def load_config():
    path = config_path()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_config(data, parent=None, error_title=None):
    path = config_path()
    if error_title is None:
        error_title = STRINGS["zh"]["cfg_save_fail"]
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        messagebox.showerror(error_title, str(e), parent=parent)


def parse_hhmm(s):
    s = s.strip()
    m = re.fullmatch(r"(\d{1,2}):(\d{1,2})", s)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 23 or mi > 59:
        return None
    return time(h, mi)


def normalize_time_input(s):
    """
    将输入规范为 HH:MM。
    仅数字：1～2 位为整点（12 -> 12:00）；3 位为 H+MM（130 -> 01:30）；4 位及以上为 HH+MM（0130 -> 01:30）。
    含冒号：按小时:分钟解析并补零。
    """
    s = (s or "").strip()
    if not s:
        return ""
    if ":" in s:
        parts = s.split(":", 1)
        da = re.sub(r"\D", "", parts[0])
        db = re.sub(r"\D", "", parts[1]) if len(parts) > 1 else ""
        if not da:
            return s
        h = int(da)
        if not db:
            m = 0
        else:
            m = int(db[:2]) if len(db) >= 2 else int(db)
        h = min(max(h, 0), 23)
        m = min(max(m, 0), 59)
        return "{0:02d}:{1:02d}".format(h, m)
    digits = re.sub(r"\D", "", s)
    if not digits:
        return s
    if len(digits) <= 2:
        h = int(digits)
        h = min(max(h, 0), 23)
        return "{0:02d}:00".format(h)
    if len(digits) == 3:
        h = int(digits[0])
        m = int(digits[1:3])
        h = min(max(h, 0), 23)
        m = min(max(m, 0), 59)
        return "{0:02d}:{1:02d}".format(h, m)
    h = int(digits[:2])
    m = int(digits[2:4])
    h = min(max(h, 0), 23)
    m = min(max(m, 0), 59)
    return "{0:02d}:{1:02d}".format(h, m)


def in_daily_window(now, start_t, end_t):
    t = now.time().replace(microsecond=0)
    if start_t <= end_t:
        return start_t <= t <= end_t
    return t >= start_t or t <= end_t


def load_interval_from_cfg(cfg):
    """返回 (间隔数值, 单位英文 seconds|minutes|hours)，兼容旧键 interval_minutes。"""
    unit = cfg.get("interval_unit", "minutes")
    if unit not in INTERVAL_UNIT_LIMITS:
        unit = "minutes"
    if "interval_value" in cfg:
        v = int(cfg["interval_value"])
    elif "interval_minutes" in cfg:
        v = int(cfg["interval_minutes"])
        unit = "minutes"
    else:
        v = 5
        unit = "minutes"
    lo, hi = INTERVAL_UNIT_LIMITS[unit]
    return max(lo, min(hi, v)), unit


def grab_full_screen():
    """兼容旧版 Pillow：无 all_screens 参数时退化为单屏。"""
    try:
        return ImageGrab.grab(all_screens=True)
    except TypeError:
        return ImageGrab.grab()


def take_screenshot(folder):
    os.makedirs(folder, exist_ok=True)
    img = grab_full_screen()
    name = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = os.path.join(folder, name)
    img.save(path, "PNG")
    return path


class App(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self._job = None  # type: Optional[str]
        self._running = False

        cfg = load_config()
        lang = cfg.get("ui_lang", "zh")
        if lang not in ("zh", "en"):
            lang = "zh"
        self._lang = lang
        self._ui_lang = tk.StringVar(value=lang)

        self._save_dir = tk.StringVar(value=(cfg.get("save_dir") or "").strip())
        iv, iu = load_interval_from_cfg(cfg)
        self._interval_value = tk.IntVar(value=iv)
        self._interval_unit_disp = tk.StringVar(value=interval_display_for_unit(lang, iu))
        self._range_on = tk.BooleanVar(value=bool(cfg.get("time_range_enabled", False)))
        self._t_start = tk.StringVar(value=str(cfg.get("time_start", "09:00")))
        self._t_end = tk.StringVar(value=str(cfg.get("time_end", "18:00")))
        self._sound_on = tk.BooleanVar(value=bool(cfg.get("sound_on_capture", True)))

        self._countdown_win = None  # type: Optional[tk.Toplevel]
        self._countdown_after_id = None  # type: Optional[str]

        pad = 14
        frm = tk.Frame(self.root, padx=pad, pady=pad)
        frm.pack(fill=tk.BOTH, expand=True)

        lang_row = tk.Frame(frm)
        lang_row.pack(anchor=tk.E, fill=tk.X)
        self._lbl_lang = tk.Label(lang_row, anchor=tk.E)
        self._lbl_lang.pack(side=tk.RIGHT)
        tk.Radiobutton(
            lang_row,
            text="English",
            variable=self._ui_lang,
            value="en",
            command=self._on_lang_change,
        ).pack(side=tk.RIGHT, padx=(4, 0))
        tk.Radiobutton(
            lang_row,
            text="中文",
            variable=self._ui_lang,
            value="zh",
            command=self._on_lang_change,
        ).pack(side=tk.RIGHT, padx=(4, 0))

        self._lbl_save = tk.Label(frm, anchor=tk.W)
        self._lbl_save.pack(fill=tk.X)
        path_row = tk.Frame(frm)
        path_row.pack(fill=tk.X, pady=(4, 0))
        ent = tk.Entry(path_row, textvariable=self._save_dir, width=48)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._btn_browse = tk.Button(path_row, command=self._browse_save)
        self._btn_browse.pack(side=tk.LEFT, padx=(8, 0))

        self._lbl_interval = tk.Label(frm, anchor=tk.W)
        self._lbl_interval.pack(fill=tk.X, pady=(12, 0))
        iv_fr = tk.Frame(frm)
        iv_fr.pack(anchor=tk.W, pady=(4, 0))
        lo, hi = INTERVAL_UNIT_LIMITS[iu]
        self._interval_spin = tk.Spinbox(
            iv_fr,
            from_=lo,
            to=hi,
            textvariable=self._interval_value,
            width=8,
        )
        self._interval_spin.pack(side=tk.LEFT)
        self._interval_unit_combo = ttk.Combobox(
            iv_fr,
            textvariable=self._interval_unit_disp,
            values=tuple(INTERVAL_BY_LANG[lang].values()),
            state="readonly",
            width=9,
        )
        self._interval_unit_combo.pack(side=tk.LEFT, padx=(8, 0))
        self._interval_unit_combo.bind("<<ComboboxSelected>>", self._on_interval_unit_selected)
        self._interval_value.trace_add("write", lambda *_: self._on_interval_change())
        self._lbl_interval_suffix = tk.Label(iv_fr, fg="#555")
        self._lbl_interval_suffix.pack(side=tk.LEFT, padx=(8, 0))

        self._chk_range = tk.Checkbutton(
            frm,
            variable=self._range_on,
            command=self._persist,
        )
        self._chk_range.pack(anchor=tk.W, pady=(12, 0))

        tr = tk.Frame(frm)
        tr.pack(anchor=tk.W, pady=(4, 0))
        self._lbl_from = tk.Label(tr)
        self._lbl_from.pack(side=tk.LEFT)
        self._entry_t_start = tk.Entry(tr, textvariable=self._t_start, width=8)
        self._entry_t_start.pack(side=tk.LEFT, padx=4)
        self._lbl_to = tk.Label(tr)
        self._lbl_to.pack(side=tk.LEFT)
        self._entry_t_end = tk.Entry(tr, textvariable=self._t_end, width=8)
        self._entry_t_end.pack(side=tk.LEFT, padx=4)
        for w in (self._entry_t_start, self._entry_t_end):
            w.bind("<KeyRelease>", self._on_time_key_release)
            w.bind("<FocusOut>", self._on_time_focus_out)
            w.bind("<Return>", self._on_time_focus_out)

        snd = tk.Frame(frm)
        snd.pack(fill=tk.X, pady=(12, 0))
        self._chk_sound = tk.Checkbutton(
            snd,
            variable=self._sound_on,
            command=self._persist,
        )
        self._chk_sound.pack(anchor=tk.W)

        self.state_lbl = tk.Label(frm, fg="#a40", justify=tk.LEFT)
        self.state_lbl.pack(anchor=tk.W, pady=(12, 0))

        self.status = tk.Label(frm, text="", fg="#333", justify=tk.LEFT, wraplength=460)
        self.status.pack(anchor=tk.W, pady=(6, 0))

        self.last_path = tk.Label(frm, text="", fg="#0066cc", justify=tk.LEFT, wraplength=460, cursor="hand2")
        self.last_path.pack(anchor=tk.W, pady=(4, 0))
        self.last_path.bind("<Button-1>", self._open_folder)

        btn_row = tk.Frame(frm)
        btn_row.pack(anchor=tk.W, pady=(12, 0))
        self.btn_start = tk.Button(btn_row, command=self._start, width=11)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 8))
        self.btn_stop = tk.Button(btn_row, command=self._stop, width=11, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 8))
        self._btn_cap = tk.Button(btn_row, command=self._screenshot_now)
        self._btn_cap.pack(side=tk.LEFT, padx=(0, 8))
        self._btn_quit = tk.Button(btn_row, command=self._quit)
        self._btn_quit.pack(side=tk.LEFT)

        self.root.protocol("WM_DELETE_WINDOW", self._quit)

        self._pb_style = ttk.Style()
        try:
            self._pb_style.theme_use("clam")
        except tk.TclError:
            pass
        self._pb_style.configure(
            "Countdown.Horizontal.TProgressbar",
            troughcolor="#333333",
            background="#4caf50",
            thickness=14,
        )

        self._apply_ui_lang()

    def _tr(self, key):
        return STRINGS.get(self._lang, STRINGS["zh"]).get(key, key)

    def _on_lang_change(self):
        u_en = unit_en_from_interval_display(self._lang, self._interval_unit_disp.get())
        self._lang = self._ui_lang.get()
        self._interval_unit_disp.set(interval_display_for_unit(self._lang, u_en))
        self._interval_unit_combo.config(values=tuple(INTERVAL_BY_LANG[self._lang].values()))
        self._apply_ui_lang()
        self._apply_interval_spin_limits()
        self._persist()

    def _apply_ui_lang(self):
        self._lang = self._ui_lang.get()
        self.root.title(self._tr("title"))
        self._lbl_lang.config(text=self._tr("lang_label"))
        self._lbl_save.config(text=self._tr("save_hint"))
        self._btn_browse.config(text=self._tr("browse"))
        self._lbl_interval.config(text=self._tr("interval_title"))
        self._lbl_interval_suffix.config(text=self._tr("interval_suffix"))
        self._chk_range.config(text=self._tr("range_only"))
        self._lbl_from.config(text=self._tr("from_lbl"))
        self._lbl_to.config(text=self._tr("to_lbl"))
        self._chk_sound.config(text=self._tr("sound_on"))
        self.btn_start.config(text=self._tr("btn_start"))
        self.btn_stop.config(text=self._tr("btn_stop"))
        self._btn_cap.config(text=self._tr("capture_now"))
        self._btn_quit.config(text=self._tr("quit"))
        if self._running:
            self.state_lbl.config(text=self._tr("status_running"), fg="#060")
        else:
            self.state_lbl.config(text=self._tr("status_stopped"), fg="#a40")

    def _on_time_key_release(self, event):
        """尚未出现冒号且已输入两位数字时，自动插入冒号（便于继续输入分钟）。"""
        if event.keysym in (
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R",
            "Tab",
            "Return",
            "Escape",
            "BackSpace",
            "Delete",
            "Left",
            "Right",
            "Up",
            "Down",
            "Home",
            "End",
            "Next",
            "Prior",
            "Insert",
        ):
            return
        w = event.widget
        if w not in (self._entry_t_start, self._entry_t_end):
            return
        var = self._t_start if w is self._entry_t_start else self._t_end
        raw = var.get()
        if ":" in raw:
            return
        digits = re.sub(r"\D", "", raw)
        if len(digits) == 2:
            newv = digits[:2] + ":"
            if raw != newv:
                var.set(newv)
                try:
                    w.icursor(len(newv))
                except tk.TclError:
                    pass
                self._persist()

    def _on_time_focus_out(self, event=None):
        w = event.widget if event else None
        if w is self._entry_t_start:
            v = self._t_start.get()
            n = normalize_time_input(v)
            if n:
                self._t_start.set(n)
        elif w is self._entry_t_end:
            v = self._t_end.get()
            n = normalize_time_input(v)
            if n:
                self._t_end.set(n)
        self._persist()

    def _play_capture_sound(self):
        """定时截图与「立即截图」成功后均调用。MP3 走 MCI；WAV 走 winsound；多重回退。"""
        if not self._sound_on.get():
            return
        p = find_capture_sound_path()
        if not p or not os.path.isfile(p):
            p = None
        else:
            p = os.path.normpath(os.path.abspath(p))

        if p and p.lower().endswith(".mp3"):
            try:
                if play_sound_mci(p):
                    return
            except Exception:
                pass

        paths = []
        if p and p.lower().endswith(".wav"):
            paths.append(p)

        # WAV：内存播放优先，避免 SND_ASYNC + 路径问题
        if winsound is not None:
            for pth in paths:
                try:
                    with open(pth, "rb") as f:
                        data = f.read()
                    if len(data) < 44:
                        continue
                    winsound.PlaySound(data, winsound.SND_MEMORY | winsound.SND_SYNC)
                    return
                except Exception:
                    continue
            for pth in paths:
                try:
                    winsound.PlaySound(pth, winsound.SND_FILENAME | winsound.SND_SYNC)
                    return
                except Exception:
                    continue
            # 系统方案音（若用户在「声音」里关掉「系统声音」则可能仍无声）
            for _attempt in (
                lambda: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_SYNC),
                lambda: winsound.PlaySound("SystemDefault", winsound.SND_ALIAS | winsound.SND_SYNC),
                lambda: winsound.MessageBeep(winsound.MB_OK),
            ):
                try:
                    _attempt()
                    return
                except Exception:
                    continue

        # 4) 不依赖波形资源：扬声器蜂鸣（多数机器可听见）
        if sys.platform == "win32":
            try:
                ctypes.windll.user32.MessageBeep(0xFFFFFFFF)
                return
            except Exception:
                pass
            try:
                ctypes.windll.kernel32.Beep(880, 140)
            except Exception:
                pass

    def _cancel_prescreenshot_countdown(self):
        if self._countdown_after_id is not None:
            try:
                self.root.after_cancel(self._countdown_after_id)
            except (tk.TclError, ValueError):
                pass
            self._countdown_after_id = None
        if self._countdown_win is not None:
            try:
                self._countdown_win.destroy()
            except tk.TclError:
                pass
            self._countdown_win = None

    def _start_prescreenshot_countdown(self, folder, show_toast):
        self._cancel_prescreenshot_countdown()
        top = tk.Toplevel(self.root)
        self._countdown_win = top
        top.overrideredirect(True)
        top.attributes("-topmost", True)
        top.configure(bg="#1a1a1a")

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        bar_w = 300
        bar_h = 72
        margin_x = 20
        margin_y = 56
        x = max(0, sw - bar_w - margin_x)
        y = max(0, sh - bar_h - margin_y)
        top.geometry("{0}x{1}+{2}+{3}".format(bar_w, bar_h, x, y))

        outer = tk.Frame(top, bg="#1a1a1a", padx=14, pady=10)
        outer.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            outer,
            text=self._tr("countdown_title"),
            fg="#ffffff",
            bg="#1a1a1a",
            font=("Segoe UI", 10, "bold"),
        )
        title.pack(anchor=tk.W)

        pb = ttk.Progressbar(
            outer,
            style="Countdown.Horizontal.TProgressbar",
            length=bar_w - 28,
            mode="determinate",
            maximum=COUNTDOWN_SECONDS * 1000,
        )
        pb.pack(fill=tk.X, pady=(8, 4))

        num_lbl = tk.Label(
            outer,
            text="",
            fg="#aaaaaa",
            bg="#1a1a1a",
            font=("Segoe UI", 9),
        )
        num_lbl.pack(anchor=tk.E)

        pb["value"] = COUNTDOWN_SECONDS * 1000
        t0 = time_mod.monotonic()

        def tick():
            if self._countdown_win is not top:
                return
            try:
                if not top.winfo_exists():
                    return
            except tk.TclError:
                return
            elapsed = time_mod.monotonic() - t0
            left = COUNTDOWN_SECONDS - elapsed
            if left <= 0:
                pb["value"] = 0
                num_lbl.config(text=self._tr("countdown_zero"))
                top.update_idletasks()
                self._cancel_prescreenshot_countdown()
                self._withdraw_and_capture(folder, show_toast)
                return
            rem_ms = int(left * 1000)
            pb["value"] = rem_ms
            num_lbl.config(text=self._tr("countdown_sec").format(int(math.ceil(left))))
            self._countdown_after_id = self.root.after(COUNTDOWN_TICK_MS, tick)

        self._countdown_after_id = self.root.after(30, tick)

    def _withdraw_and_capture(self, folder, show_toast):
        try:
            self.root.withdraw()
        except tk.TclError:
            pass
        self.root.update_idletasks()
        self.root.after(
            SCREENSHOT_HIDE_DELAY_MS,
            lambda: self._capture_after_hidden(folder, show_toast),
        )

    def _interval_unit_en(self):
        return unit_en_from_interval_display(self._lang, self._interval_unit_disp.get())

    def _clamp_interval_value(self):
        lo, hi = INTERVAL_UNIT_LIMITS[self._interval_unit_en()]
        try:
            v = int(self._interval_value.get())
        except (tk.TclError, ValueError):
            v = lo
        v = max(lo, min(hi, v))
        if self._interval_value.get() != v:
            self._interval_value.set(v)

    def _apply_interval_spin_limits(self):
        u = self._interval_unit_en()
        lo, hi = INTERVAL_UNIT_LIMITS[u]
        self._interval_spin.config(from_=lo, to=hi)
        self._clamp_interval_value()

    def _on_interval_unit_selected(self, _event=None):
        self._apply_interval_spin_limits()
        self._on_interval_change()

    def _persist(self):
        self._clamp_interval_value()
        unit_en = self._interval_unit_en()
        try:
            val = int(self._interval_value.get())
        except (tk.TclError, ValueError):
            val = INTERVAL_UNIT_LIMITS[unit_en][0]
        lo, hi = INTERVAL_UNIT_LIMITS[unit_en]
        val = max(lo, min(hi, val))
        save_config(
            {
                "save_dir": self._save_dir.get().strip(),
                "interval_value": val,
                "interval_unit": unit_en,
                "time_range_enabled": self._range_on.get(),
                "time_start": self._t_start.get().strip(),
                "time_end": self._t_end.get().strip(),
                "sound_on_capture": self._sound_on.get(),
                "ui_lang": self._lang,
            },
            parent=self.root,
            error_title=self._tr("cfg_save_fail"),
        )

    def _browse_save(self):
        d = filedialog.askdirectory(initialdir=self._save_dir.get() or default_save_dir())
        if d:
            self._save_dir.set(d)
            self._persist()

    def _on_interval_change(self):
        self._persist()
        if self._running:
            self._schedule_next()

    def _require_save_folder(self, silent):
        """返回可用的保存目录；未填写或无法创建时返回 None。"""
        p = self._save_dir.get().strip()
        if not p:
            msg = self._tr("msg_need_folder")
            if silent:
                self.status.config(text=msg)
            else:
                messagebox.showwarning(self._tr("warn_no_folder"), msg, parent=self.root)
            return None
        try:
            os.makedirs(p, exist_ok=True)
        except OSError as e:
            err = self._tr("err_folder").format(e)
            if silent:
                self.status.config(text=err)
            else:
                messagebox.showerror(self._tr("err_folder_title"), err, parent=self.root)
            return None
        return p

    def _get_interval_ms(self):
        self._clamp_interval_value()
        unit_en = self._interval_unit_en()
        try:
            v = int(self._interval_value.get())
        except (tk.TclError, ValueError):
            lo, _ = INTERVAL_UNIT_LIMITS[unit_en]
            v = lo
        lo, hi = INTERVAL_UNIT_LIMITS[unit_en]
        v = max(lo, min(hi, v))
        if unit_en == "seconds":
            sec = v
        elif unit_en == "minutes":
            sec = v * 60
        else:
            sec = v * 3600
        sec = max(1, min(86400, sec))
        return sec * 1000

    def _parse_window_times(self):
        a = parse_hhmm(normalize_time_input(self._t_start.get()))
        b = parse_hhmm(normalize_time_input(self._t_end.get()))
        if a is None or b is None:
            return None
        return a, b

    def _open_folder(self, _event=None):
        folder = self._require_save_folder(silent=False)
        if folder is None:
            return
        subprocess.run(["explorer", folder], check=False)

    def _start(self):
        if self._require_save_folder(silent=False) is None:
            return
        for var in (self._t_start, self._t_end):
            n = normalize_time_input(var.get())
            if n:
                var.set(n)
        if self._range_on.get():
            if self._parse_window_times() is None:
                messagebox.showwarning(
                    self._tr("warn_time_title"),
                    self._tr("warn_time_msg"),
                    parent=self.root,
                )
                return
        self._persist()
        if self._running:
            return
        self._running = True
        self.state_lbl.config(text=self._tr("status_running"), fg="#060")
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self._schedule_next()

    def _stop(self):
        self._cancel_prescreenshot_countdown()
        if not self._running:
            return
        self._running = False
        if self._job is not None:
            self.root.after_cancel(self._job)
            self._job = None
        self.state_lbl.config(text=self._tr("status_stopped"), fg="#a40")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

    def _schedule_next(self):
        if self._job is not None:
            self.root.after_cancel(self._job)
        self._job = self.root.after(self._get_interval_ms(), self._on_timer)

    def _on_timer(self):
        if not self._running:
            return
        self._job = None
        now = datetime.now()
        should_capture = True
        if self._range_on.get():
            tw = self._parse_window_times()
            if tw is None:
                should_capture = False
            else:
                should_capture = in_daily_window(now, tw[0], tw[1])
        if should_capture:
            self._do_screenshot(show_toast=True, from_timer=True)
        else:
            self.status.config(
                text=self._tr("skip_window").format(
                    now.strftime("%H:%M"),
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                )
            )
        self._schedule_next()

    def _screenshot_now(self):
        self._persist()
        self._do_screenshot(show_toast=False, from_timer=False)

    def _do_screenshot(self, show_toast, from_timer=False):
        folder = self._require_save_folder(silent=from_timer)
        if folder is None:
            return
        self._start_prescreenshot_countdown(folder, show_toast)

    def _capture_after_hidden(self, folder, show_toast):
        if not self.root.winfo_exists():
            return
        path = None
        err = None
        try:
            path = take_screenshot(folder)
        except Exception as e:
            err = e
        finally:
            try:
                self.root.deiconify()
                self.root.lift()
            except tk.TclError:
                pass

        if err is not None:
            self.status.config(text=self._tr("capture_fail").format(err))
            if show_toast:
                self._show_toast(self._tr("toast_fail"))
            return

        short = os.path.basename(path)
        self.status.config(text=self._tr("last_time").format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.last_path.config(text=path)
        self._play_capture_sound()
        if show_toast:
            self._show_toast(self._tr("toast_done").format(short))

    def _show_toast(self, message):
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        f = tk.Frame(toast, bg="#2d2d2d", padx=16, pady=12)
        f.pack(fill=tk.BOTH, expand=True)
        tk.Label(
            f,
            text=self._tr("toast_title"),
            fg="#ffffff",
            bg="#2d2d2d",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor=tk.W)
        tk.Label(
            f,
            text=message,
            fg="#e0e0e0",
            bg="#2d2d2d",
            font=("Segoe UI", 10),
            wraplength=320,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(4, 0))

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        toast.update_idletasks()
        w = toast.winfo_reqwidth()
        h = toast.winfo_reqheight()
        x = sw - w - 24
        y = sh - h - 72
        toast.geometry("+{0}+{1}".format(x, y))
        toast.after(4500, toast.destroy)

    def _quit(self):
        self._cancel_prescreenshot_countdown()
        self._persist()
        if self._job is not None:
            self.root.after_cancel(self._job)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    App().run()


if __name__ == "__main__":
    main()
