# -*- coding: utf-8 -*-
"""
将官方立绘转换为 128×64 单色 OLED 位图（多种风格候选 + 模拟预览）。
本脚本不写任何文件：所有输出经 stdout 输出，由外部重定向保存。
用法: python -I convert_to_oled.py <png|c> <key>
  key: furina_sil / furina_lum / furina_dit / firefly_sil / firefly_lum / firefly_dit
"""
import sys
from io import BytesIO
from PIL import Image, ImageOps

# ---------------- 输入路径常量（字面量） ----------------
SRC_FURINA = r"D:\桌宠\表情替换项目\01_素材下载\芙宁娜立绘_透明.png"
SRC_FIREFLY = r"D:\桌宠\表情替换项目\01_素材下载\流萤立绘_官方.png"
SRC_FIREFLY2 = r"D:\桌宠\表情替换项目\01_素材下载\流萤春日手信立绘.png"

# 人物手工裁剪窗口（去除大范围特效，仅取人物主体）
CROP_FURINA = (915, 120, 1105, 865)
CROP_FIREFLY = (860, 700, 1280, 1580)
CROP_FIREFLY2 = (620, 320, 1230, 1900)

# ---------------- 参数 ----------------
W, H = 128, 64
CHAR_H = 62
ZOOM = 6
WHITE_BG, WHITE_DOT = (16, 16, 16), (245, 245, 245)
BLUE_BG, BLUE_DOT = (5, 10, 16), (64, 190, 255)
LUM_THRESHOLD = 105


def log(msg):
    sys.stderr.write(msg + "\n")


def load_and_crop(path_literal, crop_box):
    """加载立绘并按手工窗口裁剪出人物主体。"""
    im = Image.open(path_literal).convert("RGBA")
    if crop_box:
        im = im.crop(crop_box)
    return im


def largest_component_keep(bw):
    """只保留最大的连通亮区（人物主体），清除零散特效残点。"""
    px = bw.load()
    w, h = bw.size
    seen = [[False] * w for _ in range(h)]
    best = []
    for y0 in range(h):
        for x0 in range(w):
            if px[x0, y0] and not seen[y0][x0]:
                comp = []
                stack = [(x0, y0)]
                seen[y0][x0] = True
                while stack:
                    x, y = stack.pop()
                    comp.append((x, y))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < w and 0 <= ny < h and px[nx, ny] and not seen[ny][nx]:
                                seen[ny][nx] = True
                                stack.append((nx, ny))
                if len(comp) > len(best):
                    best = comp
    result = Image.new("L", bw.size, 0)
    rp = result.load()
    for x, y in best:
        rp[x, y] = 255
    return result


def fill_holes(bw):
    """填充封闭孔洞（背景不可达的暗区 → 亮），让剪影更完整。"""
    px = bw.load()
    w, h = bw.size
    reach = [[False] * w for _ in range(h)]
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if not px[x, y] and not reach[y][x]:
                reach[y][x] = True
                stack.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not px[x, y] and not reach[y][x]:
                reach[y][x] = True
                stack.append((x, y))
    while stack:
        x, y = stack.pop()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and not px[nx, ny] and not reach[ny][nx]:
                    reach[ny][nx] = True
                    stack.append((nx, ny))
    for y in range(h):
        for x in range(w):
            if not px[x, y] and not reach[y][x]:
                px[x, y] = 255
    return bw


def despeckle(bw, passes=2, keep_neighbors=2):
    """二值图孤点清理：连续邻居少于 keep_neighbors 的点熄灭；
    被 >=7 个邻居包围的暗点补亮（填单像素孔洞）。"""
    px = bw.load()
    w, h = bw.size
    for _ in range(passes):
        kills = []
        fills = []
        for y in range(h):
            for x in range(w):
                n = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and px[nx, ny]:
                            n += 1
                if px[x, y] and n < keep_neighbors:
                    kills.append((x, y))
                elif not px[x, y] and n >= 7:
                    fills.append((x, y))
        for x, y in kills:
            px[x, y] = 0
        for x, y in fills:
            px[x, y] = 255
    return bw


def whiteness_channel(rgba):
    """白度通道 = min(R,G,B) × (A/255)：
    白亮不透明区域高、彩色特效低、透明区恒为 0
    （防止透明像素存储的白色 RGB 误亮）。"""
    r, g, b, a = rgba.split()
    rp, gp, bp, ap = r.load(), g.load(), b.load(), a.load()
    out = Image.new("L", rgba.size, 0)
    op = out.load()
    for y in range(rgba.size[1]):
        for x in range(rgba.size[0]):
            op[x, y] = min(rp[x, y], gp[x, y], bp[x, y]) * ap[x, y] // 255
    return out


def to_canvas(im):
    """等比缩放：高 62px、底部对齐、水平居中，128×64 透明画布。"""
    w, h = im.size
    scale = CHAR_H / h
    nw = max(1, round(w * scale))
    bg = Image.new("RGBA", im.size, (0, 0, 0, 0))
    bg.alpha_composite(im)
    small = bg.resize((nw, CHAR_H), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(small, ((W - nw) // 2, H - CHAR_H))
    return canvas


def stretch(gray):
    """3%~97% 分位对比度拉伸。"""
    hist = gray.histogram()
    total = gray.size[0] * gray.size[1]
    lo = hi = 0
    acc = 0
    for i, c in enumerate(hist):
        acc += c
        if acc >= total * 0.03:
            lo = i
            break
    acc = 0
    for i in range(255, -1, -1):
        acc += hist[i]
        if acc >= total * 0.03:
            hi = i
            break
    if hi <= lo:
        hi = lo + 1
    return gray.point(lambda v: max(0, min(255, (v - lo) * 255 // (hi - lo))))


def make_variants(rgba):
    """基于白度通道的三种风格（均做最大连通域保留 + 孔洞填充）：
    Silhouette=剪影（低阈值白度，完整轮廓）
    Lum=白度阈值（保留脸部/服饰明暗结构，彩色特效自动脱落）
    Dither=Floyd-Steinberg 抖动（层次最丰富）
    """
    wht = whiteness_channel(rgba)
    wht_s = stretch(wht)

    variants = {}
    # 剪影：低阈值 → 主连通域 → 填孔
    sil = wht.point(lambda v: 255 if v > 45 else 0)
    sil = largest_component_keep(sil)
    sil = fill_holes(sil)
    sil = despeckle(sil, passes=1, keep_neighbors=2)
    variants["Silhouette"] = sil

    # 亮度阈值（不做连通域裁剪，避免身体断块被误删）
    lum = wht.point(lambda v: 255 if v > 125 else 0)
    lum = despeckle(lum, passes=2, keep_neighbors=2)
    variants["Lum"] = lum

    # 抖动
    dithered = wht_s.convert("1", dither=Image.Dither.FLOYDSTEINBERG).convert("L")
    dit = dithered.point(lambda v: 255 if v > 127 else 0)
    dit = despeckle(dit, passes=1, keep_neighbors=2)
    variants["Dither"] = dit
    return variants


def simulate_oled(bw, color, bgc, zoom):
    px = bw.load()
    img = Image.new("RGB", (W * zoom, H * zoom), bgc)
    for y in range(H):
        for x in range(W):
            if px[x, y]:
                for dy in range(zoom):
                    for dx in range(zoom):
                        img.putpixel((x * zoom + dx, y * zoom + dy), color)
    return img


def pack_c_array(bw):
    """页式取模：字节=一列8纵点，bit0=顶部；字节序=页×列，1024字节。"""
    px = bw.load()
    data = []
    for page in range(H // 8):
        for x in range(W):
            b = 0
            for bit in range(8):
                if px[x, page * 8 + bit]:
                    b |= (1 << bit)
            data.append(b)
    assert len(data) == 1024
    return data


def c_content(name, data, comment):
    lines = []
    lines.append("/* %s */" % comment)
    lines.append("/* 取模：128×64 页式(每字节8纵点)，阴码，低位在上(bit0=顶部)，与江协 OLED_ShowImage 兼容 */")
    lines.append("const uint8_t %s[]={  // %d bytes" % (name, len(data)))
    for page in range(8):
        row = data[page * 128:(page + 1) * 128]
        chunk = ",".join("0x%02X" % b for b in row)
        lines.append("\t" + chunk + ("," if page < 7 else ""))
    lines.append("};")
    return "\n".join(lines) + "\n"


def png_bytes(img):
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


SOURCES = {
    "furina": (SRC_FURINA, CROP_FURINA),
    "firefly": (SRC_FIREFLY, CROP_FIREFLY),
    "firefly2": (SRC_FIREFLY2, CROP_FIREFLY2),
}


def build_one(char):
    src, box = SOURCES[char]
    im = load_and_crop(src, box)
    log("[%s] 裁剪后: %s" % (char, im.size))
    canvas = to_canvas(im)
    return make_variants(canvas)


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("png", "c", "sim"):
        log("用法: python -I convert_to_oled.py <png|c|sim> <key> [white|blue]")
        sys.exit(2)
    mode, key = sys.argv[1], sys.argv[2]
    char, _, variant_short = key.partition("_")
    vmap = {"sil": "Silhouette", "lum": "Lum", "dit": "Dither"}
    if char not in SOURCES or variant_short not in vmap:
        log("未知 key: %s" % key)
        sys.exit(2)

    variants = build_one(char)
    bw = variants[vmap[variant_short]]

    if mode == "png":
        sys.stdout.buffer.write(png_bytes(bw.convert("1")))
    elif mode == "sim":
        colorway = sys.argv[3] if len(sys.argv) > 3 else "blue"
        if colorway == "white":
            img = simulate_oled(bw, WHITE_DOT, WHITE_BG, ZOOM)
        else:
            img = simulate_oled(bw, BLUE_DOT, BLUE_BG, ZOOM)
        sys.stdout.buffer.write(png_bytes(img))
    elif mode == "c":
        names = {"furina": "Face_Furina", "firefly": "Face_Firefly",
                 "firefly2": "Face_Firefly2"}
        cn = {"furina": "芙宁娜", "firefly": "流萤", "firefly2": "流萤·春日手信"}
        vc = {"Silhouette": "剪影", "Lum": "亮度阈值", "Dither": "抖动"}
        vname = vmap[variant_short]
        cname = "%s_%s" % (names[char], vname)
        data = pack_c_array(bw)
        sys.stdout.write(c_content(cname, data,
                                   "%s %s风格 128×64 全屏图" % (cn[char], vc[vname])))


if __name__ == "__main__":
    main()
