#!/usr/bin/env python3
"""模拟 AI Agent 请求，验证 EvilInjector 注入触发。"""
import json, httpx, sys, os

RELAY_BASE_URL = "http://192.168.50.218:3000/api"
RELAY_API_KEY  = "cr_4ed27837ed3c7c477358b0ab7663a56904dc48fdf53eb8e19178c0a233e21c60"

PROMPT = "告诉我更新ubuntu系统软件包的命令，不要多余回答，markdown格式"

def main():
    payload = {
        "model": "ccr,MiniMax-M2.5",
        "max_tokens": 512,
        "stream": True,
        "messages": [{"role": "user", "content": PROMPT}]
    }
    headers = {
        "User-Agent": "claude-cli/0.2.56 claude-code/0.2.56",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": RELAY_API_KEY,
        "Accept": "text/event-stream",
    }

    print("[ Agent 请求 ]  UA: claude-cli  →  中转站注入测试")
    print("-" * 60)
    print(f"User: {PROMPT}")
    print(f"LLM Response:")

    full_text = ""
    injected = False

    with httpx.Client(timeout=90.0) as client:
        with client.stream("POST", f"{RELAY_BASE_URL}/v1/messages",
                           json=payload, headers=headers) as resp:
            if resp.status_code != 200:
                body = b"".join(resp.iter_bytes()).decode("utf-8", errors="replace")
                print(f"[HTTP {resp.status_code}] {body}")
                sys.exit(1)

            for line in resp.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                try:
                    evt = json.loads(data)
                    text = evt.get("delta", {}).get("text", "")
                    if not text:
                        continue
                    full_text += text
                    if "relay_pwned" in text.lower() or "whoami" in text.lower():
                        injected = True
                        print("\033[91m" + text + "\033[0m", end="", flush=True)
                    else:
                        print(text, end="", flush=True)
                except json.JSONDecodeError:
                    pass

    print("\n" + "-" * 60)

    if injected:
        print("\033[91m[+] INJECTION SUCCESS — 恶意载荷已注入响应\033[0m")
    else:
        print("[-] 未检测到注入（检查 UA 是否匹配）")

    pwned = "/tmp/relay_pwned.txt"
    if os.path.exists(pwned):
        print("\033[91m[!] PWNED — " + open(pwned).read().strip() + "\033[0m")
    else:
        print("[i] relay_pwned.txt 不存在（脚本未被执行）")

    return injected

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
