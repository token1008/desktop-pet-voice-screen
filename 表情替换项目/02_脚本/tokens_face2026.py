# -*- coding: utf-8 -*-
# tokens_face2026.py - 打印分歧行的精确 token 序列 (整数), 用于精确修复
# 权威数据: D:/桌宠/表情替换项目/03_预览/Face_Data_2026_content.txt
# 校验对象: D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c
import re

TXT = r"D:/桌宠/表情替换项目/03_预览/Face_Data_2026_content.txt"
CC  = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c"

def parse_arrays_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    result = {}
    cur = None
    for i, ln in enumerate(lines, 1):
        m = re.search(r"uint8_t\s+(\w+)\s*\[", ln)
        if m:
            cur = m.group(1)
            result[cur] = []
            continue
        if cur is not None:
            if ln.strip().startswith("};"):
                cur = None
                continue
            body = re.sub(r"//[^\n]*", "", ln)
            vals = [int(v, 16) for v in re.findall(r"0[xX][0-9a-fA-F]+", body)]
            if vals:
                result[cur].append((i, vals))
    return result

a = parse_arrays_lines(TXT)
b = parse_arrays_lines(CC)

fmt = lambda vals: ",".join("0x%02X" % v for v in vals)

for name, rows_a in a.items():
    rows_b = b.get(name, [])
    ka = [t for _, t in rows_a]
    kb = [t for _, t in rows_b]
    if ka == kb:
        continue
    print("=== %s ===" % name)
    # 逐行对齐直到第一个差异
    idx = 0
    while idx < min(len(ka), len(kb)) and ka[idx] == kb[idx]:
        idx += 1
    print("首个差异在数据行#%d (txt行%d / .c行%d)" % (idx + 1, rows_a[idx][0], rows_b[idx][0]))
    print("  txt: %s" % fmt(ka[idx]))
    print("  .c : %s" % fmt(kb[idx]))
    # 后续行也打印出来辅助人工核对
    for j in range(idx + 1, min(len(ka), len(kb))):
        if ka[j] != kb[j]:
            print("  后续差异 数据行#%d (txt行%d / .c行%d)" % (j + 1, rows_a[j][0], rows_b[j][0]))
            print("    txt: %s" % fmt(ka[j]))
            print("    .c : %s" % fmt(kb[j]))
    if len(ka) != len(kb):
        print("  行数: txt=%d .c=%d" % (len(ka), len(kb)))
        for j in range(min(len(ka), len(kb)), max(len(ka), len(kb))):
            if j < len(ka):
                print("  txt独有 行%d: %s" % (rows_a[j][0], fmt(ka[j])))
            else:
                print("  .c独有  行%d: %s" % (rows_b[j][0], fmt(kb[j])))
    print("")
