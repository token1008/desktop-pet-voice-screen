# -*- coding: utf-8 -*-
"""固件数据 .c 文件的生成辅助与校验（16字节/行短行格式，便于精确转录）。
用法:
  python -I verify_c.py dump furina   -> 打印期望的完整 .c 文件内容(短行)
  python -I verify_c.py check         -> 字节级校验两个 .c 文件，列出所有不一致行
"""
import re
import sys

sys.path.insert(0, r"D:\桌宠\表情替换项目\02_脚本")
import pixel_art  # noqa: E402

CHECKS = [
    (r"D:\桌宠\表情替换项目\04_固件数据\Face_Furina_Chibi.c",
     "furina", pixel_art.draw_furina, "芙宁娜"),
    (r"D:\桌宠\表情替换项目\04_固件数据\Face_Firefly_Chibi.c",
     "firefly", pixel_art.draw_firefly, "流萤"),
]

PER_LINE = 16


def parse_c_bytes(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return [int(n, 16) for n in re.findall(r"0[xX][0-9A-Fa-f]{2}", text)]


def build_file(name, data, comment):
    """生成 16字节/行 的完整 .c 文件内容。"""
    out = []
    out.append("/* %s */" % comment)
    out.append("/* 取模：128×64 页式(每字节8纵点)，阴码，低位在上(bit0=顶部)，与江协 OLED_ShowImage 兼容 */")
    out.append("const uint8_t %s[]={  // %d bytes" % (name, len(data)))
    for i in range(0, len(data), PER_LINE):
        row = data[i:i + PER_LINE]
        chunk = ",".join("0x%02X" % b for b in row)
        tail = "," if i + PER_LINE < len(data) else ""
        out.append("\t" + chunk + tail)
    out.append("};")
    return "\n".join(out) + "\n"


def dump(key):
    name = "Face_Furina_Chibi" if key == "furina" else "Face_Firefly_Chibi"
    cn = "芙宁娜" if key == "furina" else "流萤"
    drawer = pixel_art.draw_furina if key == "furina" else pixel_art.draw_firefly
    data = pixel_art.pack_c_array(drawer())
    sys.stdout.write(build_file(name, data, "%s Q版像素画 128×64 全屏图" % cn))


def check():
    ok_all = True
    for c_path, key, drawer, label in CHECKS:
        data = pixel_art.pack_c_array(drawer())
        try:
            got = parse_c_bytes(c_path)
        except FileNotFoundError:
            print("=== %s === 文件不存在" % label)
            ok_all = False
            continue
        if got == data:
            print("=== %s === 字节级完全一致 ✓ (%d bytes)" % (label, len(got)))
            continue
        ok_all = False
        print("=== %s === 不一致 (实际 %d / 期望 1024)" % (label, len(got)))
        # 期望行列表（按行号索引）：完整文件的 [3:-2] 恰好是 128 条数据行
        exp_lines = build_file("", data, "").split("\n")[3:-2]
        assert len(exp_lines) == 1024 // PER_LINE, len(exp_lines)
        with open(c_path, "r", encoding="utf-8") as f:
            c_text_lines = f.read().split("\n")
        data_lines_c = [ln for ln in c_text_lines if ln.strip().startswith("0x")]
        wrong = []
        for i, el in enumerate(exp_lines):
            cl = data_lines_c[i] if i < len(data_lines_c) else "<缺失>"
            cl_norm = cl.strip().rstrip(",")
            el_norm = el.strip().rstrip(",")
            if cl_norm != el_norm:
                wrong.append((i + 1, el, cl))
        print("不一致数据行数: %d" % len(wrong))
        for ln_no, el, cl in wrong:
            print("---- 数据行 %d" % ln_no)
            print("  期望: %s" % el)
            print("  实际: %s" % cl)
    print("\n总体:", "全部一致 ✓" if ok_all else "存在差异 ✗")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "dump" and len(sys.argv) == 3:
        dump(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "check":
        check()
    else:
        sys.stderr.write("用法: python -I verify_c.py <dump furina|dump firefly|check>\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
