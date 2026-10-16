# 说明：启用延迟类型注解，提升类型提示在不同 Python 版本下的兼容性。
from __future__ import annotations

# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import struct
import zlib
# 说明：导入当前模块需要使用的标准库、第三方库或项目内部模块。
import shutil
from pathlib import Path


# 说明：给 ASSET_DIR 赋值，保存当前步骤需要继续使用的数据。
ASSET_DIR = Path(__file__).resolve().parent / "assets"
# 说明：给 NYAN_SOURCE 赋值，保存当前步骤需要继续使用的数据。
NYAN_SOURCE = ASSET_DIR / "nyan_cat_source.gif"
# 说明：给 NYAN_LOGIN 赋值，保存当前步骤需要继续使用的数据。
NYAN_LOGIN = ASSET_DIR / "nyan_cat_login.gif"
# 说明：给 NYAN_SIDEBAR 赋值，保存当前步骤需要继续使用的数据。
NYAN_SIDEBAR = ASSET_DIR / "nyan_cat_sidebar.gif"
# 说明：给 LOGIN_FALLBACK 赋值，保存当前步骤需要继续使用的数据。
LOGIN_FALLBACK = ASSET_DIR / "login_mascot.png"
# 说明：给 SIDEBAR_FALLBACK 赋值，保存当前步骤需要继续使用的数据。
SIDEBAR_FALLBACK = ASSET_DIR / "sidebar_mascot.png"
# 说明：给 KANBAN_SOURCE 赋值，保存当前步骤需要继续使用的数据。
KANBAN_SOURCE = ASSET_DIR / "kanban_catgirl_candidate.png"
# 说明：给 KANBAN_FALLBACK 赋值，保存当前步骤需要继续使用的数据。
KANBAN_FALLBACK = ASSET_DIR / "kanban_musume_fallback.png"


# 说明：构造 PNG 文件块，用于手动生成占位素材图片。
def _png_chunk(kind: bytes, data: bytes) -> bytes:
    # 说明：给 checksum 赋值，保存当前步骤需要继续使用的数据。
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
    # 说明：使用 pack 布局管理器摆放控件。
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


# 说明：把像素数组编码并写入 PNG 文件。
def _save_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    # 说明：给 raw 赋值，保存当前步骤需要继续使用的数据。
    raw = bytearray()
    # 说明：循环处理多条记录、多个控件或多个动画粒子。
    for y in range(height):
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        raw.append(0)
        # 说明：给 start 赋值，保存当前步骤需要继续使用的数据。
        start = y * width
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for r, g, b, a in pixels[start : start + width]:
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            raw.extend((r, g, b, a))
    # 说明：给 data 赋值，保存当前步骤需要继续使用的数据。
    data = b"".join(
        [
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            b"\x89PNG\r\n\x1a\n",
            # 说明：使用 pack 布局管理器摆放控件。
            _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            _png_chunk(b"IEND", b""),
        ]
    )
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    path.write_bytes(data)


# 说明：简易像素画布类，用于生成本地备用素材。
class PixelCanvas:
    # 说明：文档字符串，用于说明当前模块、类或函数的用途。
    """用于生成缺失素材时的简易像素画布。"""

    # 说明：定义 __init__ 函数，封装当前模块的一段处理逻辑。
    def __init__(self, width: int, height: int, scale: int = 3):
        # 说明：给 self.grid_width 赋值，保存当前步骤需要继续使用的数据。
        self.grid_width = width
        # 说明：给 self.grid_height 赋值，保存当前步骤需要继续使用的数据。
        self.grid_height = height
        # 说明：给 self.scale 赋值，保存当前步骤需要继续使用的数据。
        self.scale = scale
        # 说明：给 self.width 赋值，保存当前步骤需要继续使用的数据。
        self.width = width * scale
        # 说明：给 self.height 赋值，保存当前步骤需要继续使用的数据。
        self.height = height * scale
        # 说明：给 self.pixels 赋值，保存当前步骤需要继续使用的数据。
        self.pixels = [(0, 0, 0, 0)] * (self.width * self.height)

    # 说明：定义 rect 函数，封装当前模块的一段处理逻辑。
    def rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int, int]) -> None:
        # 说明：给 x0, y0 赋值，保存当前步骤需要继续使用的数据。
        x0, y0 = x * self.scale, y * self.scale
        # 说明：给 x1, y1 赋值，保存当前步骤需要继续使用的数据。
        x1, y1 = (x + w) * self.scale, (y + h) * self.scale
        # 说明：循环处理多条记录、多个控件或多个动画粒子。
        for py in range(max(0, y0), min(self.height, y1)):
            # 说明：给 row 赋值，保存当前步骤需要继续使用的数据。
            row = py * self.width
            # 说明：循环处理多条记录、多个控件或多个动画粒子。
            for px in range(max(0, x0), min(self.width, x1)):
                # 说明：给 self.pixels[row + px] 赋值，保存当前步骤需要继续使用的数据。
                self.pixels[row + px] = color

    # 说明：定义 save 函数，封装当前模块的一段处理逻辑。
    def save(self, path: Path) -> None:
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        _save_png(path, self.width, self.height, self.pixels)


# 说明：生成登录页备用彩虹猫素材。
def _make_login_mascot(path: Path) -> None:
    # 说明：给 c 赋值，保存当前步骤需要继续使用的数据。
    c = PixelCanvas(48, 48, 3)
    # 说明：给 outline 赋值，保存当前步骤需要继续使用的数据。
    outline = (25, 25, 45, 255)
    # 说明：给 gray 赋值，保存当前步骤需要继续使用的数据。
    gray = (153, 153, 153, 255)
    # 说明：给 gray_light 赋值，保存当前步骤需要继续使用的数据。
    gray_light = (205, 205, 205, 255)
    # 说明：给 pink 赋值，保存当前步骤需要继续使用的数据。
    pink = (255, 160, 205, 255)
    # 说明：给 toast 赋值，保存当前步骤需要继续使用的数据。
    toast = (248, 214, 147, 255)
    # 说明：给 red 赋值，保存当前步骤需要继续使用的数据。
    red = (255, 65, 65, 255)
    # 说明：给 orange 赋值，保存当前步骤需要继续使用的数据。
    orange = (255, 162, 51, 255)
    # 说明：给 yellow 赋值，保存当前步骤需要继续使用的数据。
    yellow = (255, 238, 70, 255)
    # 说明：给 green 赋值，保存当前步骤需要继续使用的数据。
    green = (75, 220, 92, 255)
    # 说明：给 blue 赋值，保存当前步骤需要继续使用的数据。
    blue = (76, 171, 255, 255)
    # 说明：给 purple 赋值，保存当前步骤需要继续使用的数据。
    purple = (163, 92, 255, 255)
    # 说明：给 star 赋值，保存当前步骤需要继续使用的数据。
    star = (255, 255, 255, 255)

    # 说明：循环处理多条记录、多个控件或多个动画粒子。
    for index, color in enumerate([red, orange, yellow, green, blue, purple]):
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        c.rect(2, 16 + index * 2, 20, 2, color)
    c.rect(20, 13, 16, 15, outline)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(22, 15, 12, 11, toast)
    c.rect(23, 16, 10, 9, pink)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(34, 11, 10, 10, outline)
    c.rect(36, 13, 6, 6, gray)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(35, 10, 2, 3, gray_light)
    c.rect(41, 10, 2, 3, gray_light)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(37, 15, 1, 1, outline)
    c.rect(41, 15, 1, 1, outline)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(39, 18, 2, 1, outline)
    c.rect(17, 27, 4, 3, gray)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(29, 27, 4, 3, gray)
    c.rect(42, 21, 4, 2, gray)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(6, 7, 2, 2, star)
    c.rect(12, 35, 2, 2, star)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(40, 5, 2, 2, star)
    c.save(path)


# 说明：生成侧边栏备用彩虹猫素材。
def _make_sidebar_mascot(path: Path) -> None:
    # 说明：给 c 赋值，保存当前步骤需要继续使用的数据。
    c = PixelCanvas(48, 36, 2)
    # 说明：给 outline 赋值，保存当前步骤需要继续使用的数据。
    outline = (25, 25, 45, 255)
    # 说明：给 gray 赋值，保存当前步骤需要继续使用的数据。
    gray = (153, 153, 153, 255)
    # 说明：给 pink 赋值，保存当前步骤需要继续使用的数据。
    pink = (255, 160, 205, 255)
    # 说明：给 toast 赋值，保存当前步骤需要继续使用的数据。
    toast = (248, 214, 147, 255)
    # 说明：给 colors 赋值，保存当前步骤需要继续使用的数据。
    colors = [
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        (255, 65, 65, 255),
        (255, 162, 51, 255),
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        (255, 238, 70, 255),
        (75, 220, 92, 255),
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        (76, 171, 255, 255),
        (163, 92, 255, 255),
    ]

    # 说明：循环处理多条记录、多个控件或多个动画粒子。
    for index, color in enumerate(colors):
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        c.rect(1, 11 + index * 2, 21, 2, color)
    c.rect(19, 9, 16, 15, outline)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(21, 11, 12, 11, toast)
    c.rect(22, 12, 10, 9, pink)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(33, 7, 10, 10, outline)
    c.rect(35, 9, 6, 6, gray)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(36, 11, 1, 1, outline)
    c.rect(40, 11, 1, 1, outline)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(38, 14, 2, 1, outline)
    c.rect(16, 23, 4, 3, gray)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(28, 23, 4, 3, gray)
    c.rect(41, 17, 4, 2, gray)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.save(path)


# 说明：生成备用看板娘像素图。
def _make_kanban_musume(path: Path) -> None:
    # 说明：给 c 赋值，保存当前步骤需要继续使用的数据。
    c = PixelCanvas(40, 56, 3)
    # 说明：给 outline 赋值，保存当前步骤需要继续使用的数据。
    outline = (31, 25, 53, 255)
    # 说明：给 skin 赋值，保存当前步骤需要继续使用的数据。
    skin = (255, 224, 208, 255)
    # 说明：给 blush 赋值，保存当前步骤需要继续使用的数据。
    blush = (255, 136, 174, 255)
    # 说明：给 hair 赋值，保存当前步骤需要继续使用的数据。
    hair = (83, 104, 196, 255)
    # 说明：给 hair_light 赋值，保存当前步骤需要继续使用的数据。
    hair_light = (120, 205, 255, 255)
    # 说明：给 pink 赋值，保存当前步骤需要继续使用的数据。
    pink = (255, 111, 178, 255)
    # 说明：给 pink_light 赋值，保存当前步骤需要继续使用的数据。
    pink_light = (255, 210, 234, 255)
    # 说明：给 cream 赋值，保存当前步骤需要继续使用的数据。
    cream = (255, 248, 221, 255)
    # 说明：给 skirt 赋值，保存当前步骤需要继续使用的数据。
    skirt = (82, 198, 245, 255)
    # 说明：给 sock 赋值，保存当前步骤需要继续使用的数据。
    sock = (250, 250, 255, 255)
    # 说明：给 shoe 赋值，保存当前步骤需要继续使用的数据。
    shoe = (45, 39, 76, 255)
    # 说明：给 yellow 赋值，保存当前步骤需要继续使用的数据。
    yellow = (255, 242, 96, 255)

    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(5, 5, 4, 4, yellow)
    c.rect(6, 4, 2, 6, yellow)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(4, 6, 6, 2, yellow)
    c.rect(31, 8, 3, 3, pink_light)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(32, 7, 1, 5, pink_light)
    c.rect(30, 9, 5, 1, pink_light)

    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(11, 4, 6, 7, outline)
    c.rect(12, 5, 4, 5, pink_light)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(24, 4, 6, 7, outline)
    c.rect(25, 5, 4, 5, pink_light)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(8, 9, 24, 20, outline)
    c.rect(10, 11, 20, 18, hair)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(11, 13, 18, 14, skin)
    c.rect(8, 13, 5, 13, hair)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(28, 13, 5, 13, hair)
    c.rect(13, 10, 4, 4, hair_light)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(22, 10, 4, 4, hair_light)
    c.rect(15, 17, 2, 2, outline)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(24, 17, 2, 2, outline)
    c.rect(16, 18, 1, 1, cream)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(25, 18, 1, 1, cream)
    c.rect(19, 23, 4, 1, outline)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(13, 21, 3, 2, blush)
    c.rect(25, 21, 3, 2, blush)

    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(18, 28, 5, 3, skin)
    c.rect(9, 31, 23, 12, outline)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(11, 32, 19, 10, cream)
    c.rect(17, 31, 3, 5, pink)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(21, 31, 3, 5, pink)
    c.rect(18, 34, 5, 3, pink)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(6, 32, 5, 12, outline)
    c.rect(7, 33, 3, 9, skin)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(31, 32, 5, 12, outline)
    c.rect(32, 33, 3, 9, skin)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(9, 42, 23, 7, outline)
    c.rect(11, 43, 19, 5, skirt)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(13, 49, 5, 5, skin)
    c.rect(24, 49, 5, 5, skin)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(13, 53, 5, 2, sock)
    c.rect(24, 53, 5, 2, sock)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.rect(11, 55, 8, 1, shoe)
    c.rect(23, 55, 8, 1, shoe)
    # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
    c.save(path)


# 说明：检查素材文件是否存在，缺失时生成本地占位素材。
def ensure_assets() -> dict[str, Path]:
    # 优先使用下载的 Nyan Cat / 看板娘素材；素材缺失时生成占位图，保证离线运行不崩溃。
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if not KANBAN_SOURCE.exists():
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        _make_kanban_musume(KANBAN_SOURCE)
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if not KANBAN_FALLBACK.exists():
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        _make_kanban_musume(KANBAN_FALLBACK)
    # 说明：给 kanban_path 赋值，保存当前步骤需要继续使用的数据。
    kanban_path = KANBAN_SOURCE if KANBAN_SOURCE.exists() else KANBAN_FALLBACK
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if NYAN_SOURCE.exists():
        if not NYAN_LOGIN.exists():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            shutil.copyfile(NYAN_SOURCE, NYAN_LOGIN)
        # 说明：根据条件选择不同处理分支，控制程序执行路径。
        if not NYAN_SIDEBAR.exists():
            # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
            shutil.copyfile(NYAN_SOURCE, NYAN_SIDEBAR)
        # 说明：返回处理结果，供调用方继续使用。
        return {"login": NYAN_LOGIN, "sidebar": NYAN_SIDEBAR, "source": NYAN_SOURCE, "kanban": kanban_path}
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if not LOGIN_FALLBACK.exists():
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        _make_login_mascot(LOGIN_FALLBACK)
    # 说明：根据条件选择不同处理分支，控制程序执行路径。
    if not SIDEBAR_FALLBACK.exists():
        # 说明：执行当前逻辑语句，完成所在函数中的一个处理步骤。
        _make_sidebar_mascot(SIDEBAR_FALLBACK)
    # 说明：返回处理结果，供调用方继续使用。
    return {"login": LOGIN_FALLBACK, "sidebar": SIDEBAR_FALLBACK, "kanban": kanban_path}
