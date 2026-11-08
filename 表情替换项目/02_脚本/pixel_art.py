# -*- coding: utf-8 -*-
"""
Q 版像素画 v8（128×64 单色 OLED 用）。
设计原则：剪影优先、大头身比(头19:身26)、躯干无内部细节、
深色部位=描边+实暗、浅色部位=实心亮。
不写任何文件，输出走 stdout。
用法: python -I pixel_art.py <png|sim> <furina|firefly> [white|blue]
"""
import sys
from io import BytesIO
from PIL import Image, ImageDraw

W, H = 128, 64
ZOOM = 6
WHITE_BG, WHITE_DOT = (16, 16, 16), (245, 245, 245)
BLUE_BG, BLUE_DOT = (5, 10, 16), (64, 190, 255)


def R(d, box, on=True):
    d.rectangle(box, fill=255 if on else 0)


def E(d, box, on=True):
    d.ellipse(box, fill=255 if on else 0)


def O(d, box):
    d.rectangle(box, outline=255)


def D(d, box):
    """棋盘格抖动填充。"""
    x0, y0, x1, y1 = box
    for j in range(y0, y1 + 1):
        for i in range(x0, x1 + 1):
            if (i + j) % 2 == 0:
                d.point((i, j), fill=255)


def draw_furina():
    """芙宁娜 v8：大礼帽(蓝帽带)/波波头侧发绺/领结/无内部细节躯干/白短裤/裸腿/深色短靴
    纵向布局: 帽4-14 头14-33 领33-34 躯干35-43 短裤45-49 腿49-53 靴53-59"""
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    cx = 64

    # ===== 帽子 (y4-14) =====
    R(d, (cx - 5, 4, cx + 5, 5), on=True)            # 帽顶
    R(d, (cx - 9, 5, cx + 9, 12), on=True)           # 帽筒
    R(d, (cx - 8, 8, cx + 8, 9), on=False)           # 蓝帽带(暗)
    R(d, (cx - 12, 12, cx + 12, 14), on=True)        # 帽檐

    # ===== 头/波波头 (y14-33) =====
    E(d, (cx - 12, 14, cx + 12, 33), on=True)
    R(d, (cx - 12, 24, cx - 8, 34), on=True)         # 左侧发绺(延到肩)
    R(d, (cx + 8, 24, cx + 12, 34), on=True)         # 右侧发绺(延到肩)
    # 五官(暗)
    R(d, (cx - 6, 24, cx - 5, 27), on=False)
    R(d, (cx + 5, 24, cx + 6, 27), on=False)
    R(d, (cx - 1, 29, cx + 1, 29), on=False)

    # ===== 颈部暗隙(窄)+深色领结 (y33-35) =====
    R(d, (cx - 4, 33, cx + 4, 33), on=False)
    R(d, (cx - 3, 34, cx + 3, 35), on=False)         # 深蓝领结(暗块)

    # ===== 躯干 (y36-43) + 手臂 =====
    R(d, (cx - 7, 36, cx + 7, 43), on=True)          # 躯干(无内部细节)
    R(d, (cx - 8, 36, cx - 8, 41), on=False)         # 左臂缝线
    R(d, (cx + 8, 36, cx + 8, 41), on=False)         # 右臂缝线
    R(d, (cx - 12, 36, cx - 9, 41), on=True)         # 左臂
    R(d, (cx + 9, 36, cx + 12, 41), on=True)         # 右臂
    R(d, (cx - 13, 41, cx - 10, 43), on=True)        # 白袖口
    R(d, (cx + 10, 41, cx + 13, 43), on=True)
    R(d, (cx - 14, 43, cx - 11, 45), on=True)        # 手
    R(d, (cx + 11, 43, cx + 14, 45), on=True)

    # ===== 白短裤 (y45-49, 上缘暗线分界) =====
    R(d, (cx - 8, 45, cx + 8, 45), on=False)
    R(d, (cx - 8, 46, cx + 8, 49), on=True)

    # ===== 腿 (y49-53) =====
    R(d, (cx - 6, 49, cx - 3, 53), on=True)
    R(d, (cx + 3, 49, cx + 6, 53), on=True)

    # ===== 靴 (y53-59): 白褶边+描边实暗+亮鞋底 =====
    R(d, (cx - 7, 53, cx - 2, 55), on=True)          # 左靴口褶边
    R(d, (cx + 2, 53, cx + 7, 55), on=True)          # 右靴口褶边
    O(d, (cx - 7, 55, cx - 2, 58))                   # 左靴身(暗)
    O(d, (cx + 2, 55, cx + 7, 58))                   # 右靴身
    R(d, (cx - 7, 58, cx - 2, 59), on=True)          # 亮鞋底
    R(d, (cx + 2, 58, cx + 7, 59), on=True)
    return img


def draw_firefly():
    """流萤 v8：银白长发+发梢+蝶饰/白外套深内衬/深色短裤(描边实暗)/黑过膝袜(描边实暗)
    纵向布局: 头4-24 发绺至33 躯干27-39 短裤40-45 袜45-57 鞋57-60"""
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    cx = 64

    # ===== 头/长发 (y4-24, 发绺至33) =====
    E(d, (cx - 11, 4, cx + 11, 24), on=True)
    R(d, (cx - 12, 10, cx - 11, 15), on=True)        # 左发量
    R(d, (cx + 11, 10, cx + 12, 15), on=True)        # 右发量
    R(d, (cx - 11, 16, cx - 8, 33), on=True)         # 左长发绺至胸
    R(d, (cx + 8, 16, cx + 11, 33), on=True)         # 右长发绺至胸
    for j in range(29, 34):                          # 发梢抖动
        for i in range(cx - 11, cx - 7):
            if (i + j) % 2 == 0:
                d.point((i, j), fill=255)
        for i in range(cx + 8, cx + 12):
            if (i + j) % 2 == 0:
                d.point((i, j), fill=255)
    # 刘海分界(暗)
    R(d, (cx - 7, 15, cx + 7, 15), on=False)
    # 五官(暗)
    R(d, (cx - 5, 18, cx - 4, 21), on=False)
    R(d, (cx + 4, 18, cx + 5, 21), on=False)
    R(d, (cx - 1, 23, cx + 1, 23), on=False)
    # 蝶形发饰(暗)
    R(d, (cx + 6, 9, cx + 8, 11), on=False)

    # ===== 躯干 (y25-39): 白外套+浅V领 =====
    R(d, (cx - 8, 25, cx + 8, 39), on=True)
    R(d, (cx - 2, 25, cx + 2, 26), on=False)         # 领口浅V
    # 手臂
    R(d, (cx - 12, 26, cx - 9, 37), on=True)
    R(d, (cx + 9, 26, cx + 12, 37), on=True)
    R(d, (cx - 13, 37, cx - 10, 39), on=True)        # 手
    R(d, (cx + 10, 37, cx + 13, 39), on=True)

    # ===== 短裤 (y40-45): 描边+抖动 =====
    O(d, (cx - 8, 40, cx + 8, 45))
    D(d, (cx - 7, 41, cx + 7, 44))
    R(d, (cx - 9, 39, cx + 9, 40), on=True)          # 上衣下摆亮边

    # ===== 过膝袜 (y46-57): 袜口亮边+描边抖动 =====
    R(d, (cx - 8, 46, cx - 3, 47), on=True)          # 左袜口
    R(d, (cx + 3, 46, cx + 8, 47), on=True)          # 右袜口
    O(d, (cx - 7, 47, cx - 3, 57))                   # 左袜身
    D(d, (cx - 6, 48, cx - 4, 56))
    O(d, (cx + 3, 47, cx + 7, 57))                   # 右袜身
    D(d, (cx + 4, 48, cx + 6, 56))
    # ===== 鞋 (y57-60) =====
    R(d, (cx - 8, 57, cx - 2, 58), on=True)          # 鞋头亮
    R(d, (cx + 2, 57, cx + 8, 58), on=True)
    O(d, (cx - 8, 58, cx - 3, 60))                   # 鞋身描边
    O(d, (cx + 2, 58, cx + 7, 60))
    return img


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


def png_bytes(img):
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


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


ART = {"furina": draw_furina, "firefly": draw_firefly}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "sim"
    who = sys.argv[2] if len(sys.argv) > 2 else "furina"
    colorway = sys.argv[3] if len(sys.argv) > 3 else "blue"
    canvas = ART[who]()
    if mode == "png":
        sys.stdout.buffer.write(png_bytes(canvas))
    elif mode == "c":
        names = {"furina": "Face_Furina_Chibi", "firefly": "Face_Firefly_Chibi"}
        cn = {"furina": "芙宁娜", "firefly": "流萤"}
        data = pack_c_array(canvas)
        sys.stdout.write(c_content(names[who], data,
                                   "%s Q版像素画 128×64 全屏图" % cn[who]))
    else:
        if colorway == "white":
            img = simulate_oled(canvas, WHITE_DOT, WHITE_BG, ZOOM)
        else:
            img = simulate_oled(canvas, BLUE_DOT, BLUE_BG, ZOOM)
        sys.stdout.buffer.write(png_bytes(img))


if __name__ == "__main__":
    main()
