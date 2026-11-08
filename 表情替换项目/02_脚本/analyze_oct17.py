# -*- coding: utf-8 -*-
# analyze_oct17.py - 分析10月17日官方固件与当前源码的一致性, 并导出Face_Config代码段供反汇编分析
# 1) 解析 Project.hex, 提取7个原版数组地址处的1024字节
# 2) 与当前 OLED_Data.c 中原版数组逐字节比对 (证明构建与源码数据一致)
# 3) 导出 Face_Config 段(0x0800113c, 0x14c字节) 和 main 段, 供判断 case->数组 映射
import re

MAP_ARRAYS = {
    "Face_hello": 0x080042F0,
    "Face_eyes": 0x080046F0,
    "Face_happy": 0x08004AF0,
    "Face_mania": 0x08004EF0,
    "Face_sleep": 0x080052F0,
    "Face_stare": 0x080056F0,
    "Face_very_happy": 0x08005AF0,
}
HEX = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/Objects/Project.hex"
SRC = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/OLED_Data.c"

# ---- 解析 Intel HEX ----
mem = {}
upper = 0
with open(HEX, "r") as f:
    for line in f:
        line = line.strip()
        if not line.startswith(":"):
            continue
        raw = bytes.fromhex(line[1:])
        n, addr, rtype = raw[0], (raw[1] << 8) | raw[2], raw[3]
        data = raw[4:4 + n]
        if rtype == 0:
            for i, b in enumerate(data):
                mem[upper + addr + i] = b
        elif rtype == 4:
            upper = ((data[0] << 8) | data[1]) << 16
        elif rtype == 1:
            break
print("hex映射: %d 字节, 地址范围 0x%08X - 0x%08X" % (len(mem), min(mem), max(mem)))

# ---- 解析 OLED_Data.c 原版数组 ----
with open(SRC, "r", encoding="utf-8") as f:
    src = f.read()
orig = {}
for m in re.finditer(r"uint8_t\s+(Face_\w+)\s*\[\s*\]\s*=\s*\{(.*?)\};", src, re.S):
    name = m.group(1)
    if name.endswith("_X"):
        continue
    body = re.sub(r"//[^\n]*", "", m.group(2))
    vals = [int(v, 16) for v in re.findall(r"0[xX][0-9a-fA-F]+", body)]
    orig[name] = vals
print("源码中原版数组:", ", ".join("%s(%d)" % (k, len(v)) for k, v in sorted(orig.items())))

# ---- 比对 ----
ok = True
for name, addr in MAP_ARRAYS.items():
    if name not in orig:
        print("缺失源码数组:", name)
        ok = False
        continue
    vals = orig[name]
    got = [mem.get(addr + i) for i in range(len(vals))]
    if None in got:
        print("FAIL %s: hex中缺地址" % name)
        ok = False
        continue
    if vals == got:
        print("MATCH %s @0x%08X (1024 bytes)" % (name, addr))
    else:
        diffs = sum(1 for a, b in zip(vals, got) if a != b)
        print("DIFF  %s @0x%08X: %d/%d 字节不同" % (name, addr, diffs, len(vals)))
        ok = False

print("")
print("结论:", "10月17日固件的数据区与当前源码原版数组完全一致" if ok else "固件与源码不一致, 不能走原位替换路线")

# ---- 导出代码段(供反汇编判断case映射) ----
def dump(start, length, label):
    print("\n=== %s @0x%08X (%d bytes) ===" % (label, start, length))
    for off in range(0, length, 16):
        chunk = [mem.get(start + off + i) for i in range(16)]
        if any(x is None for x in chunk):
            print("%04X: <缺数据>" % off)
            continue
        hexs = " ".join("%02X" % x for x in chunk)
        le32 = ""
        if off + 16 <= length:
            for w in range(0, 16, 4):
                val = chunk[w] | (chunk[w + 1] << 8) | (chunk[w + 2] << 16) | (chunk[w + 3] << 24)
                le32 += " %08X" % val
        print("%04X: %-47s |%s" % (off, hexs, le32))

dump(0x0800113C, 0x14C, "face_config.o(i.Face_Config)")
dump(0x08002B98, 0x120, "main.o(i.main) 头部")
