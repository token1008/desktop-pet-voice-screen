# -*- coding: utf-8 -*-
# diff_face2026.py - 定位 Face_Data_2026.c 与权威 txt 的逐行差异(按数据行顺序对齐)
# 权威数据: D:/桌宠/表情替换项目/03_预览/Face_Data_2026_content.txt
# 校验对象: D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c
import re

TXT = r"D:/桌宠/表情替换项目/03_预览/Face_Data_2026_content.txt"
CC  = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c"

def parse_arrays_lines(path):
    """返回 {数组名: [ (行号, 原始行, tokens) ]}"""
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
            vals = re.findall(r"0[xX][0-9a-fA-F]+", body)
            if vals:
                result[cur].append((i, ln.rstrip("\n"), vals))
    return result

a = parse_arrays_lines(TXT)
b = parse_arrays_lines(CC)

for name, rows_a in a.items():
    rows_b = b.get(name, [])
    if len(rows_a) != len(rows_b):
        print("=== %s: 行数不同 权威=%d .c=%d ===" % (name, len(rows_a), len(rows_b)))
    na = sum(len(t) for _, _, t in rows_a)
    nb = sum(len(t) for _, _, t in rows_b)
    if na != nb:
        print("=== %s: 字节数不同 权威=%d .c=%d (差%+d) ===" % (name, na, nb, nb - na))
    # 对齐比较: 数据行一一对应
    for k in range(max(len(rows_a), len(rows_b))):
        if k < len(rows_a) and k < len(rows_b):
            la, ta = rows_a[k][1], rows_a[k][2]
            lb, tb = rows_b[k][1], rows_b[k][2]
            if ta != tb:
                print("--- %s 数据行#%d (权威txt行%d / .c行%d) ---" % (name, k + 1, rows_a[k][0], rows_b[k][0]))
                print("  txt (%d字节): %s" % (len(ta), la.strip()))
                print("  .c  (%d字节): %s" % (len(tb), lb.strip()))
        elif k < len(rows_a):
            print("--- %s .c 缺少数据行#%d (txt行%d): %s" % (name, k + 1, rows_a[k][0], rows_a[k][1].strip()))
        else:
            print("--- %s .c 多出数据行#%d (.c行%d): %s" % (name, k + 1, rows_b[k][0], rows_b[k][1].strip()))
    print("")
