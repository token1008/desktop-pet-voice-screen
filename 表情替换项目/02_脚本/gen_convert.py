# -*- coding: utf-8 -*-
"""将生成的像素画（纯白背景）转换为 128×64 单色 OLED 图。
流程：泛洪填充识别白底 -> 裁剪 -> 缩放(高62) -> 亮度/抖动变体 -> 模拟预览。
输出走 stdout，由外部重定向保存。
用法: python -I gen_convert.py <png|sim> <furina|firefly> <lum|dither|th> [white|blue]
"""
import sys
from collections import deque
from io import BytesIO

sys.path.insert(0, r"D:\桌宠\表情替换项目\02_脚本")
from PIL import Image, ImageOps

import pixel_art  # noqa: E402  (复用 simulate_oled / 常量)

SRC = {
    "furina": r"D:\桌宠\表情替换项目\01_素材下载\生成\furina_gen2.png",
    "firefly": r"D:\桌宠\表情替换项目\01_素材下载\生成\firefly_gen2.png",
    "furina_v1": r"D:\桌宠\表情替换项目\01_素材下载\生成\furina_gen.png",
    "firefly_v1": r"D:\桌宠\表情替换项目\01_素材下载\生成\firefly_gen.png",
    "firefly_ref": r"D:\桌宠\表情替换项目\01_素材下载\参考图\流萤_参考.png",
    "furina_ref": r"D:\桌宠\表情替换项目\01_素材下载\参考图\芙宁娜_参考.png",
    "furina_bust": r"D:\桌宠\表情替换项目\01_素材下载\生成\furina_bust.png",
    "firefly_bust": r"D:\桌宠\表情替换项目\01_素材下载\生成\firefly_bust.png",
    "firefly_bust2": r"D:\桌宠\表情替换项目\01_素材下载\生成\firefly_bust2.png",
    "firefly_bust3": r"D:\桌宠\表情替换项目\01_素材下载\生成\firefly_bust3.png",
    "firefly_bust4": r"D:\桌宠\表情替换项目\01_素材下载\生成\firefly_bust4.png",
    "furina_sleep": r"D:\桌宠\表情替换项目\01_素材下载\生成\furina_sleep.png",
    "furina_lying": r"D:\桌宠\表情替换项目\01_素材下载\生成\furina_lying.png",
    "furina_lying2": r"D:\桌宠\表情替换项目\01_素材下载\生成\furina_lying2.png",
    "firefly_stare": r"D:\桌宠\表情替换项目\01_素材下载\生成\firefly_stare.png",
    "furina_excited": r"D:\桌宠\表情替换项目\01_素材下载\生成\furina_excited.png",
    "firefly_hello": r"D:\桌宠\表情替换项目\01_素材下载\生成\firefly_hello.png",
}
# 参考图/大头贴(脸部特写)使用满屏高度
CHAR_H_MAP = {"firefly_ref": 64, "furina_ref": 64,
              "firefly_bust": 64, "furina_bust": 64,
              "firefly_bust2": 64, "firefly_bust3": 64, "firefly_bust4": 64,
              "furina_sleep": 64, "firefly_stare": 64,
              "furina_excited": 64, "firefly_hello": 64,
              "furina_lying": 64, "furina_lying2": 64}
W, H = 128, 64
CHAR_H = 62

# 头部区域占人物高度比例（脸部清晰转换用）；参考图整幅都是脸 → 1.0
HEAD_ENDS = {"furina": 0.50, "firefly": 0.52, "furina_v1": 0.55, "firefly_v1": 0.55,
             "firefly_ref": 1.0, "furina_ref": 1.0,
             "firefly_bust": 1.0, "furina_bust": 1.0,
             "firefly_bust2": 1.0, "firefly_bust3": 1.0, "firefly_bust4": 1.0,
             "furina_sleep": 1.0, "firefly_stare": 1.0,
             "furina_excited": 1.0, "firefly_hello": 1.0,
             "furina_lying": 1.0, "furina_lying2": 1.0}
# 参考图特殊区：顶部低阈值区（深色帽子实心化），比例 + 阈值
TOP_LOW = {"furina_ref": (0.34, 60, 0.5), "furina_bust": (0.30, 60, 0.5),
           "furina_sleep": (0.30, 60, 0.5), "furina_excited": (0.30, 60, 0.5),
           "furina_lying2": (0.45, 60, 0.5)}
# 宽幅横排模式：按指定宽度缩放(水平居中)，再垂直裁剪64高窗口；(宽度, 纵向偏移)
FIT_WIDTH = {}
# 区域裁剪：按内容bbox的比例保留 (宽比例, 高比例) —— 用于从宽构图中裁出头部+手
CROP_FRAC = {"furina_lying": (0.55, 0.90)}


def largest_alpha_component(alpha):
    """只保留最大连通非透明区（人物主体），剔除孤立装饰物。"""
    px = alpha.load()
    w, h = alpha.size
    seen = [[False] * w for _ in range(h)]
    best = []
    for y0 in range(h):
        for x0 in range(w):
            if px[x0, y0] > 40 and not seen[y0][x0]:
                comp = []
                stack = [(x0, y0)]
                seen[y0][x0] = True
                while stack:
                    x, y = stack.pop()
                    comp.append((x, y))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < w and 0 <= ny < h and px[nx, ny] > 40
                                    and not seen[ny][nx]):
                                seen[ny][nx] = True
                                stack.append((nx, ny))
                if len(comp) > len(best):
                    best = comp
    result = Image.new("L", alpha.size, 0)
    rp = result.load()
    for x, y in best:
        rp[x, y] = 255
    return result


def despeckle_small(bw):
    """一轮孤点清理：亮点邻居<2 则熄灭；被>=7邻居包围的暗点补亮。"""
    px = bw.load()
    w, h = bw.size
    kills, fills = [], []
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
            if px[x, y] and n < 2:
                kills.append((x, y))
            elif not px[x, y] and n >= 7:
                fills.append((x, y))
    for x, y in kills:
        px[x, y] = 0
    for x, y in fills:
        px[x, y] = 255
    return bw


def log(msg):
    sys.stderr.write(msg + "\n")


def load_figures(path):
    """返回 (rgb图, figure_alpha掩码)：与边框连通的近白/透明区域=背景。"""
    im0 = Image.open(path)
    if im0.mode in ("RGBA", "LA", "P"):
        rgba = im0.convert("RGBA")
        white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        white.alpha_composite(rgba)
        im = white.convert("RGB")
        # 有 alpha 通道时直接以 alpha>40 为人物，再做最大连通域剔除装饰
        a = rgba.getchannel("A")
        if a.getextrema()[0] < 200:
            a = largest_alpha_component(a)
            bbox = a.getbbox()
            rgb_c = im.crop(bbox)
            return rgb_c, a.crop(bbox)
    else:
        im = im0.convert("RGB")
    w, h = im.size
    px = im.load()
    NEAR_WHITE = 235

    def is_bg(x, y):
        r, g, b = px[x, y]
        return r > NEAR_WHITE and g > NEAR_WHITE and b > NEAR_WHITE

    bg = [[False] * w for _ in range(h)]
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(x, y) and not bg[y][x]:
                bg[y][x] = True
                dq.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(x, y) and not bg[y][x]:
                bg[y][x] = True
                dq.append((x, y))
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not bg[ny][nx] and is_bg(nx, ny):
                bg[ny][nx] = True
                dq.append((nx, ny))

    alpha = Image.new("L", im.size, 0)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            if not bg[y][x]:
                ap[x, y] = 255
    return im, alpha


def stretch(gray):
    hist = gray.histogram()
    total = gray.size[0] * gray.size[1]
    lo = hi = 0
    acc = 0
    for i, c in enumerate(hist):
        acc += c
        if acc >= total * 0.02:
            lo = i
            break
    acc = 0
    for i in range(255, -1, -1):
        acc += hist[i]
        if acc >= total * 0.02:
            hi = i
            break
    if hi <= lo:
        hi = lo + 1
    return gray.point(lambda v: max(0, min(255, (v - lo) * 255 // (hi - lo))))


def make_canvas(path, char_h=None, who=None):
    ch = char_h or CHAR_H
    im, alpha = load_figures(path)
    bbox = alpha.getbbox()
    im = im.crop(bbox)
    alpha = alpha.crop(bbox)
    w, h = im.size
    if who in CROP_FRAC:
        fx, fy = CROP_FRAC[who]
        im = im.crop((0, 0, int(w * fx), int(h * fy)))
        alpha = alpha.crop((0, 0, int(w * fx), int(h * fy)))
        w, h = im.size

    if who in FIT_WIDTH:
        # 宽幅横排：按指定宽度缩放(水平居中)，垂直裁出64高窗口
        fw, y_off = FIT_WIDTH[who]
        nw = min(W, fw)
        nh = max(ch, round(h * nw / w))
        black = Image.new("RGB", im.size, (0, 0, 0))
        black.paste(im, (0, 0), alpha)
        small = black.resize((nw, nh), Image.LANCZOS)
        small_a = alpha.resize((nw, nh), Image.LANCZOS)
        x0 = (W - nw) // 2
        canvas_rgb = Image.new("RGB", (W, H), (0, 0, 0))
        canvas_rgb.paste(small, (x0, y_off))
        canvas_a = Image.new("L", (W, H), 0)
        canvas_a.paste(small_a, (x0, y_off))
        return canvas_rgb, canvas_a

    nw = max(1, round(w * ch / h))
    black = Image.new("RGB", im.size, (0, 0, 0))
    black.paste(im, (0, 0), alpha)
    small = black.resize((nw, ch), Image.LANCZOS)
    small_a = alpha.resize((nw, ch), Image.LANCZOS)

    canvas_rgb = Image.new("RGB", (W, H), (0, 0, 0))
    canvas_rgb.paste(small, ((W - nw) // 2, H - ch))
    canvas_a = Image.new("L", (W, H), 0)
    canvas_a.paste(small_a, ((W - nw) // 2, H - ch))
    return canvas_rgb, canvas_a


def make_variants(rgb, alpha, who="furina"):
    gray = ImageOps.grayscale(rgb)
    mask = alpha.point(lambda v: 255 if v > 96 else 0)
    gray_s = stretch(gray)
    # 伽马提亮：暗部(深色衣料/袜子)提升到可读的抖动密度，避免下半身消失
    GAMMA = 0.55
    gray_g = gray_s.point(lambda v: round(255 * (v / 255.0) ** GAMMA))

    variants = {}
    # ============ smart：分区域转换（脸部清晰 + 身体干净少黑点） ============
    HEAD_END = HEAD_ENDS[who]                 # 头部占人物高度比例
    gp = gray.load()
    mp = mask.load()
    out = Image.new("L", gray.size, 0)
    op = out.load()
    w, h = gray.size
    # 找人物实际顶部（canvas 内第一个 mask 行）
    top = 0
    for yy in range(h):
        if any(mp[xx, yy] for xx in range(w)):
            top = yy
            break
    head_cut = top + int((h - top) * HEAD_END)
    G_BODY = 0.55
    tl = TOP_LOW.get(who)          # (比例, 阈值, 伽马) —— 伽马仅趴姿版需要
    for yy in range(h):
        for xx in range(w):
            if not mp[xx, yy]:
                continue
            v = gp[xx, yy]
            if tl and yy < top + int((h - top) * tl[0]):
                # 顶部低阈值区(深色帽子实心化)：伽马=1 时等价于原始整数阈值
                if tl[2] == 1.0:
                    op[xx, yy] = 255 if v > tl[1] else 0
                else:
                    vg = 255 * (v / 255.0) ** tl[2]
                    op[xx, yy] = 255 if vg > tl[1] else 0
            elif yy < head_cut:
                # 头部：高阈值，五官(眼/嘴/帽带/轮廓)全灭，肤色白发全亮
                op[xx, yy] = 255 if v > 138 else 0
            else:
                # 身体：伽马提亮后低阈值，纯黑轮廓变稀疏点阵
                vg = 255 * (v / 255.0) ** G_BODY
                if vg > 62:
                    op[xx, yy] = 255
                elif vg > 42:
                    # 极暗带(纯黑轮廓/黑袜): 25% 稀疏点亮，保持结构可见
                    op[xx, yy] = 255 if (xx % 2 == 0 and yy % 2 == 0) else 0
                else:
                    op[xx, yy] = 0
    # 孤点清理
    out = despeckle_small(out)
    variants["smart"] = out
    # 阈值（旧）
    th = gray_g.point(lambda v: 255 if v > 128 else 0)
    variants["th"] = Image.composite(th, Image.new("L", gray.size, 0), mask)
    # Floyd-Steinberg 抖动（纹理细节最丰富，暗部呈纹理）
    dit = gray_g.convert("1", dither=Image.Dither.FLOYDSTEINBERG).convert("L")
    variants["dither"] = Image.composite(
        dit.point(lambda v: 255 if v > 127 else 0),
        Image.new("L", gray.size, 0), mask)
    # 混合：亮部实心 + 中间调抖动（避免脸部/白衣被噪点覆盖）
    mixed = gray_g.point(lambda v: 255 if v > 175 else (128 if v > 85 else 0))
    mixed = mixed.convert("1", dither=Image.Dither.FLOYDSTEINBERG).convert("L")
    variants["mix"] = Image.composite(
        mixed.point(lambda v: 255 if v > 127 else 0),
        Image.new("L", gray.size, 0), mask)
    return variants


def main():
    mode = sys.argv[1]
    who = sys.argv[2]
    variant = sys.argv[3] if len(sys.argv) > 3 else "dither"
    colorway = sys.argv[4] if len(sys.argv) > 4 else "blue"
    rgb, alpha = make_canvas(SRC[who], CHAR_H_MAP.get(who), who)
    bw = make_variants(rgb, alpha, who)[variant]
    if mode == "png":
        buf = BytesIO()
        bw.convert("1").save(buf, "PNG")
        sys.stdout.buffer.write(buf.getvalue())
    elif mode == "dump":
        # 打印完整 .c 文件内容（16字节/行短行格式）
        names = {("furina", "smart"): "Face_Furina_AIGen2_Smart",
                 ("firefly", "smart"): "Face_Firefly_AIGen2_Smart",
                 ("furina_ref", "smart"): "Face_Furina_Ref_Smart",
                 ("firefly_ref", "smart"): "Face_Firefly_Ref_Smart",
                 ("furina_bust", "smart"): "Face_Furina_Bust_Smart",
                 ("firefly_bust", "smart"): "Face_Firefly_Bust_Smart",
                 ("firefly_bust2", "smart"): "Face_Firefly_Bust2_Smart",
                 ("firefly_bust3", "smart"): "Face_Firefly_Bust3_Smart",
                 ("firefly_bust4", "smart"): "Face_Firefly_Bust4_Smart",
                 ("furina_sleep", "smart"): "Face_Furina_Sleep",
                 ("firefly_stare", "smart"): "Face_Firefly_Stare",
                 ("furina_excited", "smart"): "Face_Furina_Excited",
                 ("firefly_hello", "smart"): "Face_Firefly_Hello",
                 ("furina_lying", "smart"): "Face_Furina_Lying",
                 ("furina_lying2", "smart"): "Face_Furina_Lying2",
                 ("furina", "mix"): "Face_Furina_AIGen_Mix",
                 ("firefly", "mix"): "Face_Firefly_AIGen_Mix",
                 ("furina", "dither"): "Face_Furina_AIGen_Dither",
                 ("firefly", "dither"): "Face_Firefly_AIGen_Dither"}
        cn = {"furina": "芙宁娜", "firefly": "流萤",
              "furina_ref": "芙宁娜(参考图)", "firefly_ref": "流萤(参考图)",
              "furina_bust": "芙宁娜(大头贴)", "firefly_bust": "流萤(大头贴)",
              "firefly_bust2": "流萤(大笑)", "firefly_bust3": "流萤(眨眼)",
              "firefly_bust4": "流萤(温柔)",
              "furina_sleep": "芙宁娜(睡觉)", "firefly_stare": "流萤(瞪眼)",
              "furina_excited": "芙宁娜(兴奋)", "firefly_hello": "流萤(打招呼)",
              "furina_lying": "芙宁娜(趴姿)", "furina_lying2": "芙宁娜(趴姿大头贴)"}
        vc = {"smart": "分区转换", "mix": "AI生图转换(混合)",
              "dither": "AI生图转换(抖动)"}
        data = pixel_art.pack_c_array(bw)
        lines = []
        lines.append("/* %s %s 128×64 全屏图 */" % (cn[who], vc[variant]))
        lines.append("/* 取模：128×64 页式(每字节8纵点)，阴码，低位在上(bit0=顶部)，与江协 OLED_ShowImage 兼容 */")
        lines.append("const uint8_t %s[]={  // %d bytes" % (names[(who, variant)], len(data)))
        PER = 16
        for i in range(0, len(data), PER):
            row = data[i:i + PER]
            chunk = ",".join("0x%02X" % b for b in row)
            lines.append("\t" + chunk + ("," if i + PER < len(data) else ""))
        lines.append("};")
        sys.stdout.write("\n".join(lines) + "\n")
    else:
        if colorway == "white":
            img = pixel_art.simulate_oled(bw, pixel_art.WHITE_DOT, pixel_art.WHITE_BG, 6)
        else:
            img = pixel_art.simulate_oled(bw, pixel_art.BLUE_DOT, pixel_art.BLUE_BG, 6)
        buf = BytesIO()
        img.save(buf, "PNG")
        sys.stdout.buffer.write(buf.getvalue())


if __name__ == "__main__":
    main()
