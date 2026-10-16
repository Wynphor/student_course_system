# 说明：启用延迟类型注解，提升类型提示在不同 Python 版本下的兼容性。
from __future__ import annotations

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import math
import random
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import tkinter as tk
from pathlib import Path
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from .db import DB_PATH, initialize_database
from .pixel_assets import ensure_assets
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
from .services import (
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    AuthService,
    CourseService,
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    EnrollmentService,
    ServiceError,
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    SettingsService,
    StudentService,
)

# 说明：开始异常捕获，避免底层错误直接中断程序。
try:
    # 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
    from PIL import Image, ImageTk
# 说明：捕获异常并转换为业务提示或测试结果。
except ImportError:  # pragma: no cover - runtime fallback
    # 说明：给 Image 赋值，保存当前步骤需要继续使用的数据。
    Image = None
    # 说明：把 Pillow 图片转换为 Tkinter 可显示对象。
    ImageTk = None


# 说明：给 THEME 赋值，保存当前步骤需要继续使用的数据。
THEME = {
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "bg": "#0b102f",
    "surface": "#fff9f0",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "panel": "#f6fbff",
    "header": "#10184a",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "header_2": "#1d2b72",
    "nav": "#121a4f",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "nav_hover": "#24327f",
    "border": "#050819",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "text": "#111535",
    "muted": "#4c5272",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "pink": "#ff66ad",
    "pink_light": "#ffd6ea",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "blue": "#4fc3ff",
    "blue_light": "#dff6ff",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "cream": "#fff7d6",
    "yellow": "#fff06a",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "green": "#6ef37a",
    "orange": "#ffb347",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "purple": "#a675ff",
    "ok": "#1b8c72",
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    "warning": "#a04467",
}

# 说明：给 FONT_UI 赋值，保存当前步骤需要继续使用的数据。
FONT_UI = ("Microsoft YaHei UI", 10)
# 说明：给 FONT_UI_BOLD 赋值，保存当前步骤需要继续使用的数据。
FONT_UI_BOLD = ("Microsoft YaHei UI", 10, "bold")
# 说明：给 FONT_TITLE 赋值，保存当前步骤需要继续使用的数据。
FONT_TITLE = ("Microsoft YaHei UI", 15, "bold")
# 说明：给 FONT_PIXEL 赋值，保存当前步骤需要继续使用的数据。
FONT_PIXEL = ("Consolas", 11, "bold")
# 说明：给 FONT_PIXEL_BIG 赋值，保存当前步骤需要继续使用的数据。
FONT_PIXEL_BIG = ("Consolas", 18, "bold")


# 说明：GIF 动画播放类，用 Tkinter 原生 PhotoImage 按帧播放。
class AnimatedGif:
    # 说明：加载 Tkinter 可显示的图片素材。
    """用 Tkinter 原生 PhotoImage 播放 GIF，避免为动效引入复杂 GUI 框架。"""

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, root: tk.Misc, label: tk.Label, path: Path | None, subsample: int = 1, delay: int = 80) -> None:
        # 说明：保存或更新 self.root 状态，供界面事件、页面刷新或权限判断继续使用。
        self.root = root
        # 说明：保存或更新 self.label 状态，供界面事件、页面刷新或权限判断继续使用。
        self.label = label
        # 说明：保存或更新 self.delay 状态，供界面事件、页面刷新或权限判断继续使用。
        self.delay = delay
        # 说明：创建或配置 Tkinter 界面对象。
        self.frames: list[tk.PhotoImage] = []
        # 说明：保存或更新 self.index 状态，供界面事件、页面刷新或权限判断继续使用。
        self.index = 0
        # 说明：保存或更新 self._job: str | None 状态，供界面事件、页面刷新或权限判断继续使用。
        self._job: str | None = None
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if path is not None and path.exists():
            # 说明：保存或更新 self.frames 状态，供界面事件、页面刷新或权限判断继续使用。
            self.frames = self._load_frames(path, max(1, subsample))

    # 说明：定义 _load_frames 函数，封装当前模块的一段处理逻辑。
    def _load_frames(self, path: Path, subsample: int) -> list[tk.PhotoImage]:
        # 说明：创建或配置 Tkinter 界面对象。
        frames: list[tk.PhotoImage] = []
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for frame_index in range(80):
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：创建或配置 Tkinter 界面对象。
                frame = tk.PhotoImage(file=str(path), format=f"gif -index {frame_index}")
            except tk.TclError:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                break
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if subsample > 1:
                # 说明：给 frame 赋值，保存当前步骤需要继续使用的数据。
                frame = frame.subsample(subsample, subsample)
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            frames.append(frame)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if frames:
            # 说明：返回处理结果，供调用方继续使用。
            return frames
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：创建或配置 Tkinter 界面对象。
            frame = tk.PhotoImage(file=str(path))
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if subsample > 1:
                # 说明：给 frame 赋值，保存当前步骤需要继续使用的数据。
                frame = frame.subsample(subsample, subsample)
            # 说明：返回处理结果，供调用方继续使用。
            return [frame]
        # 说明：创建或配置 Tkinter 界面对象。
        except tk.TclError:
            # 说明：返回处理结果，供调用方继续使用。
            return []

    # 说明：定义 start 函数，封装当前模块的一段处理逻辑。
    def start(self) -> bool:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.frames:
            # 说明：返回处理结果，供调用方继续使用。
            return False
        # 说明：保存或更新 self.label.configure(image 状态，供界面事件、页面刷新或权限判断继续使用。
        self.label.configure(image=self.frames[0])
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._tick()
        # 说明：返回处理结果，供调用方继续使用。
        return True

    # 说明：定义 stop 函数，封装当前模块的一段处理逻辑。
    def stop(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self._job is not None:
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：取消定时回调，避免界面切换后旧动画继续运行。
                self.root.after_cancel(self._job)
            # 说明：创建或配置 Tkinter 界面对象。
            except tk.TclError:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                pass
            # 说明：保存或更新 self._job 状态，供界面事件、页面刷新或权限判断继续使用。
            self._job = None

    # 说明：定义 _tick 函数，封装当前模块的一段处理逻辑。
    def _tick(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.frames or not self.label.winfo_exists():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：保存或更新 self.label.configure(image 状态，供界面事件、页面刷新或权限判断继续使用。
        self.label.configure(image=self.frames[self.index])
        # 说明：保存或更新 self.index 状态，供界面事件、页面刷新或权限判断继续使用。
        self.index = (self.index + 1) % len(self.frames)
        # 说明：注册定时回调，驱动动画循环或延迟任务。
        self._job = self.root.after(self.delay, self._tick)


# 说明：登录页彩虹猫动态背景类。
class NyanVirusBackground:
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """登录页背景动画：星空、彩虹尾迹和循环飞行的 Nyan Cat。"""

    # 说明：给 RAINBOW 赋值，保存当前步骤需要继续使用的数据。
    RAINBOW = ["#ff4040", "#ff9f2a", "#fff15a", "#55e565", "#4fc3ff", "#a675ff"]

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, canvas: tk.Canvas, asset_path: Path | None) -> None:
        # 说明：保存或更新 self.canvas 状态，供界面事件、页面刷新或权限判断继续使用。
        self.canvas = canvas
        # 说明：保存或更新 self.asset_path 状态，供界面事件、页面刷新或权限判断继续使用。
        self.asset_path = asset_path
        # 说明：保存或更新 self.window_item: int | None 状态，供界面事件、页面刷新或权限判断继续使用。
        self.window_item: int | None = None
        # 说明：保存或更新 self.frames 状态，供界面事件、页面刷新或权限判断继续使用。
        self.frames = self._load_sprite_frames(asset_path)
        # 说明：保存或更新 self.frame_index 状态，供界面事件、页面刷新或权限判断继续使用。
        self.frame_index = 0
        # 说明：保存或更新 self._job: str | None 状态，供界面事件、页面刷新或权限判断继续使用。
        self._job: str | None = None
        # 说明：保存或更新 self.stars 状态，供界面事件、页面刷新或权限判断继续使用。
        self.stars = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            (random.random(), random.random(), random.choice((2, 3)), random.choice(("#ffffff", "#fff06a", "#4fc3ff")))
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for _ in range(64)
        ]
        # 说明：保存或更新 self.sprites 状态，供界面事件、页面刷新或权限判断继续使用。
        self.sprites = [self._new_sprite(-index * 180) for index in range(5)]

    # 说明：定义 _load_sprite_frames 函数，封装当前模块的一段处理逻辑。
    def _load_sprite_frames(self, path: Path | None) -> list[tk.PhotoImage]:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if path is None or not path.exists():
            # 说明：返回处理结果，供调用方继续使用。
            return []
        # 说明：创建或配置 Tkinter 界面对象。
        frames: list[tk.PhotoImage] = []
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for frame_index in range(24):
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：创建或配置 Tkinter 界面对象。
                frame = tk.PhotoImage(file=str(path), format=f"gif -index {frame_index}").subsample(5, 5)
            except tk.TclError:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                break
            frames.append(frame)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if frames:
            # 说明：返回处理结果，供调用方继续使用。
            return frames
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：创建或配置 Tkinter 界面对象。
            return [tk.PhotoImage(file=str(path)).subsample(5, 5)]
        except tk.TclError:
            # 说明：返回处理结果，供调用方继续使用。
            return []

    # 说明：定义 _new_sprite 函数，封装当前模块的一段处理逻辑。
    def _new_sprite(self, x: float | None = None) -> dict[str, float]:
        # 说明：返回处理结果，供调用方继续使用。
        return {
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "x": float(x if x is not None else random.randint(-520, -80)),
            "y": float(random.randint(36, 320)),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "speed": random.uniform(2.2, 4.6),
            "wave": random.uniform(0, math.pi * 2),
        }

    # 说明：定义 start 函数，封装当前模块的一段处理逻辑。
    def start(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._tick()

    # 说明：定义 stop 函数，封装当前模块的一段处理逻辑。
    def stop(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self._job is not None:
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：取消定时回调，避免界面切换后旧动画继续运行。
                self.canvas.after_cancel(self._job)
            # 说明：创建或配置 Tkinter 界面对象。
            except tk.TclError:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                pass
            # 说明：保存或更新 self._job 状态，供界面事件、页面刷新或权限判断继续使用。
            self._job = None

    # 说明：定义 _tick 函数，封装当前模块的一段处理逻辑。
    def _tick(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.canvas.winfo_exists():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：给 width 赋值，保存当前步骤需要继续使用的数据。
        width = max(self.canvas.winfo_width(), 680)
        # 说明：给 height 赋值，保存当前步骤需要继续使用的数据。
        height = max(self.canvas.winfo_height(), 420)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.canvas.delete("virus")
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for rx, ry, size, color in self.stars:
            # 说明：给 x 赋值，保存当前步骤需要继续使用的数据。
            x = int(rx * width)
            # 说明：给 y 赋值，保存当前步骤需要继续使用的数据。
            y = int(ry * height)
            # 说明：保存或更新 self.canvas.create_rectangle(x, y, x + size, y + size, fill 状态，供界面事件、页面刷新或权限判断继续使用。
            self.canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="", tags="virus")
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for sprite in self.sprites:
            # 说明：给 sprite["x"] + 赋值，保存当前步骤需要继续使用的数据。
            sprite["x"] += sprite["speed"]
            # 说明：给 sprite["wave"] + 赋值，保存当前步骤需要继续使用的数据。
            sprite["wave"] += 0.12
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if sprite["x"] > width + 80:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                sprite.update(self._new_sprite())
                # 说明：给 sprite["y"] 赋值，保存当前步骤需要继续使用的数据。
                sprite["y"] = random.randint(26, max(70, height - 80))
            # 说明：给 x 赋值，保存当前步骤需要继续使用的数据。
            x = sprite["x"]
            # 说明：给 y 赋值，保存当前步骤需要继续使用的数据。
            y = sprite["y"] + math.sin(sprite["wave"]) * 8
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for row, color in enumerate(self.RAINBOW):
                # 说明：给 yy 赋值，保存当前步骤需要继续使用的数据。
                yy = y + 8 + row * 4
                # 说明：保存或更新 self.canvas.create_rectangle(x - 132, yy, x - 8, yy + 3, fill 状态，供界面事件、页面刷新或权限判断继续使用。
                self.canvas.create_rectangle(x - 132, yy, x - 8, yy + 3, fill=color, outline="", tags="virus")
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if self.frames:
                # 说明：保存或更新 self.canvas.create_image(x, y, image 状态，供界面事件、页面刷新或权限判断继续使用。
                self.canvas.create_image(x, y, image=self.frames[self.frame_index], anchor="nw", tags="virus")
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            else:
                # 说明：保存或更新 self.canvas.create_rectangle(x, y, x + 44, y + 26, fill 状态，供界面事件、页面刷新或权限判断继续使用。
                self.canvas.create_rectangle(x, y, x + 44, y + 26, fill=THEME["pink"], outline=THEME["border"], tags="virus")
                # 说明：保存或更新 self.canvas.create_rectangle(x + 34, y - 4, x + 58, y + 18, fill 状态，供界面事件、页面刷新或权限判断继续使用。
                self.canvas.create_rectangle(x + 34, y - 4, x + 58, y + 18, fill="#999999", outline=THEME["border"], tags="virus")
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self.frames:
            # 说明：保存或更新 self.frame_index 状态，供界面事件、页面刷新或权限判断继续使用。
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self.window_item is not None:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.canvas.tag_raise(self.window_item)
        # 说明：注册定时回调，驱动动画循环或延迟任务。
        self._job = self.canvas.after(70, self._tick)


# 说明：点击烟花粒子效果类。
class PixelFirework:
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """点击反馈动效，使用独立透明顶层窗口绘制短暂像素粒子。"""

    # 说明：给 COLORS 赋值，保存当前步骤需要继续使用的数据。
    COLORS = ["#ff4040", "#ff9f2a", "#fff15a", "#55e565", "#4fc3ff", "#a675ff", "#ff66ad"]

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, root: tk.Tk, x_root: int, y_root: int) -> None:
        # 说明：保存或更新 self.root 状态，供界面事件、页面刷新或权限判断继续使用。
        self.root = root
        # 说明：保存或更新 self.size 状态，供界面事件、页面刷新或权限判断继续使用。
        self.size = 126
        # 说明：保存或更新 self.life 状态，供界面事件、页面刷新或权限判断继续使用。
        self.life = 18
        # 说明：创建或配置 Tkinter 界面对象。
        self.top = tk.Toplevel(root)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.top.overrideredirect(True)
        self.top.geometry(f"{self.size}x{self.size}+{x_root - self.size // 2}+{y_root - self.size // 2}")
        # 说明：给 transparent 赋值，保存当前步骤需要继续使用的数据。
        transparent = "#010203"
        # 说明：保存或更新 self.top.configure(bg 状态，供界面事件、页面刷新或权限判断继续使用。
        self.top.configure(bg=transparent)
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.top.attributes("-transparentcolor", transparent)
            self.top.attributes("-topmost", True)
        # 说明：创建或配置 Tkinter 界面对象。
        except tk.TclError:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            pass
        # 说明：创建或配置 Tkinter 界面对象。
        self.canvas = tk.Canvas(self.top, width=self.size, height=self.size, bg=transparent, highlightthickness=0)
        # 说明：使用 pack 布局管理器摆放控件。
        self.canvas.pack(fill="both", expand=True)
        # 说明：保存或更新 self.particles: list[dict[str, float | str]] 状态，供界面事件、页面刷新或权限判断继续使用。
        self.particles: list[dict[str, float | str]] = []
        # 说明：给 count 赋值，保存当前步骤需要继续使用的数据。
        count = random.randint(12, 18)
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for index in range(count):
            # 说明：给 angle 赋值，保存当前步骤需要继续使用的数据。
            angle = math.tau * index / count + random.uniform(-0.14, 0.14)
            # 说明：给 speed 赋值，保存当前步骤需要继续使用的数据。
            speed = random.uniform(2.0, 4.8)
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.particles.append(
                {
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    "x": self.size / 2,
                    "y": self.size / 2,
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    "color": random.choice(self.COLORS),
                }
            )
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._tick()

    # 说明：定义 _tick 函数，封装当前模块的一段处理逻辑。
    def _tick(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.top.winfo_exists():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        self.canvas.delete("particle")
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for particle in self.particles:
            # 说明：给 particle["x"] 赋值，保存当前步骤需要继续使用的数据。
            particle["x"] = float(particle["x"]) + float(particle["vx"])
            # 说明：给 particle["y"] 赋值，保存当前步骤需要继续使用的数据。
            particle["y"] = float(particle["y"]) + float(particle["vy"])
            # 说明：给 particle["vy"] 赋值，保存当前步骤需要继续使用的数据。
            particle["vy"] = float(particle["vy"]) + 0.18
            # 说明：给 block 赋值，保存当前步骤需要继续使用的数据。
            block = 5 if self.life > 9 else 3
            # 说明：给 x 赋值，保存当前步骤需要继续使用的数据。
            x = float(particle["x"])
            # 说明：给 y 赋值，保存当前步骤需要继续使用的数据。
            y = float(particle["y"])
            # 说明：保存或更新 self.canvas.create_rectangle(x, y, x + block, y + block, fill 状态，供界面事件、页面刷新或权限判断继续使用。
            self.canvas.create_rectangle(x, y, x + block, y + block, fill=str(particle["color"]), outline="", tags="particle")
        # 说明：保存或更新 self.life - 状态，供界面事件、页面刷新或权限判断继续使用。
        self.life -= 1
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self.life <= 0:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.top.destroy()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        else:
            # 说明：注册定时回调，驱动动画循环或延迟任务。
            self.top.after(28, self._tick)


# 说明：侧边栏看板娘组件类。
class KanbanMascot(tk.Frame):
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """侧边栏看板娘组件；安装 Pillow 时会随鼠标轻微转向。"""

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, parent: tk.Misc, path: Path | None) -> None:
        # 说明：给 super().__init__(parent, bg 赋值，保存当前步骤需要继续使用的数据。
        super().__init__(parent, bg=THEME["nav"], width=168, height=150)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.pack_propagate(False)
        # 说明：创建或配置 Tkinter 界面对象。
        self.label = tk.Label(self, bg=THEME["nav"], borderwidth=0)
        # 说明：使用 pack 布局管理器摆放控件。
        self.label.pack(expand=True)
        # 说明：保存或更新 self.base_image: Any | None 状态，供界面事件、页面刷新或权限判断继续使用。
        self.base_image: Any | None = None
        # 说明：保存或更新 self.photo: Any | None 状态，供界面事件、页面刷新或权限判断继续使用。
        self.photo: Any | None = None
        # 说明：保存或更新 self.current_angle 状态，供界面事件、页面刷新或权限判断继续使用。
        self.current_angle = 0
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._load(path)

    # 说明：定义 _load 函数，封装当前模块的一段处理逻辑。
    def _load(self, path: Path | None) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if path is None or not path.exists():
            # 说明：保存或更新 self.label.configure(text 状态，供界面事件、页面刷新或权限判断继续使用。
            self.label.configure(text="[KANBAN]", fg=THEME["yellow"], font=FONT_PIXEL)
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：把 Pillow 图片转换为 Tkinter 可显示对象。
        if Image is not None and ImageTk is not None:
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：给 image 赋值，保存当前步骤需要继续使用的数据。
                image = Image.open(path).convert("RGBA")
                # 说明：给 width, height 赋值，保存当前步骤需要继续使用的数据。
                width, height = image.size
                # 说明：根据条件选择不同处理分支，控制程序执行路径。
                if width > height * 2:
                    # 说明：给 image 赋值，保存当前步骤需要继续使用的数据。
                    image = image.crop((0, 0, height, height))
                # 说明：给 resampling 赋值，保存当前步骤需要继续使用的数据。
                resampling = getattr(Image, "Resampling", Image).LANCZOS if max(width, height) > 256 else getattr(Image, "Resampling", Image).NEAREST
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                image.thumbnail((124, 136), resampling)
                # 说明：保存或更新 self.base_image 状态，供界面事件、页面刷新或权限判断继续使用。
                self.base_image = image
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._set_angle(0)
                return
            # 说明：捕获异常并转换为业务提示或测试结果。
            except Exception:
                # 说明：保存或更新 self.base_image 状态，供界面事件、页面刷新或权限判断继续使用。
                self.base_image = None
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：创建或配置 Tkinter 界面对象。
            photo = tk.PhotoImage(file=str(path))
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            while photo.width() > 138 or photo.height() > 142:
                # 说明：给 photo 赋值，保存当前步骤需要继续使用的数据。
                photo = photo.subsample(2, 2)
            # 说明：保存或更新 self.photo 状态，供界面事件、页面刷新或权限判断继续使用。
            self.photo = photo
            # 说明：保存或更新 self.label.configure(image 状态，供界面事件、页面刷新或权限判断继续使用。
            self.label.configure(image=self.photo)
        # 说明：创建或配置 Tkinter 界面对象。
        except tk.TclError:
            # 说明：保存或更新 self.label.configure(text 状态，供界面事件、页面刷新或权限判断继续使用。
            self.label.configure(text="[KANBAN]", fg=THEME["yellow"], font=FONT_PIXEL)

    # 说明：定义 _set_angle 函数，封装当前模块的一段处理逻辑。
    def _set_angle(self, angle: int) -> None:
        # 说明：把 Pillow 图片转换为 Tkinter 可显示对象。
        if self.base_image is None or ImageTk is None:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：给 resampling 赋值，保存当前步骤需要继续使用的数据。
        resampling = getattr(Image, "Resampling", Image).BICUBIC
        # 说明：给 rotated 赋值，保存当前步骤需要继续使用的数据。
        rotated = self.base_image.rotate(angle, resample=resampling, expand=True)
        # 说明：加载 Tkinter 可显示的图片素材。
        self.photo = ImageTk.PhotoImage(rotated)
        # 说明：保存或更新 self.label.configure(image 状态，供界面事件、页面刷新或权限判断继续使用。
        self.label.configure(image=self.photo)
        # 说明：保存或更新 self.current_angle 状态，供界面事件、页面刷新或权限判断继续使用。
        self.current_angle = angle

    # 说明：定义 follow_pointer 函数，封装当前模块的一段处理逻辑。
    def follow_pointer(self, x_root: int) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self.base_image is None:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：给 center 赋值，保存当前步骤需要继续使用的数据。
        center = self.winfo_rootx() + max(1, self.winfo_width()) / 2
        # 说明：给 angle 赋值，保存当前步骤需要继续使用的数据。
        angle = int(max(-10, min(10, (x_root - center) / 32)))
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if abs(angle - self.current_angle) >= 2:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self._set_angle(angle)


# 说明：系统主窗口类，整合登录、菜单、页面和交互逻辑。
class ElectiveCourseApp(tk.Tk):
    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        super().__init__()
        # UI 启动时再次初始化数据库，便于直接双击 main.py 运行。
        initialize_database(DB_PATH)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.title("学生选修课程系统")
        self.geometry("420x280")
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.minsize(420, 280)

        # 说明：保存或更新 self.course_service 状态，供界面事件、页面刷新或权限判断继续使用。
        self.course_service = CourseService(DB_PATH)
        # 说明：保存或更新 self.student_service 状态，供界面事件、页面刷新或权限判断继续使用。
        self.student_service = StudentService(DB_PATH)
        # 说明：保存或更新 self.enrollment_service 状态，供界面事件、页面刷新或权限判断继续使用。
        self.enrollment_service = EnrollmentService(DB_PATH)
        # 说明：保存或更新 self.settings_service 状态，供界面事件、页面刷新或权限判断继续使用。
        self.settings_service = SettingsService(DB_PATH)
        # 说明：保存或更新 self.auth_service 状态，供界面事件、页面刷新或权限判断继续使用。
        self.auth_service = AuthService(DB_PATH)

        # 说明：保存或更新 self._student_options: dict[str, str] 状态，供界面事件、页面刷新或权限判断继续使用。
        self._student_options: dict[str, str] = {}
        # 说明：创建或配置 Tkinter 界面对象。
        self._current_student_id = tk.StringVar()
        self.status_text = tk.StringVar(value="系统就绪")
        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
        self.current_user: dict[str, Any] | None = None
        # 说明：创建或配置 Tkinter 界面对象。
        self.header_user_text = tk.StringVar(value="")
        # 说明：检查并准备本地素材，素材缺失时自动生成占位图。
        self.asset_paths = ensure_assets()
        # 保存图片和动画对象引用，避免被 Tkinter 垃圾回收导致图片不显示。
        self._images: dict[str, tk.PhotoImage] = {}
        # 说明：保存或更新 self._gif_players: list[AnimatedGif] 状态，供界面事件、页面刷新或权限判断继续使用。
        self._gif_players: list[AnimatedGif] = []
        # 说明：保存或更新 self._login_background: NyanVirusBackground | None 状态，供界面事件、页面刷新或权限判断继续使用。
        self._login_background: NyanVirusBackground | None = None
        # 说明：保存或更新 self._kanban: KanbanMascot | None 状态，供界面事件、页面刷新或权限判断继续使用。
        self._kanban: KanbanMascot | None = None

        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._setup_style()
        # 说明：绑定全局事件，用于鼠标点击烟花和看板娘跟随等交互。
        self.bind_all("<Button-1>", self._show_click_firework, add="+")
        self.bind_all("<Motion>", self._track_pointer, add="+")
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.show_login()

    # 说明：定义 _setup_style 函数，封装当前模块的一段处理逻辑。
    def _setup_style(self) -> None:
        # 说明：创建或配置 Tkinter 界面对象。
        style = ttk.Style(self)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if "clam" in style.theme_names():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            style.theme_use("clam")
        # 说明：保存或更新 self.configure(bg 状态，供界面事件、页面刷新或权限判断继续使用。
        self.configure(bg=THEME["bg"])
        # 说明：给 style.configure(".", font 赋值，保存当前步骤需要继续使用的数据。
        style.configure(".", font=FONT_UI, background=THEME["bg"], foreground=THEME["text"])
        # 说明：给 style.configure("TFrame", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("TFrame", background=THEME["bg"])
        # 说明：给 style.configure("TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("TLabel", background=THEME["surface"], foreground=THEME["text"], font=FONT_UI)
        # 说明：给 style.configure("Panel.TFrame", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Panel.TFrame", background=THEME["surface"])
        # 说明：给 style.configure("Header.TFrame", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Header.TFrame", background=THEME["header"])
        # 说明：给 style.configure("Header.TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Header.TLabel", background=THEME["header"], foreground=THEME["cream"], font=FONT_TITLE)
        # 说明：给 style.configure("HeaderSub.TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("HeaderSub.TLabel", background=THEME["header"], foreground=THEME["yellow"], font=FONT_PIXEL)
        # 说明：给 style.configure("Nav.TFrame", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Nav.TFrame", background=THEME["nav"])
        # 说明：给 style.configure("Content.TFrame", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Content.TFrame", background=THEME["surface"])
        # 说明：给 style.configure("Toolbar.TFrame", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Toolbar.TFrame", background=THEME["surface"])
        # 说明：给 style.configure("Pixel.TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Pixel.TLabel", background=THEME["surface"], foreground=THEME["text"], font=FONT_UI)
        # 说明：给 style.configure("Hint.TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Hint.TLabel", background=THEME["surface"], foreground=THEME["muted"], font=("Microsoft YaHei UI", 9))
        # 说明：给 style.configure("LoginTitle.TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("LoginTitle.TLabel", background=THEME["surface"], foreground=THEME["header"], font=FONT_TITLE)
        # 说明：给 style.configure("PageTitle.TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("PageTitle.TLabel", background=THEME["surface"], foreground=THEME["header"], font=FONT_TITLE)
        # 说明：给 style.configure("Mascot.TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Mascot.TLabel", background=THEME["nav"], foreground=THEME["yellow"], font=FONT_PIXEL)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        style.configure(
            "TButton",
            # 说明：给 font 赋值，保存当前步骤需要继续使用的数据。
            font=FONT_UI_BOLD,
            # 说明：给 padding 赋值，保存当前步骤需要继续使用的数据。
            padding=(12, 6),
            # 说明：给 background 赋值，保存当前步骤需要继续使用的数据。
            background=THEME["blue_light"],
            # 说明：给 foreground 赋值，保存当前步骤需要继续使用的数据。
            foreground=THEME["text"],
            # 说明：给 bordercolor 赋值，保存当前步骤需要继续使用的数据。
            bordercolor=THEME["border"],
            # 说明：给 lightcolor 赋值，保存当前步骤需要继续使用的数据。
            lightcolor=THEME["cream"],
            # 说明：给 darkcolor 赋值，保存当前步骤需要继续使用的数据。
            darkcolor=THEME["border"],
            # 说明：给 focuscolor 赋值，保存当前步骤需要继续使用的数据。
            focuscolor=THEME["pink"],
        )
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        style.map(
            "TButton",
            # 说明：给 background 赋值，保存当前步骤需要继续使用的数据。
            background=[("active", THEME["yellow"]), ("pressed", THEME["pink"]), ("disabled", "#e8dfe8")],
            # 说明：给 foreground 赋值，保存当前步骤需要继续使用的数据。
            foreground=[("disabled", "#8f8497")],
        )
        # 说明：给 style.configure("Nav.TButton", anchor 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Nav.TButton", anchor="w", padding=(12, 9), background=THEME["header_2"], foreground=THEME["cream"])
        # 说明：给 style.map("Nav.TButton", background 赋值，保存当前步骤需要继续使用的数据。
        style.map("Nav.TButton", background=[("active", THEME["nav_hover"]), ("pressed", THEME["pink"])])
        # 说明：给 style.configure("Accent.TButton", padding 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Accent.TButton", padding=(12, 6), background=THEME["pink"], foreground=THEME["text"])
        # 说明：给 style.map("Accent.TButton", background 赋值，保存当前步骤需要继续使用的数据。
        style.map("Accent.TButton", background=[("active", THEME["pink_light"]), ("pressed", THEME["blue_light"])])
        # 说明：给 style.configure("TEntry", fieldbackground 赋值，保存当前步骤需要继续使用的数据。
        style.configure("TEntry", fieldbackground="#ffffff", bordercolor=THEME["border"], lightcolor=THEME["blue"])
        # 说明：给 style.configure("TCombobox", fieldbackground 赋值，保存当前步骤需要继续使用的数据。
        style.configure("TCombobox", fieldbackground="#ffffff", bordercolor=THEME["border"], arrowcolor=THEME["header"])
        # 说明：给 style.configure("Treeview", rowheight 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Treeview", rowheight=29, font=FONT_UI, background="#ffffff", fieldbackground="#ffffff", foreground=THEME["text"])
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        style.configure(
            "Treeview.Heading",
            # 说明：给 font 赋值，保存当前步骤需要继续使用的数据。
            font=FONT_UI_BOLD,
            # 说明：给 background 赋值，保存当前步骤需要继续使用的数据。
            background=THEME["yellow"],
            # 说明：给 foreground 赋值，保存当前步骤需要继续使用的数据。
            foreground=THEME["header"],
            # 说明：给 bordercolor 赋值，保存当前步骤需要继续使用的数据。
            bordercolor=THEME["border"],
        )
        # 说明：给 style.map("Treeview", background 赋值，保存当前步骤需要继续使用的数据。
        style.map("Treeview", background=[("selected", THEME["blue_light"])], foreground=[("selected", THEME["header"])])
        # 说明：给 style.configure("Status.TLabel", background 赋值，保存当前步骤需要继续使用的数据。
        style.configure("Status.TLabel", background=THEME["header"], foreground=THEME["cream"], font=FONT_PIXEL)

    # 说明：定义 _stop_dynamic_effects 函数，封装当前模块的一段处理逻辑。
    def _stop_dynamic_effects(self) -> None:
        # 登录页、主页之间切换时停止旧动画，避免 after 回调重复运行。
        if self._login_background is not None:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self._login_background.stop()
            # 说明：保存或更新 self._login_background 状态，供界面事件、页面刷新或权限判断继续使用。
            self._login_background = None
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for player in self._gif_players:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            player.stop()
        self._gif_players.clear()
        # 说明：保存或更新 self._kanban 状态，供界面事件、页面刷新或权限判断继续使用。
        self._kanban = None

    # 说明：定义 _start_gif 函数，封装当前模块的一段处理逻辑。
    def _start_gif(self, label: tk.Label, path: Path | None, subsample: int = 1, delay: int = 80) -> bool:
        # 说明：给 player 赋值，保存当前步骤需要继续使用的数据。
        player = AnimatedGif(self, label, path, subsample=subsample, delay=delay)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if player.start():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self._gif_players.append(player)
            # 说明：返回处理结果，供调用方继续使用。
            return True
        return False

    # 说明：定义 _show_click_firework 函数，封装当前模块的一段处理逻辑。
    def _show_click_firework(self, event: tk.Event) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.winfo_exists():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            PixelFirework(self, event.x_root, event.y_root)
        # 说明：创建或配置 Tkinter 界面对象。
        except tk.TclError:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            pass

    # 说明：定义 _track_pointer 函数，封装当前模块的一段处理逻辑。
    def _track_pointer(self, event: tk.Event) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self._kanban is not None and self._kanban.winfo_exists():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self._kanban.follow_pointer(event.x_root)

    # 说明：根据当前用户角色生成顶部菜单。
    def _build_menu(self) -> None:
        # 说明：创建或配置 Tkinter 界面对象。
        menu_bar = tk.Menu(self)
        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
        role = self.current_user["role"] if self.current_user else ""

        # 菜单根据账号角色动态生成，学生账号只能看到本人相关功能。
        file_menu = tk.Menu(menu_bar, tearoff=False)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if role == "admin":
            # 说明：给 file_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
            file_menu.add_command(label="导出课程表", command=self.export_courses)
            file_menu.add_command(label="导出选课表", command=self.export_enrollments)
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            file_menu.add_separator()
        # 说明：给 file_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
        file_menu.add_command(label="退出登录", command=self.logout)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        file_menu.add_separator()
        # 说明：给 file_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
        file_menu.add_command(label="退出", command=self.destroy)
        # 说明：给 menu_bar.add_cascade(label 赋值，保存当前步骤需要继续使用的数据。
        menu_bar.add_cascade(label="文件", menu=file_menu)

        # 说明：创建或配置 Tkinter 界面对象。
        manage_menu = tk.Menu(menu_bar, tearoff=False)
        # 说明：给 manage_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
        manage_menu.add_command(label="课程信息管理" if role == "admin" else "课程浏览", command=self.show_courses)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if role == "admin":
            # 说明：给 manage_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
            manage_menu.add_command(label="学生信息管理", command=self.show_students)
            manage_menu.add_command(label="学生选课管理", command=self.show_enrollment)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        else:
            # 说明：给 manage_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
            manage_menu.add_command(label="我的选课", command=self.show_enrollment)
        # 说明：给 menu_bar.add_cascade(label 赋值，保存当前步骤需要继续使用的数据。
        menu_bar.add_cascade(label="管理", menu=manage_menu)

        # 说明：创建或配置 Tkinter 界面对象。
        query_menu = tk.Menu(menu_bar, tearoff=False)
        # 说明：给 query_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
        query_menu.add_command(label="课程查询", command=self.show_courses)
        query_menu.add_command(label="学分统计" if role == "admin" else "我的学分", command=self.show_statistics)
        # 说明：给 menu_bar.add_cascade(label 赋值，保存当前步骤需要继续使用的数据。
        menu_bar.add_cascade(label="查询统计", menu=query_menu)

        # 说明：创建或配置 Tkinter 界面对象。
        system_menu = tk.Menu(menu_bar, tearoff=False)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if role == "admin":
            # 说明：给 system_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
            system_menu.add_command(label="系统设置", command=self.show_settings)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        else:
            # 说明：给 system_menu.add_command(label 赋值，保存当前步骤需要继续使用的数据。
            system_menu.add_command(label="修改密码", command=self.open_change_password_dialog)
        system_menu.add_command(label="关于", command=self.show_about)
        # 说明：给 menu_bar.add_cascade(label 赋值，保存当前步骤需要继续使用的数据。
        menu_bar.add_cascade(label="系统", menu=system_menu)
        # 说明：保存或更新 self.config(menu 状态，供界面事件、页面刷新或权限判断继续使用。
        self.config(menu=menu_bar)

    # 说明：构建主界面的顶部栏、左侧导航、内容区和状态栏。
    def _build_layout(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._stop_dynamic_effects()
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for child in self.winfo_children():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            child.destroy()
        # 说明：保存或更新 self.configure(bg 状态，供界面事件、页面刷新或权限判断继续使用。
        self.configure(bg=THEME["bg"])
        # 说明：创建或配置 Tkinter 界面对象。
        header = ttk.Frame(self, style="Header.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        header.pack(fill="x")
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(header, text="学生选修课程系统", style="Header.TLabel").pack(side="left", padx=18, pady=(10, 3))
        ttk.Label(header, text="NYAN CAMPUS ELECTIVE SYS", style="HeaderSub.TLabel").pack(side="left", padx=(8, 0), pady=(13, 3))
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(header, text="退出登录", command=self.logout).pack(side="right", padx=(6, 18), pady=(8, 6))
        ttk.Label(
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            header,
            # 说明：给 textvariable 赋值，保存当前步骤需要继续使用的数据。
            textvariable=self.header_user_text,
            # 说明：给 style 赋值，保存当前步骤需要继续使用的数据。
            style="HeaderSub.TLabel",
        # 说明：使用 pack 布局管理器摆放控件。
        ).pack(side="right", padx=(0, 8), pady=(13, 3))

        # 说明：创建或配置 Tkinter 界面对象。
        body = ttk.Frame(self)
        # 说明：使用 pack 布局管理器摆放控件。
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # 说明：创建或配置 Tkinter 界面对象。
        nav_shell = tk.Frame(body, bg=THEME["border"], padx=3, pady=3)
        # 说明：使用 pack 布局管理器摆放控件。
        nav_shell.pack(side="left", fill="y", padx=(0, 8), pady=0)
        # 说明：创建或配置 Tkinter 界面对象。
        nav = ttk.Frame(nav_shell, width=186, style="Nav.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        nav.pack(fill="y", expand=True)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        nav.pack_propagate(False)

        # 说明：创建或配置 Tkinter 界面对象。
        mascot_label = tk.Label(nav, bg=THEME["nav"], borderwidth=0)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self._start_gif(mascot_label, self.asset_paths.get("sidebar"), subsample=3, delay=80):
            # 说明：使用 pack 布局管理器摆放控件。
            mascot_label.pack(pady=(12, 4))
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        else:
            # 说明：给 mascot 赋值，保存当前步骤需要继续使用的数据。
            mascot = self._load_image("sidebar")
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if mascot is not None:
                # 说明：给 mascot_label.configure(image 赋值，保存当前步骤需要继续使用的数据。
                mascot_label.configure(image=mascot)
                # 说明：使用 pack 布局管理器摆放控件。
                mascot_label.pack(pady=(12, 4))
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            else:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                mascot_label.destroy()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not mascot_label.winfo_exists():
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Label(nav, text="[NYAN CAT]", style="Mascot.TLabel").pack(pady=(14, 8))
        ttk.Label(nav, text="NYAN MENU", style="Mascot.TLabel").pack(pady=(0, 10))

        # 左侧导航与顶部菜单保持同一套权限规则。
        if self.is_admin:
            # 说明：给 nav_items 赋值，保存当前步骤需要继续使用的数据。
            nav_items = [
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                ("课程信息管理", self.show_courses),
                ("学生信息管理", self.show_students),
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                ("学生选课管理", self.show_enrollment),
                ("学分统计", self.show_statistics),
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                ("系统设置", self.show_settings),
            ]
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        else:
            # 说明：给 nav_items 赋值，保存当前步骤需要继续使用的数据。
            nav_items = [
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                ("课程浏览", self.show_courses),
                ("我的选课", self.show_enrollment),
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                ("我的学分", self.show_statistics),
                ("修改密码", self.open_change_password_dialog),
            ]
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for text, command in nav_items:
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Button(nav, text=f"> {text}", style="Nav.TButton", command=command).pack(fill="x", padx=9, pady=4)
        ttk.Button(nav, text="> 退出登录", style="Nav.TButton", command=self.logout).pack(fill="x", padx=9, pady=(12, 4))

        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(nav, text="RAINBOW LOCAL MODE", style="Mascot.TLabel").pack(side="bottom", pady=12)
        # 说明：保存或更新 self._kanban 状态，供界面事件、页面刷新或权限判断继续使用。
        self._kanban = KanbanMascot(nav, self.asset_paths.get("kanban"))
        # 说明：使用 pack 布局管理器摆放控件。
        self._kanban.pack(side="bottom", padx=8, pady=(4, 2), fill="x")

        # 说明：创建或配置 Tkinter 界面对象。
        main_shell = tk.Frame(body, bg=THEME["border"], padx=3, pady=3)
        # 说明：使用 pack 布局管理器摆放控件。
        main_shell.pack(side="left", fill="both", expand=True)
        # 说明：创建或配置 Tkinter 界面对象。
        main_area = ttk.Frame(main_shell, style="Content.TFrame", padding=12)
        # 说明：使用 pack 布局管理器摆放控件。
        main_area.pack(fill="both", expand=True)
        # 说明：创建或配置 Tkinter 界面对象。
        self.page_title = ttk.Label(main_area, text="", style="PageTitle.TLabel")
        # 说明：使用 pack 布局管理器摆放控件。
        self.page_title.pack(anchor="w", pady=(0, 8))

        # 说明：创建或配置 Tkinter 界面对象。
        self.content = ttk.Frame(main_area, style="Content.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        self.content.pack(fill="both", expand=True)

        # 说明：创建或配置 Tkinter 界面对象。
        status = ttk.Label(self, textvariable=self.status_text, style="Status.TLabel", anchor="w")
        # 说明：使用 pack 布局管理器摆放控件。
        status.pack(fill="x", side="bottom", ipady=5)

    # 说明：装饰器用于给下一行函数或属性添加额外行为。
    @property
    def is_admin(self) -> bool:
        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
        return bool(self.current_user and self.current_user["role"] == "admin")

    # 说明：定义 _load_image 函数，封装当前模块的一段处理逻辑。
    def _load_image(self, name: str) -> tk.PhotoImage | None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if name in self._images:
            # 说明：返回处理结果，供调用方继续使用。
            return self._images[name]
        # 说明：给 path 赋值，保存当前步骤需要继续使用的数据。
        path = self.asset_paths.get(name)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if path is None or not path.exists():
            # 说明：返回处理结果，供调用方继续使用。
            return None
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：创建或配置 Tkinter 界面对象。
            image = tk.PhotoImage(file=str(path))
        except tk.TclError:
            # 说明：返回处理结果，供调用方继续使用。
            return None
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if name == "sidebar" and image.width() > 170:
            # 说明：给 image 赋值，保存当前步骤需要继续使用的数据。
            image = image.subsample(3, 3)
        # 说明：保存或更新 self._images[name] 状态，供界面事件、页面刷新或权限判断继续使用。
        self._images[name] = image
        # 说明：返回处理结果，供调用方继续使用。
        return image

    # 说明：构建登录界面并处理登录事件。
    def show_login(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._stop_dynamic_effects()
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for child in self.winfo_children():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            child.destroy()
        # 说明：创建或配置 Tkinter 界面对象。
        self.config(menu=tk.Menu(self))
        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
        self.current_user = None
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.title("学生选修课程系统 - 登录")
        self.geometry("680x420")
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.minsize(680, 420)
        # 说明：保存或更新 self.configure(bg 状态，供界面事件、页面刷新或权限判断继续使用。
        self.configure(bg=THEME["bg"])
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.deiconify()

        # 登录页使用 Canvas 承载动态背景，登录表单仍放在普通 Frame 中保证输入稳定。
        outer = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        # 说明：使用 pack 布局管理器摆放控件。
        outer.pack(fill="both", expand=True)
        # 说明：保存或更新 self._login_background 状态，供界面事件、页面刷新或权限判断继续使用。
        self._login_background = NyanVirusBackground(outer, self.asset_paths.get("source", self.asset_paths.get("login")))

        # 说明：创建或配置 Tkinter 界面对象。
        shell = tk.Frame(outer, bg=THEME["border"], padx=4, pady=4)
        # 说明：给 shell_window 赋值，保存当前步骤需要继续使用的数据。
        shell_window = outer.create_window(0, 0, window=shell, anchor="center")

        # 说明：定义 place_login_panel 函数，封装当前模块的一段处理逻辑。
        def place_login_panel(event: tk.Event | None = None) -> None:
            # 说明：给 width 赋值，保存当前步骤需要继续使用的数据。
            width = outer.winfo_width() if event is None else event.width
            # 说明：给 height 赋值，保存当前步骤需要继续使用的数据。
            height = outer.winfo_height() if event is None else event.height
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            outer.coords(shell_window, max(340, width // 2), max(210, height // 2))

        # 说明：绑定控件事件，使用户操作能够触发回调函数。
        outer.bind("<Configure>", place_login_panel)
        # 说明：保存或更新 self._login_background.window_item 状态，供界面事件、页面刷新或权限判断继续使用。
        self._login_background.window_item = shell_window
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._login_background.start()

        # 说明：创建或配置 Tkinter 界面对象。
        panel = ttk.Frame(shell, padding=20, style="Panel.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        panel.pack()

        # 说明：创建或配置 Tkinter 界面对象。
        left = ttk.Frame(panel, style="Panel.TFrame")
        # 说明：使用 grid 网格布局管理器摆放控件。
        left.grid(row=0, column=0, rowspan=6, padx=(0, 22), sticky="n")
        # 说明：创建或配置 Tkinter 界面对象。
        login_label = tk.Label(left, bg=THEME["surface"], borderwidth=0)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if self._start_gif(login_label, self.asset_paths.get("login"), delay=80):
            # 说明：使用 pack 布局管理器摆放控件。
            login_label.pack(pady=(0, 8))
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        else:
            # 说明：给 login_mascot 赋值，保存当前步骤需要继续使用的数据。
            login_mascot = self._load_image("login")
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if login_mascot is not None:
                # 说明：给 login_label.configure(image 赋值，保存当前步骤需要继续使用的数据。
                login_label.configure(image=login_mascot)
                # 说明：使用 pack 布局管理器摆放控件。
                login_label.pack(pady=(0, 8))
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            else:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                login_label.destroy()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not login_label.winfo_exists():
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Label(left, text="[NYAN CAT]", style="LoginTitle.TLabel").pack(pady=(12, 20))
        ttk.Label(left, text="RAINBOW TRAIL LOGIN", style="Hint.TLabel").pack()
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(left, text="OFFLINE COURSE SYS", style="Hint.TLabel").pack()

        right = ttk.Frame(panel, style="Panel.TFrame")
        # 说明：使用 grid 网格布局管理器摆放控件。
        right.grid(row=0, column=1, sticky="n")
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(right, text="学生选修课程系统", style="LoginTitle.TLabel").grid(
            # 说明：给 row 赋值，保存当前步骤需要继续使用的数据。
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(right, text="NYAN CAMPUS LOGIN", style="Hint.TLabel").grid(
            # 说明：给 row 赋值，保存当前步骤需要继续使用的数据。
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 16)
        )

        # 说明：创建或配置 Tkinter 界面对象。
        username_var = tk.StringVar(value="admin")
        password_var = tk.StringVar(value="")
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(right, text="用户名", style="Pixel.TLabel").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=7)
        username_entry = ttk.Entry(right, textvariable=username_var, width=24)
        # 说明：使用 grid 网格布局管理器摆放控件。
        username_entry.grid(row=2, column=1, sticky="w", pady=7)
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(right, text="密码", style="Pixel.TLabel").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=7)
        password_entry = ttk.Entry(right, textvariable=password_var, width=24, show="*")
        # 说明：使用 grid 网格布局管理器摆放控件。
        password_entry.grid(row=3, column=1, sticky="w", pady=7)
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(right, text="管理员：admin / 123456；学生：学号 / 学号", style="Hint.TLabel").grid(
            # 说明：给 row 赋值，保存当前步骤需要继续使用的数据。
            row=4, column=0, columnspan=2, pady=(4, 14), sticky="w"
        )

        # 说明：定义 do_login 函数，封装当前模块的一段处理逻辑。
        def do_login() -> None:
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                self.current_user = self.auth_service.login(username_var.get(), password_var.get())
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showerror("登录失败", str(exc), parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            self.start_session()

        # 说明：创建或配置 Tkinter 界面对象。
        buttons = ttk.Frame(right, style="Panel.TFrame")
        # 说明：使用 grid 网格布局管理器摆放控件。
        buttons.grid(row=5, column=0, columnspan=2, sticky="w")
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(buttons, text="登录", style="Accent.TButton", command=do_login).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="退出", command=self.destroy).pack(side="left", padx=6)
        # 说明：绑定控件事件，使用户操作能够触发回调函数。
        self.bind("<Return>", lambda _event: do_login())
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        username_entry.focus_set()

    # 说明：登录成功后构建主界面并跳转到默认页面。
    def start_session(self) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.unbind("<Return>")
        # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
        role_name = "管理员" if self.is_admin else "学生"
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.title(f"学生选修课程系统 - {role_name}")
        self.geometry("1120x720")
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.minsize(960, 620)
        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
        self.header_user_text.set(f"NYAN READY > {role_name}：{self.current_user['display_name']}")
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self._build_menu()
        self._build_layout()
        # 管理员默认进入课程管理，学生默认进入本人选课页。
        self.show_courses() if self.is_admin else self.show_enrollment()

    # 说明：退出当前账号并返回登录界面。
    def logout(self) -> None:
        # 说明：弹出提示、错误、确认或结果信息。
        if not messagebox.askyesno("退出登录", "确定退出当前账号吗？", parent=self):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 清空当前会话并回到登录界面，方便演示时切换管理员和学生账号。
        self.current_user = None
        # 说明：创建或配置 Tkinter 界面对象。
        self.config(menu=tk.Menu(self))
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.show_login()

    # 说明：定义 require_admin 函数，封装当前模块的一段处理逻辑。
    def require_admin(self) -> bool:
        # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
        if self.is_admin:
            # 说明：返回处理结果，供调用方继续使用。
            return True
        # 说明：弹出提示、错误、确认或结果信息。
        messagebox.showwarning("权限不足", "当前账号无权执行该操作", parent=self)
        # 说明：返回处理结果，供调用方继续使用。
        return False

    # 说明：定义 _set_page 函数，封装当前模块的一段处理逻辑。
    def _set_page(self, title: str) -> None:
        # 说明：保存或更新 self.page_title.config(text 状态，供界面事件、页面刷新或权限判断继续使用。
        self.page_title.config(text=title)
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for child in self.content.winfo_children():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            child.destroy()
        self.status_text.set(f"NYAN READY > {title}")

    # 说明：创建带勾选列、滚动条和统一列配置的表格。
    def _make_table(self, parent: ttk.Frame, columns: list[tuple[str, str, int]]) -> ttk.Treeview:
        # 说明：创建或配置 Tkinter 界面对象。
        frame = ttk.Frame(parent, style="Content.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        frame.pack(fill="both", expand=True)

        # 每个表格统一加一列勾选框，供批量删除、批量选课和批量退课复用。
        table_columns = [("_checked", "选择", 48), *columns]
        # 说明：创建或配置 Tkinter 界面对象。
        tree = ttk.Treeview(frame, columns=[col[0] for col in table_columns], show="headings", selectmode="browse")
        # 说明：给 tree._data_columns 赋值，保存当前步骤需要继续使用的数据。
        tree._data_columns = [col[0] for col in columns]  # type: ignore[attr-defined]
        # 说明：构造包含勾选列的表格列配置，用于批量操作。
        for key, title, width in table_columns:
            # 说明：给 tree.heading(key, text 赋值，保存当前步骤需要继续使用的数据。
            tree.heading(key, text=title)
            # 说明：给 tree.column(key, width 赋值，保存当前步骤需要继续使用的数据。
            tree.column(key, width=width, anchor="center")
        # 说明：给 tree.column("_checked", width 赋值，保存当前步骤需要继续使用的数据。
        tree.column("_checked", width=48, minwidth=48, stretch=False)
        # 说明：绑定控件事件，使用户操作能够触发回调函数。
        tree.bind("<Button-1>", self._handle_table_check_click, add="+")

        # 说明：创建或配置 Tkinter 界面对象。
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        # 说明：给 tree.configure(yscrollcommand 赋值，保存当前步骤需要继续使用的数据。
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # 说明：使用 grid 网格布局管理器摆放控件。
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        # 说明：使用 grid 网格布局管理器摆放控件。
        x_scroll.grid(row=1, column=0, sticky="ew")
        # 说明：给 frame.columnconfigure(0, weight 赋值，保存当前步骤需要继续使用的数据。
        frame.columnconfigure(0, weight=1)
        # 说明：给 frame.rowconfigure(0, weight 赋值，保存当前步骤需要继续使用的数据。
        frame.rowconfigure(0, weight=1)
        # 说明：返回处理结果，供调用方继续使用。
        return tree

    # 说明：定义 _selected_values 函数，封装当前模块的一段处理逻辑。
    def _selected_values(self, tree: ttk.Treeview) -> dict[str, Any] | None:
        # 说明：给 selected 赋值，保存当前步骤需要继续使用的数据。
        selected = tree.selection()
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not selected:
            # 说明：返回处理结果，供调用方继续使用。
            return None
        # 说明：给 values 赋值，保存当前步骤需要继续使用的数据。
        values = tree.item(selected[0], "values")
        # 说明：返回处理结果，供调用方继续使用。
        return self._row_values(tree, values)

    # 说明：定义 _selected_values_list 函数，封装当前模块的一段处理逻辑。
    def _selected_values_list(self, tree: ttk.Treeview) -> list[dict[str, Any]]:
        # 说明：给 rows: list[dict[str, Any]] 赋值，保存当前步骤需要继续使用的数据。
        rows: list[dict[str, Any]] = []
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for item_id in tree.get_children():
            # 说明：给 values 赋值，保存当前步骤需要继续使用的数据。
            values = tree.item(item_id, "values")
            # 说明：切换表格勾选状态，实现多选功能。
            if values and values[0] == "☑":
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                rows.append(self._row_values(tree, values))
        # 说明：返回处理结果，供调用方继续使用。
        return rows

    # 说明：定义 _row_values 函数，封装当前模块的一段处理逻辑。
    def _row_values(self, tree: ttk.Treeview, values: tuple[Any, ...] | list[Any]) -> dict[str, Any]:
        # 说明：给 data_columns 赋值，保存当前步骤需要继续使用的数据。
        data_columns = getattr(tree, "_data_columns", [column for column in tree["columns"] if column != "_checked"])
        # 说明：给 offset 赋值，保存当前步骤需要继续使用的数据。
        offset = 1 if "_checked" in tree["columns"] else 0
        # 说明：返回处理结果，供调用方继续使用。
        return {column: values[index + offset] for index, column in enumerate(data_columns)}

    # 说明：定义 _insert_table_row 函数，封装当前模块的一段处理逻辑。
    def _insert_table_row(self, tree: ttk.Treeview, values: list[Any]) -> str:
        # 说明：返回处理结果，供调用方继续使用。
        return tree.insert("", "end", values=["☐", *values])

    # 说明：处理表格勾选列点击，实现批量操作选择状态切换。
    def _handle_table_check_click(self, event: tk.Event) -> None:
        # 说明：给 tree 赋值，保存当前步骤需要继续使用的数据。
        tree = event.widget
        # 说明：创建或配置 Tkinter 界面对象。
        if not isinstance(tree, ttk.Treeview):
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if tree.identify_region(event.x, event.y) != "cell":
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if tree.identify_column(event.x) != "#1":
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：给 item_id 赋值，保存当前步骤需要继续使用的数据。
        item_id = tree.identify_row(event.y)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not item_id:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        tree.selection_set(item_id)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        tree.focus(item_id)
        # 说明：给 values 赋值，保存当前步骤需要继续使用的数据。
        values = list(tree.item(item_id, "values"))
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not values:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # Treeview 没有原生复选框，用“☐/☑”文本模拟勾选状态。
        values[0] = "☐" if values[0] == "☑" else "☑"
        # 说明：给 tree.item(item_id, values 赋值，保存当前步骤需要继续使用的数据。
        tree.item(item_id, values=values)

    # 说明：定义 _show_error 函数，封装当前模块的一段处理逻辑。
    def _show_error(self, error: Exception) -> None:
        # 说明：弹出提示、错误、确认或结果信息。
        messagebox.showerror("操作失败", str(error), parent=self)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        self.status_text.set(f"NYAN ERROR > {error}")

    # 说明：定义 _ask_save_path 函数，封装当前模块的一段处理逻辑。
    def _ask_save_path(self, default_name: str) -> str | None:
        # 说明：返回处理结果，供调用方继续使用。
        return filedialog.asksaveasfilename(
            # 说明：给 parent 赋值，保存当前步骤需要继续使用的数据。
            parent=self,
            # 说明：给 title 赋值，保存当前步骤需要继续使用的数据。
            title="保存导出文件",
            # 说明：给 defaultextension 赋值，保存当前步骤需要继续使用的数据。
            defaultextension=".csv",
            # 说明：给 initialfile 赋值，保存当前步骤需要继续使用的数据。
            initialfile=default_name,
            # 说明：给 filetypes 赋值，保存当前步骤需要继续使用的数据。
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
        )

    # 说明：显示课程管理或课程浏览页面。
    def show_courses(self) -> None:
        # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
        self._set_page("课程信息管理" if self.is_admin else "课程浏览")

        # 说明：创建或配置 Tkinter 界面对象。
        toolbar = ttk.Frame(self.content, style="Toolbar.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        toolbar.pack(fill="x", pady=(0, 8))
        # 说明：创建或配置 Tkinter 界面对象。
        keyword_var = tk.StringVar()
        type_var = tk.StringVar()
        # 说明：创建或配置 Tkinter 界面对象。
        min_var = tk.StringVar()
        max_var = tk.StringVar()
        # 说明：创建或配置 Tkinter 界面对象。
        semester_var = tk.StringVar()

        ttk.Label(toolbar, text="关键字").pack(side="left", padx=(0, 4))
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Entry(toolbar, textvariable=keyword_var, width=16).pack(side="left", padx=(0, 8))
        ttk.Label(toolbar, text="课程性质").pack(side="left", padx=(0, 4))
        # 说明：创建或配置 Tkinter 界面对象。
        type_box = ttk.Combobox(toolbar, textvariable=type_var, width=12)
        # 说明：使用 pack 布局管理器摆放控件。
        type_box.pack(side="left", padx=(0, 8))
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(toolbar, text="学分").pack(side="left", padx=(0, 4))
        ttk.Entry(toolbar, textvariable=min_var, width=6).pack(side="left")
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(toolbar, text="至").pack(side="left", padx=3)
        ttk.Entry(toolbar, textvariable=max_var, width=6).pack(side="left", padx=(0, 8))
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(toolbar, text="学期").pack(side="left", padx=(0, 4))
        semester_box = ttk.Combobox(toolbar, textvariable=semester_var, width=10)
        # 说明：使用 pack 布局管理器摆放控件。
        semester_box.pack(side="left", padx=(0, 8))

        # 说明：给 columns 赋值，保存当前步骤需要继续使用的数据。
        columns = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("course_code", "课程编号", 90),
            ("course_name", "课程名称", 150),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("course_type", "课程性质", 100),
            ("total_hours", "总学时", 70),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("lecture_hours", "授课学时", 80),
            ("practice_hours", "实验/上机", 80),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("credits", "学分", 60),
            ("semester", "开课学期", 90),
        ]
        # 说明：给 table 赋值，保存当前步骤需要继续使用的数据。
        table = self._make_table(self.content, columns)

        # 说明：定义 refresh 函数，封装当前模块的一段处理逻辑。
        def refresh() -> None:
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 查询条件来自工具栏，支持名称关键字、课程性质、学期和学分区间组合筛选。
                type_box["values"] = [""] + self.course_service.distinct_values("course_type")
                # 说明：给 semester_box["values"] 赋值，保存当前步骤需要继续使用的数据。
                semester_box["values"] = [""] + self.course_service.distinct_values("semester")
                # 说明：给 rows 赋值，保存当前步骤需要继续使用的数据。
                rows = self.course_service.list_courses(
                    {
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        "keyword": keyword_var.get(),
                        "course_type": type_var.get(),
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        "min_credits": min_var.get(),
                        "max_credits": max_var.get(),
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        "semester": semester_var.get(),
                    }
                )
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                table.delete(*table.get_children())
                # 说明：循环处理多条记录、多个控件或多个动画粒子。
                for row in rows:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self._insert_table_row(table, [row[key] for key, _, _ in columns])
                self.status_text.set(f"NYAN READY > 课程信息管理：共 {len(rows)} 条课程记录")
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._show_error(exc)

        # 说明：定义 reset 函数，封装当前模块的一段处理逻辑。
        def reset() -> None:
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for var in (keyword_var, type_var, min_var, max_var, semester_var):
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                var.set("")
            refresh()

        # 说明：定义 edit_selected 函数，封装当前模块的一段处理逻辑。
        def edit_selected() -> None:
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not self.require_admin():
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 selected 赋值，保存当前步骤需要继续使用的数据。
            selected = self._selected_values(table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not selected:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择一条课程记录", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 course 赋值，保存当前步骤需要继续使用的数据。
            course = self.course_service.get_course(selected["course_code"])
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if course:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self.open_course_dialog(course, refresh)

        # 说明：定义 delete_selected 函数，封装当前模块的一段处理逻辑。
        def delete_selected() -> None:
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not self.require_admin():
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 selected 赋值，保存当前步骤需要继续使用的数据。
            selected = self._selected_values(table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not selected:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择一条课程记录", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：弹出提示、错误、确认或结果信息。
            if messagebox.askyesno("确认删除", f"确定删除课程 {selected['course_code']} 吗？", parent=self):
                # 说明：开始异常捕获，避免底层错误直接中断程序。
                try:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self.course_service.delete_course(selected["course_code"])
                    refresh()
                # 说明：捕获异常并转换为业务提示或测试结果。
                except ServiceError as exc:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self._show_error(exc)

        # 说明：定义 delete_many_selected 函数，封装当前模块的一段处理逻辑。
        def delete_many_selected() -> None:
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not self.require_admin():
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 rows 赋值，保存当前步骤需要继续使用的数据。
            rows = self._selected_values_list(table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not rows:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择要批量删除的课程记录", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 codes 赋值，保存当前步骤需要继续使用的数据。
            codes = [row["course_code"] for row in rows]
            # 说明：弹出提示、错误、确认或结果信息。
            if messagebox.askyesno("批量删除课程", f"确定删除选中的 {len(codes)} 门课程吗？相关选课记录也会同步删除。", parent=self):
                # 说明：开始异常捕获，避免底层错误直接中断程序。
                try:
                    # 说明：给 count 赋值，保存当前步骤需要继续使用的数据。
                    count = self.course_service.delete_courses(codes)
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    refresh()
                    self.status_text.set(f"NYAN READY > 已批量删除 {count} 门课程")
                # 说明：捕获异常并转换为业务提示或测试结果。
                except ServiceError as exc:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self._show_error(exc)

        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(toolbar, text="查询", command=refresh).pack(side="left", padx=3)
        ttk.Button(toolbar, text="重置", command=reset).pack(side="left", padx=3)
        # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
        if self.is_admin:
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Button(toolbar, text="新增", command=lambda: self.open_course_dialog(None, refresh)).pack(side="left", padx=(14, 3))
            ttk.Button(toolbar, text="编辑", command=edit_selected).pack(side="left", padx=3)
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Button(toolbar, text="删除", command=delete_selected).pack(side="left", padx=3)
            ttk.Button(toolbar, text="批量删除", command=delete_many_selected).pack(side="left", padx=3)
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Button(toolbar, text="导出", command=self.export_courses).pack(side="left", padx=3)

        # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
        if self.is_admin:
            # 说明：绑定控件事件，使用户操作能够触发回调函数。
            table.bind("<Double-1>", lambda _event: edit_selected())
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        refresh()

    # 说明：定义 open_course_dialog 函数，封装当前模块的一段处理逻辑。
    def open_course_dialog(self, course: dict[str, Any] | None, refresh: Callable[[], None]) -> None:
        # 说明：创建或配置 Tkinter 界面对象。
        dialog = tk.Toplevel(self)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.title("编辑课程" if course else "新增课程")
        dialog.geometry("390x390")
        # 说明：给 dialog.configure(bg 赋值，保存当前步骤需要继续使用的数据。
        dialog.configure(bg=THEME["bg"])
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.resizable(False, False)
        dialog.transient(self)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.grab_set()

        # 说明：给 fields 赋值，保存当前步骤需要继续使用的数据。
        fields = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("course_code", "课程编号"),
            ("course_name", "课程名称"),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("course_type", "课程性质"),
            ("total_hours", "总学时"),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("lecture_hours", "授课学时"),
            ("practice_hours", "实验或上机学时"),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("credits", "学分"),
            ("semester", "开课学期"),
        ]
        # 说明：创建或配置 Tkinter 界面对象。
        vars_map: dict[str, tk.StringVar] = {}
        form = ttk.Frame(dialog, padding=16, style="Panel.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        form.pack(fill="both", expand=True)
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for row_index, (key, label) in enumerate(fields):
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Label(form, text=label).grid(row=row_index, column=0, sticky="e", padx=(0, 8), pady=6)
            # 说明：给 value 赋值，保存当前步骤需要继续使用的数据。
            value = "" if course is None else str(course[key])
            # 说明：创建或配置 Tkinter 界面对象。
            var = tk.StringVar(value=value)
            # 说明：给 vars_map[key] 赋值，保存当前步骤需要继续使用的数据。
            vars_map[key] = var
            # 说明：创建或配置 Tkinter 界面对象。
            entry = ttk.Entry(form, textvariable=var, width=26)
            # 说明：使用 grid 网格布局管理器摆放控件。
            entry.grid(row=row_index, column=1, sticky="w", pady=6)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if key == "course_code" and course is not None:
                # 说明：给 entry.config(state 赋值，保存当前步骤需要继续使用的数据。
                entry.config(state="disabled")

        # 说明：创建或配置 Tkinter 界面对象。
        buttons = ttk.Frame(form)
        # 说明：使用 grid 网格布局管理器摆放控件。
        buttons.grid(row=len(fields), column=0, columnspan=2, pady=(14, 0))

        # 说明：定义 save 函数，封装当前模块的一段处理逻辑。
        def save() -> None:
            # 说明：给 data 赋值，保存当前步骤需要继续使用的数据。
            data = {key: var.get() for key, var in vars_map.items()}
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：根据条件选择不同处理分支，控制程序执行路径。
                if course is None:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self.course_service.create_course(data)
                # 说明：根据条件选择不同处理分支，控制程序执行路径。
                else:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self.course_service.update_course(course["course_code"], data)
                dialog.destroy()
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                refresh()
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showerror("保存失败", str(exc), parent=dialog)

        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(buttons, text="保存", command=save).pack(side="left", padx=6)
        ttk.Button(buttons, text="取消", command=dialog.destroy).pack(side="left", padx=6)
        # 说明：给 form.columnconfigure(1, weight 赋值，保存当前步骤需要继续使用的数据。
        form.columnconfigure(1, weight=1)

    # 说明：显示学生管理页面，只允许管理员访问。
    def show_students(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.require_admin():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 学生管理只开放给管理员，新增学生时服务层会同步创建学生登录账号。
        self._set_page("学生信息管理")
        # 说明：创建或配置 Tkinter 界面对象。
        toolbar = ttk.Frame(self.content, style="Toolbar.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        toolbar.pack(fill="x", pady=(0, 8))
        # 说明：创建或配置 Tkinter 界面对象。
        keyword_var = tk.StringVar()
        ttk.Label(toolbar, text="关键字").pack(side="left", padx=(0, 4))
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Entry(toolbar, textvariable=keyword_var, width=22).pack(side="left", padx=(0, 8))

        # 说明：给 columns 赋值，保存当前步骤需要继续使用的数据。
        columns = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("student_id", "学号", 110),
            ("name", "姓名", 90),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("class_name", "班级", 120),
            ("major", "专业", 180),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("phone", "联系电话", 130),
        ]
        # 说明：给 table 赋值，保存当前步骤需要继续使用的数据。
        table = self._make_table(self.content, columns)

        # 说明：定义 refresh 函数，封装当前模块的一段处理逻辑。
        def refresh() -> None:
            # 说明：给 rows 赋值，保存当前步骤需要继续使用的数据。
            rows = self.student_service.list_students(keyword_var.get())
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            table.delete(*table.get_children())
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for row in rows:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._insert_table_row(table, [row[key] for key, _, _ in columns])
            self.status_text.set(f"NYAN READY > 学生信息管理：共 {len(rows)} 条学生记录")

        # 说明：定义 edit_selected 函数，封装当前模块的一段处理逻辑。
        def edit_selected() -> None:
            # 说明：给 selected 赋值，保存当前步骤需要继续使用的数据。
            selected = self._selected_values(table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not selected:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择一条学生记录", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 student 赋值，保存当前步骤需要继续使用的数据。
            student = self.student_service.get_student(selected["student_id"])
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if student:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self.open_student_dialog(student, refresh)

        # 说明：定义 delete_selected 函数，封装当前模块的一段处理逻辑。
        def delete_selected() -> None:
            # 说明：给 selected 赋值，保存当前步骤需要继续使用的数据。
            selected = self._selected_values(table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not selected:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择一条学生记录", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：弹出提示、错误、确认或结果信息。
            if messagebox.askyesno("确认删除", f"确定删除学生 {selected['student_id']} 吗？", parent=self):
                # 说明：开始异常捕获，避免底层错误直接中断程序。
                try:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self.student_service.delete_student(selected["student_id"])
                    refresh()
                # 说明：捕获异常并转换为业务提示或测试结果。
                except ServiceError as exc:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self._show_error(exc)

        # 说明：定义 delete_many_selected 函数，封装当前模块的一段处理逻辑。
        def delete_many_selected() -> None:
            # 说明：给 rows 赋值，保存当前步骤需要继续使用的数据。
            rows = self._selected_values_list(table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not rows:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择要批量删除的学生记录", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 student_ids 赋值，保存当前步骤需要继续使用的数据。
            student_ids = [row["student_id"] for row in rows]
            # 说明：弹出提示、错误、确认或结果信息。
            if messagebox.askyesno("批量删除学生", f"确定删除选中的 {len(student_ids)} 名学生吗？学生账号和选课记录也会同步删除。", parent=self):
                # 说明：开始异常捕获，避免底层错误直接中断程序。
                try:
                    # 说明：给 count 赋值，保存当前步骤需要继续使用的数据。
                    count = self.student_service.delete_students(student_ids)
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    refresh()
                    self.status_text.set(f"NYAN READY > 已批量删除 {count} 名学生")
                # 说明：捕获异常并转换为业务提示或测试结果。
                except ServiceError as exc:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self._show_error(exc)

        # 说明：定义 reset_password 函数，封装当前模块的一段处理逻辑。
        def reset_password() -> None:
            # 说明：给 selected 赋值，保存当前步骤需要继续使用的数据。
            selected = self._selected_values(table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not selected:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择一条学生记录", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：弹出提示、错误、确认或结果信息。
            if not messagebox.askyesno(
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                "重置密码",
                f"确定将学生 {selected['student_id']} 的登录密码重置为学号吗？",
                # 说明：给 parent 赋值，保存当前步骤需要继续使用的数据。
                parent=self,
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ):
                return
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self.auth_service.reset_student_password(selected["student_id"])
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showinfo("重置成功", f"学生账号 {selected['student_id']} 的密码已重置为学号。", parent=self)
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._show_error(exc)

        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(toolbar, text="查询", command=refresh).pack(side="left", padx=3)
        ttk.Button(toolbar, text="重置", command=lambda: (keyword_var.set(""), refresh())).pack(side="left", padx=3)
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(toolbar, text="新增", command=lambda: self.open_student_dialog(None, refresh)).pack(side="left", padx=(14, 3))
        ttk.Button(toolbar, text="编辑", command=edit_selected).pack(side="left", padx=3)
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(toolbar, text="删除", command=delete_selected).pack(side="left", padx=3)
        ttk.Button(toolbar, text="批量删除", command=delete_many_selected).pack(side="left", padx=3)
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(toolbar, text="重置密码", command=reset_password).pack(side="left", padx=3)

        # 说明：绑定控件事件，使用户操作能够触发回调函数。
        table.bind("<Double-1>", lambda _event: edit_selected())
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        refresh()

    # 说明：定义 open_student_dialog 函数，封装当前模块的一段处理逻辑。
    def open_student_dialog(self, student: dict[str, Any] | None, refresh: Callable[[], None]) -> None:
        # 说明：创建或配置 Tkinter 界面对象。
        dialog = tk.Toplevel(self)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.title("编辑学生" if student else "新增学生")
        dialog.geometry("380x300")
        # 说明：给 dialog.configure(bg 赋值，保存当前步骤需要继续使用的数据。
        dialog.configure(bg=THEME["bg"])
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.resizable(False, False)
        dialog.transient(self)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.grab_set()

        # 说明：给 fields 赋值，保存当前步骤需要继续使用的数据。
        fields = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("student_id", "学号"),
            ("name", "姓名"),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("class_name", "班级"),
            ("major", "专业"),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("phone", "联系电话"),
        ]
        # 说明：创建或配置 Tkinter 界面对象。
        vars_map: dict[str, tk.StringVar] = {}
        form = ttk.Frame(dialog, padding=16, style="Panel.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        form.pack(fill="both", expand=True)
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for row_index, (key, label) in enumerate(fields):
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Label(form, text=label).grid(row=row_index, column=0, sticky="e", padx=(0, 8), pady=7)
            # 说明：给 value 赋值，保存当前步骤需要继续使用的数据。
            value = "" if student is None else str(student[key])
            # 说明：创建或配置 Tkinter 界面对象。
            var = tk.StringVar(value=value)
            # 说明：给 vars_map[key] 赋值，保存当前步骤需要继续使用的数据。
            vars_map[key] = var
            # 说明：创建或配置 Tkinter 界面对象。
            entry = ttk.Entry(form, textvariable=var, width=26)
            # 说明：使用 grid 网格布局管理器摆放控件。
            entry.grid(row=row_index, column=1, sticky="w", pady=7)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if key == "student_id" and student is not None:
                # 说明：给 entry.config(state 赋值，保存当前步骤需要继续使用的数据。
                entry.config(state="disabled")

        # 说明：创建或配置 Tkinter 界面对象。
        buttons = ttk.Frame(form)
        # 说明：使用 grid 网格布局管理器摆放控件。
        buttons.grid(row=len(fields), column=0, columnspan=2, pady=(14, 0))

        # 说明：定义 save 函数，封装当前模块的一段处理逻辑。
        def save() -> None:
            # 说明：给 data 赋值，保存当前步骤需要继续使用的数据。
            data = {key: var.get() for key, var in vars_map.items()}
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：根据条件选择不同处理分支，控制程序执行路径。
                if student is None:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self.student_service.create_student(data)
                # 说明：根据条件选择不同处理分支，控制程序执行路径。
                else:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self.student_service.update_student(student["student_id"], data)
                dialog.destroy()
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                refresh()
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showerror("保存失败", str(exc), parent=dialog)

        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(buttons, text="保存", command=save).pack(side="left", padx=6)
        ttk.Button(buttons, text="取消", command=dialog.destroy).pack(side="left", padx=6)

    # 说明：显示选课页面，管理员可代选，学生只能操作本人课程。
    def show_enrollment(self) -> None:
        # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
        self._set_page("学生选课管理" if self.is_admin else "我的选课")
        # 说明：创建或配置 Tkinter 界面对象。
        top = ttk.Frame(self.content, style="Toolbar.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        top.pack(fill="x", pady=(0, 8))
        # 说明：创建或配置 Tkinter 界面对象。
        student_box: ttk.Combobox | None = None
        # 管理员可代学生选课；学生模式固定为当前登录学号，不显示学生下拉框。
        if self.is_admin:
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Label(top, text="选择学生").pack(side="left", padx=(0, 6))
            student_box = ttk.Combobox(top, textvariable=self._current_student_id, width=32, state="readonly")
            # 说明：使用 pack 布局管理器摆放控件。
            student_box.pack(side="left", padx=(0, 10))
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        else:
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Label(
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                top,
                # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                text=f"当前学生：{self.current_user['student_id']} - {self.current_user['display_name']}",
            # 说明：使用 pack 布局管理器摆放控件。
            ).pack(side="left", padx=(0, 10))
        # 说明：创建或配置 Tkinter 界面对象。
        summary_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=summary_var).pack(side="left", padx=12)

        # 说明：创建或配置 Tkinter 界面对象。
        tables = ttk.Panedwindow(self.content, orient="horizontal")
        # 说明：使用 pack 布局管理器摆放控件。
        tables.pack(fill="both", expand=True)

        # 说明：创建或配置 Tkinter 界面对象。
        left = ttk.Frame(tables, padding=(0, 0, 6, 0), style="Content.TFrame")
        right = ttk.Frame(tables, padding=(6, 0, 0, 0), style="Content.TFrame")
        # 说明：给 tables.add(left, weight 赋值，保存当前步骤需要继续使用的数据。
        tables.add(left, weight=1)
        # 说明：给 tables.add(right, weight 赋值，保存当前步骤需要继续使用的数据。
        tables.add(right, weight=1)

        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(left, text="可选课程", font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        ttk.Label(right, text="已选课程", font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        # 说明：给 columns 赋值，保存当前步骤需要继续使用的数据。
        columns = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("course_code", "课程编号", 85),
            ("course_name", "课程名称", 130),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("course_type", "课程性质", 90),
            ("credits", "学分", 55),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("semester", "开课学期", 85),
        ]
        # 说明：给 available_table 赋值，保存当前步骤需要继续使用的数据。
        available_table = self._make_table(left, columns)
        # 说明：给 selected_table 赋值，保存当前步骤需要继续使用的数据。
        selected_table = self._make_table(right, columns)

        # 说明：创建或配置 Tkinter 界面对象。
        bottom = ttk.Frame(self.content, style="Content.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        bottom.pack(fill="x", pady=(8, 0))

        # 说明：定义 load_students 函数，封装当前模块的一段处理逻辑。
        def load_students() -> None:
            # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
            if not self.is_admin:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 students 赋值，保存当前步骤需要继续使用的数据。
            students = self.student_service.list_students()
            # 说明：保存或更新 self._student_options 状态，供界面事件、页面刷新或权限判断继续使用。
            self._student_options = {f"{row['student_id']} - {row['name']}": row["student_id"] for row in students}
            # 说明：给 values 赋值，保存当前步骤需要继续使用的数据。
            values = list(self._student_options.keys())
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if student_box is not None:
                # 说明：给 student_box["values"] 赋值，保存当前步骤需要继续使用的数据。
                student_box["values"] = values
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if values and self._current_student_id.get() not in values:
                # 说明：切换表格勾选状态，实现多选功能。
                self._current_student_id.set(values[0])

        # 说明：定义 current_student_id 函数，封装当前模块的一段处理逻辑。
        def current_student_id() -> str | None:
            # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
            if not self.is_admin:
                # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                return self.current_user["student_id"] if self.current_user else None
            # 说明：返回处理结果，供调用方继续使用。
            return self._student_options.get(self._current_student_id.get())

        # 说明：定义 refresh 函数，封装当前模块的一段处理逻辑。
        def refresh() -> None:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            load_students()
            # 说明：给 student_id 赋值，保存当前步骤需要继续使用的数据。
            student_id = current_student_id()
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            available_table.delete(*available_table.get_children())
            selected_table.delete(*selected_table.get_children())
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not student_id:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                summary_var.set("暂无学生记录，请先维护学生信息")
                return
            # 说明：读取当前学生还可以选择的课程。
            available = self.enrollment_service.list_available_courses(student_id)
            # 说明：读取当前学生已经选择的课程。
            selected = self.enrollment_service.list_enrolled_courses(student_id)
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for row in available:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._insert_table_row(available_table, [row[key] for key, _, _ in columns])
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for row in selected:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._insert_table_row(selected_table, [row[key] for key, _, _ in columns])
            # 说明：读取并展示当前学生的学分统计结果。
            summary = self.enrollment_service.get_credit_summary(student_id)
            # 学分统计直接使用数据库中的系统设置，设置页保存后这里会同步刷新。
            if summary["is_qualified"]:
                # 说明：给 status 赋值，保存当前步骤需要继续使用的数据。
                status = "已达到要求"
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            else:
                # 说明：计算距离最低毕业学分要求还差多少。
                status = f"还差 {summary['remaining_credits']:.1f} 学分"
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            summary_var.set(
                f"已选 {summary['selected_count']} 门，总学分 {summary['total_credits']:.1f}，"
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                f"要求 {summary['required_credits']:.1f}，{status}"
            )
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.status_text.set("NYAN READY > 学生选课管理")

        # 说明：定义 enroll_selected 函数，封装当前模块的一段处理逻辑。
        def enroll_selected() -> None:
            # 说明：给 student_id 赋值，保存当前步骤需要继续使用的数据。
            student_id = current_student_id()
            # 说明：给 selected 赋值，保存当前步骤需要继续使用的数据。
            selected = self._selected_values(available_table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not student_id or not selected:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择可选课程", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
                if self.is_admin:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self.enrollment_service.enroll(student_id, selected["course_code"])
                # 说明：根据条件选择不同处理分支，控制程序执行路径。
                else:
                    # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                    self.enrollment_service.enroll_for_user(self.current_user, selected["course_code"])
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                refresh()
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._show_error(exc)

        # 说明：定义 enroll_many_selected 函数，封装当前模块的一段处理逻辑。
        def enroll_many_selected() -> None:
            # 说明：给 student_id 赋值，保存当前步骤需要继续使用的数据。
            student_id = current_student_id()
            # 说明：给 rows 赋值，保存当前步骤需要继续使用的数据。
            rows = self._selected_values_list(available_table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not student_id or not rows:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择要批量选课的可选课程", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 codes 赋值，保存当前步骤需要继续使用的数据。
            codes = [row["course_code"] for row in rows]
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
                if self.is_admin:
                    # 说明：给 count 赋值，保存当前步骤需要继续使用的数据。
                    count = self.enrollment_service.enroll_many(student_id, codes)
                # 说明：根据条件选择不同处理分支，控制程序执行路径。
                else:
                    # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                    count = self.enrollment_service.enroll_many_for_user(self.current_user, codes)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                refresh()
                self.status_text.set(f"NYAN READY > 已批量选课 {count} 门")
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._show_error(exc)

        # 说明：定义 withdraw_selected 函数，封装当前模块的一段处理逻辑。
        def withdraw_selected() -> None:
            # 说明：给 student_id 赋值，保存当前步骤需要继续使用的数据。
            student_id = current_student_id()
            # 说明：给 selected 赋值，保存当前步骤需要继续使用的数据。
            selected = self._selected_values(selected_table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not student_id or not selected:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择已选课程", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：弹出提示、错误、确认或结果信息。
            if messagebox.askyesno("确认退课", f"确定退选 {selected['course_name']} 吗？", parent=self):
                # 说明：开始异常捕获，避免底层错误直接中断程序。
                try:
                    # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
                    if self.is_admin:
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        self.enrollment_service.withdraw(student_id, selected["course_code"])
                    # 说明：根据条件选择不同处理分支，控制程序执行路径。
                    else:
                        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                        self.enrollment_service.withdraw_for_user(self.current_user, selected["course_code"])
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    refresh()
                # 说明：捕获异常并转换为业务提示或测试结果。
                except ServiceError as exc:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self._show_error(exc)

        # 说明：定义 withdraw_many_selected 函数，封装当前模块的一段处理逻辑。
        def withdraw_many_selected() -> None:
            # 说明：给 student_id 赋值，保存当前步骤需要继续使用的数据。
            student_id = current_student_id()
            # 说明：给 rows 赋值，保存当前步骤需要继续使用的数据。
            rows = self._selected_values_list(selected_table)
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            if not student_id or not rows:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showwarning("提示", "请先选择要批量退课的已选课程", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：给 codes 赋值，保存当前步骤需要继续使用的数据。
            codes = [row["course_code"] for row in rows]
            # 说明：弹出提示、错误、确认或结果信息。
            if messagebox.askyesno("批量退课", f"确定退选选中的 {len(codes)} 门课程吗？", parent=self):
                # 说明：开始异常捕获，避免底层错误直接中断程序。
                try:
                    # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
                    if self.is_admin:
                        # 说明：给 count 赋值，保存当前步骤需要继续使用的数据。
                        count = self.enrollment_service.withdraw_many(student_id, codes)
                    # 说明：根据条件选择不同处理分支，控制程序执行路径。
                    else:
                        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                        count = self.enrollment_service.withdraw_many_for_user(self.current_user, codes)
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    refresh()
                    self.status_text.set(f"NYAN READY > 已批量退课 {count} 门")
                # 说明：捕获异常并转换为业务提示或测试结果。
                except ServiceError as exc:
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    self._show_error(exc)

        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(bottom, text="选课", command=enroll_selected).pack(side="left", padx=(0, 8))
        ttk.Button(bottom, text="批量选课", command=enroll_many_selected).pack(side="left", padx=(0, 8))
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(bottom, text="退课", command=withdraw_selected).pack(side="left", padx=(0, 8))
        ttk.Button(bottom, text="批量退课", command=withdraw_many_selected).pack(side="left", padx=(0, 8))
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(bottom, text="刷新", command=refresh).pack(side="left", padx=(0, 8))
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if student_box is not None:
            # 说明：绑定控件事件，使用户操作能够触发回调函数。
            student_box.bind("<<ComboboxSelected>>", lambda _event: refresh())
        available_table.bind("<Double-1>", lambda _event: enroll_selected())
        # 说明：绑定控件事件，使用户操作能够触发回调函数。
        selected_table.bind("<Double-1>", lambda _event: withdraw_selected())
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        refresh()

    # 说明：显示学分统计页面，管理员看全体学生，学生看本人。
    def show_statistics(self) -> None:
        # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
        self._set_page("学分统计" if self.is_admin else "我的学分")
        # 说明：创建或配置 Tkinter 界面对象。
        toolbar = ttk.Frame(self.content, style="Toolbar.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        toolbar.pack(fill="x", pady=(0, 8))
        # 说明：创建或配置 Tkinter 界面对象。
        info_var = tk.StringVar()
        ttk.Label(toolbar, textvariable=info_var).pack(side="left")
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(toolbar, text="刷新", command=lambda: refresh()).pack(side="right")

        # 说明：给 columns 赋值，保存当前步骤需要继续使用的数据。
        columns = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("student_id", "学号", 110),
            ("name", "姓名", 90),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("class_name", "班级", 120),
            ("selected_count", "已选门数", 80),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("total_credits", "已选学分", 90),
            ("required_credits", "要求学分", 90),
            # 说明：计算距离最低毕业学分要求还差多少。
            ("remaining_credits", "差额学分", 90),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("status", "状态", 100),
        ]
        # 说明：给 table 赋值，保存当前步骤需要继续使用的数据。
        table = self._make_table(self.content, columns)

        # 说明：定义 refresh 函数，封装当前模块的一段处理逻辑。
        def refresh() -> None:
            # 说明：判断当前用户是否为管理员，从而控制菜单和操作权限。
            if self.is_admin:
                # 管理员查看全体学生汇总；学生只查看本人记录。
                rows = self.enrollment_service.list_student_summaries()
            # 说明：根据条件选择不同处理分支，控制程序执行路径。
            else:
                # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                student_id = self.current_user["student_id"]
                # 说明：给 student 赋值，保存当前步骤需要继续使用的数据。
                student = self.student_service.get_student(student_id)
                # 说明：读取并展示当前学生的学分统计结果。
                summary = self.enrollment_service.get_credit_summary(student_id)
                # 说明：给 rows 赋值，保存当前步骤需要继续使用的数据。
                rows = [
                    {
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        "student_id": student_id,
                        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                        "name": student["name"] if student else self.current_user["display_name"],
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        "class_name": student["class_name"] if student else "",
                        **summary,
                    }
                ]
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            table.delete(*table.get_children())
            # 说明：给 required 赋值，保存当前步骤需要继续使用的数据。
            required = self.settings_service.get_min_required_credits()
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            info_var.set(f"当前最低毕业学分要求：{required:.1f}")
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for row in rows:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._insert_table_row(
                    table,
                    [
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        row["student_id"],
                        row["name"],
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        row["class_name"],
                        row["selected_count"],
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        f"{float(row['total_credits']):.1f}",
                        f"{float(row['required_credits']):.1f}",
                        # 说明：计算距离最低毕业学分要求还差多少。
                        f"{float(row['remaining_credits']):.1f}",
                        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                        "达标" if row["is_qualified"] else "未达标",
                    ],
                )
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.status_text.set(f"NYAN READY > 学分统计：共 {len(rows)} 名学生")

        refresh()

    # 说明：显示系统设置页面，用于维护最低毕业学分。
    def show_settings(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.require_admin():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 系统规则写入 settings 表，避免把最低学分要求固定在界面或业务代码中。
        self._set_page("系统设置")
        # 说明：创建或配置 Tkinter 界面对象。
        panel = ttk.Frame(self.content, padding=18, style="Panel.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        panel.pack(anchor="nw")
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(panel, text="最低毕业学分").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=8)
        credits_var = tk.StringVar(value=f"{self.settings_service.get_min_required_credits():.1f}")
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Entry(panel, textvariable=credits_var, width=18).grid(row=0, column=1, sticky="w", pady=8)
        ttk.Label(panel, text="该配置保存在本地数据库 settings 表中。").grid(row=1, column=1, sticky="w", pady=(0, 12))

        # 说明：定义 save 函数，封装当前模块的一段处理逻辑。
        def save() -> None:
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self.settings_service.set_min_required_credits(credits_var.get())
                credits_var.set(f"{self.settings_service.get_min_required_credits():.1f}")
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showinfo("保存成功", "系统设置已保存", parent=self)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self.status_text.set("NYAN READY > 系统设置已保存")
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self._show_error(exc)

        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(panel, text="保存设置", command=save).grid(row=2, column=1, sticky="w")

    # 说明：打开学生自助修改密码弹窗。
    def open_change_password_dialog(self) -> None:
        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
        if not self.current_user:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
        if self.current_user["role"] != "student":
            # 说明：弹出提示、错误、确认或结果信息。
            messagebox.showwarning("提示", "管理员请在学生信息管理中重置学生密码。", parent=self)
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return

        # 学生自助修改密码成功后强制回到登录页，避免旧会话继续使用。
        dialog = tk.Toplevel(self)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.title("修改密码")
        dialog.geometry("360x260")
        # 说明：给 dialog.configure(bg 赋值，保存当前步骤需要继续使用的数据。
        dialog.configure(bg=THEME["bg"])
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.resizable(False, False)
        dialog.transient(self)
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        dialog.grab_set()

        # 说明：创建或配置 Tkinter 界面对象。
        form = ttk.Frame(dialog, padding=18, style="Panel.TFrame")
        # 说明：使用 pack 布局管理器摆放控件。
        form.pack(fill="both", expand=True)
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(form, text=f"当前账号：{self.current_user['username']}").grid(
            # 说明：给 row 赋值，保存当前步骤需要继续使用的数据。
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )

        # 说明：创建或配置 Tkinter 界面对象。
        old_var = tk.StringVar()
        new_var = tk.StringVar()
        # 说明：创建或配置 Tkinter 界面对象。
        confirm_var = tk.StringVar()
        # 说明：给 fields 赋值，保存当前步骤需要继续使用的数据。
        fields = [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("原密码", old_var),
            ("新密码", new_var),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            ("确认新密码", confirm_var),
        ]
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for row_index, (label, var) in enumerate(fields, 1):
            # 说明：创建或配置 Tkinter 界面对象。
            ttk.Label(form, text=label).grid(row=row_index, column=0, sticky="e", padx=(0, 8), pady=7)
            ttk.Entry(form, textvariable=var, width=24, show="*").grid(row=row_index, column=1, sticky="w", pady=7)
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Label(form, text="新密码长度不能少于6位。").grid(row=4, column=1, sticky="w", pady=(0, 12))

        # 说明：定义 save 函数，封装当前模块的一段处理逻辑。
        def save() -> None:
            # 说明：开始异常捕获，避免底层错误直接中断程序。
            try:
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                self.auth_service.change_password(
                    # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
                    self.current_user["username"],
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    old_var.get(),
                    new_var.get(),
                    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                    confirm_var.get(),
                )
            # 说明：捕获异常并转换为业务提示或测试结果。
            except ServiceError as exc:
                # 说明：弹出提示、错误、确认或结果信息。
                messagebox.showerror("修改失败", str(exc), parent=dialog)
                # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
                return
            # 说明：弹出提示、错误、确认或结果信息。
            messagebox.showinfo("修改成功", "密码已修改，请使用新密码重新登录。", parent=dialog)
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            dialog.destroy()
            # 说明：读取或更新当前登录用户信息，用于权限控制和本人数据限制。
            self.current_user = None
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.show_login()

        # 说明：创建或配置 Tkinter 界面对象。
        buttons = ttk.Frame(form)
        # 说明：使用 grid 网格布局管理器摆放控件。
        buttons.grid(row=5, column=0, columnspan=2, pady=(6, 0))
        # 说明：创建或配置 Tkinter 界面对象。
        ttk.Button(buttons, text="保存", command=save).pack(side="left", padx=6)
        ttk.Button(buttons, text="取消", command=dialog.destroy).pack(side="left", padx=6)

    # 说明：选择保存路径并导出课程 CSV。
    def export_courses(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.require_admin():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：给 path 赋值，保存当前步骤需要继续使用的数据。
        path = self._ask_save_path("课程信息表.csv")
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not path:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.course_service.export_courses_csv(path)
            # 说明：弹出提示、错误、确认或结果信息。
            messagebox.showinfo("导出成功", f"已导出到：\n{path}", parent=self)
        # 说明：捕获异常并转换为业务提示或测试结果。
        except ServiceError as exc:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self._show_error(exc)

    # 说明：选择保存路径并导出学生选课 CSV。
    def export_enrollments(self) -> None:
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not self.require_admin():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：给 path 赋值，保存当前步骤需要继续使用的数据。
        path = self._ask_save_path("学生选课表.csv")
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not path:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            return
        # 说明：开始异常捕获，避免底层错误直接中断程序。
        try:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self.enrollment_service.export_enrollments_csv(path)
            # 说明：弹出提示、错误、确认或结果信息。
            messagebox.showinfo("导出成功", f"已导出到：\n{path}", parent=self)
        # 说明：捕获异常并转换为业务提示或测试结果。
        except ServiceError as exc:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            self._show_error(exc)

    # 说明：显示系统关于信息。
    def show_about(self) -> None:
        # 说明：弹出提示、错误、确认或结果信息。
        messagebox.showinfo(
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            "关于",
            "学生选修课程系统\nPython + Tkinter + SQLite\n离线本地运行",
            # 说明：给 parent 赋值，保存当前步骤需要继续使用的数据。
            parent=self,
        )
