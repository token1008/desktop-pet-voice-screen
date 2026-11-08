# -*- coding: utf-8 -*-
# patch_hex_2026.py - 在原厂固件(10月17日 Project.hex)中原位替换7个表情位图, 生成新固件
# 依据: Face_Config 反汇编证实 case0..6 -> [sleep, stare, happy, mania, very_happy, eyes, hello]
#       main 开机 -> Face_eyes
# 替换映射(零代码改动, 仅换7x1024字节位图):
#   Face_sleep      <- Face_Furina_Lying_X    (case0 睡觉)
#   Face_stare      <- Face_Firefly_Stare_X   (case1 蹲下)
#   Face_happy      <- Face_Firefly_X         (case2 前进/后退/转向)
#   Face_mania      <- Face_Furina_Excited_X  (case3 摇摆)
#   Face_very_happy <- Face_Firefly_Laugh_X   (case4 非常快乐)
#   Face_eyes       <- Face_Furina_X          (case5 站立 + 开机画面)
#   Face_hello      <- Face_Firefly_Hello_X   (case6 打招呼)
import re
from pathlib import Path

SRC_C = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/HardWare/Face_Data_2026.c"
HEX_IN = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/Objects/Project.hex"
HEX_OUT = r"D:/桌宠/桌宠代码/适配1.2.0版本电路板的代码/桌面宠物代码(更新于26年3月23日)适配国产芯片/Objects/Project_Face2026.hex"

SLOTS = {
    "Face_sleep":      (0x080052F0, "Face_Furina_Lying_X"),
    "Face_stare":      (0x080056F0, "Face_Firefly_Stare_X"),
    "Face_happy":      (0x08004AF0, "Face_Firefly_X"),
    "Face_mania":      (0x08004EF0, "Face_Furina_Excited_X"),
    "Face_very_happy": (0x08005AF0, "Face_Firefly_Laugh_X"),
    "Face_eyes":       (0x080046F0, "Face_Furina_X"),
    "Face_hello":      (0x080042F0, "Face_Firefly_Hello_X"),
}

def parse_hex(path):
    mem = {}
    upper = 0
    with open(path, "r") as f:
        for ln in f:
            ln = ln.strip()
            if not ln.startswith(":"):
                continue
            raw = bytes.fromhex(ln[1:])
            n, addr, rtype = raw[0], (raw[1] << 8) | raw[2], raw[3]
            data = raw[4:4 + n]
            chk = sum(raw[:-1]) & 0xFF
            assert (chk + raw[-1]) & 0xFF == 0, "原始hex校验和错误: " + ln
            if rtype == 0:
                for i, b in enumerate(data):
                    mem[upper + addr + i] = b
            elif rtype == 4:
                upper = ((data[0] << 8) | data[1]) << 16
            elif rtype == 1:
                break
    return mem

def write_hex(mem):
    addrs = sorted(mem)
    lines = []
    def rec(addr16, rtype, data):
        raw = bytes([len(data), (addr16 >> 8) & 0xFF, addr16 & 0xFF, rtype]) + bytes(data)
        ck = (0x100 - (sum(raw) & 0xFF)) & 0xFF
        return ":" + raw.hex().upper() + "%02X" % ck
    upper = None
    i = 0
    while i < len(addrs):
        a = addrs[i]
        up = a >> 16
        if up != upper:
            lines.append(rec(0, 4, [(up >> 8) & 0xFF, up & 0xFF]))
            upper = up
        chunk = [mem[a]]
        j = i + 1
        while j < len(addrs) and addrs[j] == addrs[j - 1] + 1 and len(chunk) < 16 and (addrs[j] >> 16) == up:
            chunk.append(mem[addrs[j]])
            j += 1
        lines.append(rec(a & 0xFFFF, 0, chunk))
        i = j
    lines.append(":00000001FF")
    Path(HEX_OUT).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)

# ---- 读取新表情数据 ----
with open(SRC_C, "r", encoding="utf-8") as f:
    src = f.read()
new = {}
for m in re.finditer(r"uint8_t\s+(\w+)\s*\[\s*\]\s*=\s*\{(.*?)\};", src, re.S):
    body = re.sub(r"//[^\n]*", "", m.group(2))
    vals = [int(v, 16) for v in re.findall(r"0[xX][0-9a-fA-F]+", body)]
    new[m.group(1)] = vals
assert len(new) == 7
for name in new:
    assert len(new[name]) == 1024, name

# ---- 打补丁 ----
mem = parse_hex(HEX_IN)
orig = dict(mem)
changed_ranges = {}
for slot, (addr, newname) in SLOTS.items():
    data = new[newname]
    for i, b in enumerate(data):
        if addr + i not in mem:
            raise SystemExit("地址缺失: %s +%d" % (slot, i))
        mem[addr + i] = b
    lo, hi = addr, addr + 1023
    changed_ranges[slot] = (lo, hi)

n_lines = write_hex(mem)
print("已生成:", HEX_OUT)

# ---- 三层校验 ----
back = parse_hex(HEX_OUT)
assert set(back.keys()) == set(orig.keys()), "地址集合发生变化!"
diff = [a for a in sorted(orig) if back[a] != orig[a]]
in_ranges = 0
for slot, (lo, hi) in changed_ranges.items():
    in_ranges += sum(1 for a in diff if lo <= a <= hi)
print("校验1 地址完整: 通过 (%d 字节, 与原固件相同地址集)" % len(back))
# 注意: 新旧位图相同的字节(背景0x00等)不产生差异, 差异数本就小于7x1024
expected_diff = 0
for slot, (addr, newname) in SLOTS.items():
    expected_diff += sum(1 for i in range(1024) if orig[addr + i] != new[newname][i])
diff_all_in = (in_ranges == len(diff))
print("校验2 差异范围: %d 字节被修改(预期%d), 全部落在7个表情区内: %s" % (
    len(diff), expected_diff, "是" if diff_all_in else "否!!"))

ok2 = True
for slot, (addr, newname) in SLOTS.items():
    got = [back[addr + i] for i in range(1024)]
    same = got == new[newname]
    print("校验3 %-16s @0x%08X <- %-24s %s" % (slot, addr, newname, "OK" if same else "FAIL"))
    ok2 = ok2 and same
assert ok2 and in_ranges == len(diff) and len(diff) == expected_diff, "校验失败!"

# 字节级确认: 未改动的部分与原固件完全一致
unchanged = all(orig[a] == back[a] for a in orig if a not in set(diff))
print("校验4 其余区域: 与原厂固件逐字节一致:", "是" if unchanged else "否!!")
print("\nRESULT: PATCH HEX 生成并校验通过")
