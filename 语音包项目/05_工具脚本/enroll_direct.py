# -*- coding: utf-8 -*-
"""直接调用百炼 qwen-voice-enrollment 复刻接口：本地文件 base64 直传 + 自定义 target_model。

用法: python enroll_direct.py <样本音频> <prefix> <target_model> [sample_text]
结果打印 JSON（含 voice_id 或错误信息）。
"""
import base64
import json
import sys
import subprocess
import tempfile
import os
from pathlib import Path

PLUGIN_MCP_DIR = Path(r"C:\Users\a1575\.zcode\cli\plugins\cache\fufu-local\bailian-voice\0.6.1\mcp")
sys.path.insert(0, str(PLUGIN_MCP_DIR))
import server  # noqa: E402  复用其 CFG / _customization / _prepare_clone_audio


def main():
    src = Path(sys.argv[1])
    prefix = sys.argv[2]
    target_model = sys.argv[3]
    sample_text = sys.argv[4] if len(sys.argv) > 4 else ""

    workdir = Path(tempfile.mkdtemp(prefix="bailian_enroll_"))
    try:
        prepared, truncated = server._prepare_clone_audio(src, workdir)
        b64 = base64.b64encode(prepared.read_bytes()).decode()
        input_obj = {
            "action": "create",
            "target_model": target_model,
            "preferred_name": prefix,
            "language": "zh",
        }
        if sample_text:
            input_obj["text"] = sample_text
        input_obj["audio"] = {"data": f"data:audio/wav;base64,{b64}"}
        body = server._customization(server.CFG, {
            "model": "qwen-voice-enrollment", "input": input_obj})
        out = body.get("output", {})
        print(json.dumps({
            "voice_id": out.get("voice") or out.get("voice_id"),
            "target_model": target_model,
            "fallback_mode": out.get("fallback_mode"),
            "fallback_reason": out.get("fallback_reason"),
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)[:300]}, ensure_ascii=False))
    finally:
        server._cleanup_workdir(workdir)


if __name__ == "__main__":
    main()
