# -*- coding: utf-8 -*-
# verify_face2026.py - 逐字节校验 HardWare/Face_Data_2026.c 与权威数据文件是否完全一致
# 权威数据: D:/桌宠/表情替换项目/03_预览/Face_Data_2026_content.txt
# 校验对象: D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c
import re
import sys

TXT = r"D:/桌宠/表情替换项目/03_预览/Face_Data_2026_content.txt"
CC  = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c"

def parse_arrays(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    arrays = {}
    for m in re.finditer(r"uint8_t\s+(\w+)\s*\[\s*\]\s*=\s*\{(.*?)\};", text, re.S):
        name = m.group(1)
        body = m.group(2)
        body = re.sub(r"//[^\n]*", "", body)
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
        vals = re.findall(r"0[xX][0-9a-fA-F]+", body)
        arrays[name] = [int(v, 16) for v in vals]
    return arrays

expect = parse_arrays(TXT)
actual = parse_arrays(CC)

ok = True
for name, data in expect.items():
    got = actual.get(name)
    if got is None:
        print("MISSING  in .c :", name)
        ok = False
        continue
    if len(data) != 1024:
        print("WARN: 权威数据 %s 长度=%d (非1024)" % (name, len(data)))
    if len(data) != len(got):
        print("LEN DIFF %s: 权威=%d .c=%d" % (name, len(data), len(got)))
        ok = False
        continue
    diffs = [i for i in range(len(data)) if data[i] != got[i]]
    if diffs:
        first = diffs[0]
        print("BYTE DIFF %s: 共%d字节不同, 首个在 idx %d (权威=0x%02X .c=0x%02X)" % (
            name, len(diffs), first, data[first], got[first]))
        ok = False
    else:
        print("OK  %s  (%d bytes)" % (name, len(data)))

for name in actual:
    if name not in expect:
        print("EXTRA in .c:", name)
        ok = False

print("")
if ok:
    print("RESULT: ALL 7 ARRAYS BYTE-PERFECT")
else:
    print("RESULT: MISMATCH FOUND")
    sys.exit(1)
