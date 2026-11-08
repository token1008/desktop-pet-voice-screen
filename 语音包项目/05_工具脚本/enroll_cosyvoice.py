# -*- coding: utf-8 -*-
"""尝试 voice-enrollment(cosyvoice 复刻) 接口 + base64 data URI 样本。

用法: python enroll_cosyvoice.py <样本音频> <prefix>
"""
import base64
import json
import sys
import tempfile
from pathlib import Path

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))
import server  # noqa: E402


def main():
    src = Path(sys.argv[1])
    prefix = sys.argv[2]

    workdir = Path(tempfile.mkdtemp(prefix="bailian_cv_"))
    try:
        prepared, _ = server._prepare_clone_audio(src, workdir)
        b64 = base64.b64encode(prepared.read_bytes()).decode()
        input_obj = {
            "action": "create_voice",
            "prefix": prefix[:10],
            "url": f"data:audio/wav;base64,{b64}",
            "language_hints": ["zh"],
        }
        body = server._customization(server.CFG, {
            "model": "voice-enrollment", "input": input_obj})
        out = body.get("output", {})
        print(json.dumps({
            "voice_id": out.get("voice_id") or out.get("voice"),
            "status": out.get("status"),
            "raw_keys": list(out.keys()),
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)[:300]}, ensure_ascii=False))
    finally:
        server._cleanup_workdir(workdir)


if __name__ == "__main__":
    main()
