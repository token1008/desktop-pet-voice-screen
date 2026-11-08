# -*- coding: utf-8 -*-
# hex_face2026.py - 从固件 Face_Data_2026.c 提取7个数组, 输出16进制串(用于预览页逐点渲染)
# 数据源: D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c
import re

SRC = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c"

with open(SRC, "r", encoding="utf-8") as f:
    text = f.read()

count = 0
for m in re.finditer(r"uint8_t\s+(\w+)\s*\[\s*\]\s*=\s*\{(.*?)\};", text, re.S):
    name = m.group(1)
    body = re.sub(r"//[^\n]*", "", m.group(2))
    vals = [int(v, 16) for v in re.findall(r"0[xX][0-9a-fA-F]+", body)]
    assert len(vals) == 1024, "%s 长度=%d" % (name, len(vals))
    print("%s|%s" % (name, "".join("%02X" % v for v in vals)))
    count += 1

assert count == 7, "数组数量=%d" % count
print("# OK: 7 arrays x 1024 bytes from firmware file")
