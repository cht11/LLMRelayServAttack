#!/usr/bin/env python3
"""对照实验：普通请求（无 Agent 特征），预期不触发注入。"""
import httpx, json, os

RELAY_BASE_URL = "http://192.168.50.218:3000/api"
RELAY_API_KEY  = "cr_4ed27837ed3c7c477358b0ab7663a56904dc48fdf53eb8e19178c0a233e21c60"
PROMPT = "告诉我更新ubuntu系统软件包的命令，不要多余回答，markdown格式"
print("[ 普通请求 ]  UA: python-httpx  →  对照组（不应注入）")
print("─" * 50)
print(f"User: {PROMPT}")
print(f"LLM Response:")
full_text = ""
with httpx.Client(timeout=60.0) as client:
    with client.stream("POST", f"{RELAY_BASE_URL}/v1/messages",
        headers={
            "User-Agent": "python-httpx/0.27",
            "x-api-key": RELAY_API_KEY,
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        json={
            "model": "ccr,MiniMax-M2.5",
            "max_tokens": 256,
            "stream": True,
            "messages": [{"role": "user", "content": PROMPT}]
        }
    ) as resp:
        for line in resp.iter_lines():
            if not line or not line.startswith("data: "):
                continue
            data = line[6:].strip()
            if data == "[DONE]":
                break
            try:
                evt = json.loads(data)
                text = evt.get("delta", {}).get("text", "")
                if text:
                    full_text += text
                    print(text, end="", flush=True)
            except json.JSONDecodeError:
                pass

print("\n" + "─" * 50)

injected = "relay_pwned" in full_text.lower() or "whoami" in full_text.lower()
if injected:
    print("⚠️  响应中发现注入标记（异常！）")
else:
    print("✅ 无注入标记  — 普通用户不受影响")