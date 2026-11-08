# -*- coding: utf-8 -*-
"""百炼语音 CLI 驱动：直接复用 bailian-voice 插件 MCP server 的底层实现。

用法（由 uv 环境运行，见 run_bailian.cmd）：
  python bailian_cli.py transcribe <file> [--out out.txt]
  python bailian_cli.py synthesize <text> [--out out.mp3] [--voice ID] [--model M]
  python bailian_cli.py clone <source音频> [--name 前缀] [--model M] [--lang zh] [--text 样本文字]
  python bailian_cli.py list-voices
  python bailian_cli.py delete-voice <voice_id>
结果一律打印 JSON（不回显任何密钥）。
"""
import argparse
import json
import sys
from pathlib import Path

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))

import server  # noqa: E402  导入即完成 CFG 加载（凭据从插件 secrets.local.json / 界面配置读取）


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("transcribe")
    t.add_argument("file")
    t.add_argument("--out", default="")

    s = sub.add_parser("synthesize")
    s.add_argument("text")
    s.add_argument("--out", default="")
    s.add_argument("--voice", default="")
    s.add_argument("--model", default="")

    c = sub.add_parser("clone")
    c.add_argument("source")
    c.add_argument("--name", default="")
    c.add_argument("--model", default="qwen3-tts-vc-2026-01-22")
    c.add_argument("--lang", default="zh")
    c.add_argument("--text", default="")

    lv = sub.add_parser("list-voices")
    lv.add_argument("--page-size", type=int, default=20)

    dv = sub.add_parser("delete-voice")
    dv.add_argument("voice_id")

    args = p.parse_args()
    if args.cmd == "transcribe":
        out = server.transcribe(file_path=args.file, output_path=args.out)
    elif args.cmd == "synthesize":
        out = server.synthesize(text=args.text, output_path=args.out,
                                voice=args.voice, model=args.model)
    elif args.cmd == "clone":
        out = server.clone_voice(source=args.source, name=args.name,
                                 target_model=args.model, language=args.lang,
                                 sample_text=args.text)
    elif args.cmd == "list-voices":
        out = server.list_voices(page_size=args.page_size)
    else:
        out = server.delete_voice(voice_id=args.voice_id)
    print(out, flush=True)


if __name__ == "__main__":
    main()
