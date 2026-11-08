# -*- coding: utf-8 -*-
"""检查下载立绘的透明通道与人物边界框"""
import os
from PIL import Image

SRC = r"D:\桌宠\表情替换项目\01_素材下载"

for name in ["芙宁娜立绘_官方.png", "流萤立绘_官方.png"]:
    path = os.path.join(SRC, name)
    im = Image.open(path)
    print(name, "mode:", im.mode, "size:", im.size)
    rgba = im.convert("RGBA")
    a = rgba.getchannel("A")
    bbox = a.getbbox()
    hist = a.histogram()
    total = im.size[0] * im.size[1]
    transparent = sum(hist[:16])
    opaque = sum(hist[240:])
    print("  alpha bbox:", bbox)
    print("  全透明占比: %.1f%%  全不透明占比: %.1f%%" % (transparent / total * 100, opaque / total * 100))
