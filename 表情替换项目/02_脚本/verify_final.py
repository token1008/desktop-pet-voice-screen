# -*- coding: utf-8 -*-
"""最终校验：OLED_Data.c 中新增的 Face_Furina / Face_Firefly 数组
必须与转换管线的预期数据逐字节一致；其余数组结构完整性检查。"""
import re
import sys

sys.path.insert(0, r"D:\桌宠\表情替换项目\02_脚本")
import gen_convert as gc  # noqa: E402
import pixel_art  # noqa: E402

OLED_DATA_C = (r"D:\桌宠\桌宠代码\适配1.2.0版本电路板的代码"
               r"\桌面宠物代码(更新于26年3月23日)适配国产芯片\HardWare\OLED_Data.c")
PER_LINE = 16


def expected_bytes(who):
    rgb, alpha = gc.make_canvas(gc.SRC[who], gc.CHAR_H_MAP.get(who))
    variants = gc.make_variants(rgb, alpha, who)
    return pixel_art.pack_c_array(variants["smart"])


def parse_array(text, name):
    m = re.search(r"const uint8_t %s\[\]\s*=\s*\{(.*?)\};" % name, text, re.S)
    if not m:
        return None
    return [int(n, 16) for n in re.findall(r"0[xX][0-9A-Fa-f]{2}", m.group(1))]


def expected_lines(data):
    lines = []
    for i in range(0, len(data), PER_LINE):
        row = data[i:i + PER_LINE]
        chunk = ",".join("0x%02X" % b for b in row)
        lines.append("\t" + chunk + ("," if i + PER_LINE < len(data) else ""))
    return lines


def main():
    with open(OLED_DATA_C, "r", encoding="utf-8") as f:
        text = f.read()

    ok = True
    for name, who, label in [
            ("Face_Furina", "furina_bust", "芙宁娜眨眼笑"),
            ("Face_Firefly", "firefly_bust4", "流萤微笑"),
            ("Face_Firefly_Laugh", "firefly_bust2", "流萤大笑"),
            ("Face_Firefly_Stare", "firefly_stare", "流萤瞪眼"),
            ("Face_Furina_Excited", "furina_excited", "芙宁娜兴奋"),
            ("Face_Firefly_Hello", "firefly_hello", "流萤打招呼"),
            ("Face_Furina_Lying2", "furina_lying2", "芙宁娜趴姿")]:
        exp = expected_bytes(who)
        got = parse_array(text, name)
        if got is None:
            print("[%s] 数组 %s 未找到!" % (label, name))
            ok = False
            continue
        if got == exp:
            print("[%s] %s 字节级完全一致 ✓ (%d bytes)" % (label, name, len(got)))
            continue
        ok = False
        n = min(len(got), len(exp))
        first = next((i for i in range(n) if got[i] != exp[i]), n)
        row_no = first // PER_LINE + 1
        print("[%s] %s 不一致! 实际%d字节, 首个差异@byte %d (数据行%d)"
              % (label, name, len(got), first, row_no))
        print("期望行:")
        print(expected_lines(exp)[row_no - 1])

    # 结构完整性：原有 7 表情 + Diode 仍在
    for name, size in [("Face_eyes", 1024), ("Face_happy", 1024), ("Face_mania", 1024),
                       ("Face_sleep", 1024), ("Face_stare", 1024),
                       ("Face_very_happy", 1024), ("Face_hello", 1024), ("Diode", 32)]:
        arr = parse_array(text, name)
        if arr is None or len(arr) != size:
            print("[结构] %s 异常! 长度=%s" % (name, len(arr) if arr else "None"))
            ok = False
        else:
            print("[结构] %s 完整 (%d bytes) ✓" % (name, len(arr)))

    print("\n总体:", "校验通过 ✓" if ok else "存在差异 ✗")


if __name__ == "__main__":
    main()
