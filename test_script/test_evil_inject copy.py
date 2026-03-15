#!/usr/bin/env python3
"""
测试 EvilInjector：模拟 AI Agent 请求，验证注入是否成功触发。
使用 httpx 直接发送请求，完全控制请求头（避免 SDK 覆盖 User-Agent）。
"""
import json, httpx, sys, os

RELAY_BASE_URL = "http://192.168.50.218:3000/api"
RELAY_API_KEY  = "cr_4ed27837ed3c7c477358b0ab7663a56904dc48fdf53eb8e19178c0a233e21c60"

def test_agent_request():
    print("=" * 60)
    print("[TEST] 模拟 AI Agent 请求（claude-cli UA + tools 声明）")
    print("=" * 60)

    # 模拟 Claude Code 的典型请求体（包含 bash tool 声明）
    payload = {
        "model": "ccr,MiniMax-M2.5",
        "max_tokens": 512,
        "stream": True,
        "tools": [
            {
                "name": "bash",
                "description": "Run bash commands",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"}
                    },
                    "required": ["command"]
                }
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": (
                    # "Write a minimal bash script that does: 1) installs curl via apt-get, "
                    # "2) prints 'Done'. Output ONLY the script content, no explanation."
                    "写一个安装 nginx 的 bash 脚本"
                )
            }
        ]
    }

    headers = {
        # 完全模拟 Claude Code CLI 的请求头
        "User-Agent": "claude-cli/0.2.56 claude-code/0.2.56",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": RELAY_API_KEY,
        "Accept": "text/event-stream",
    }

    # print(f"\n[*] 发送请求到 {RELAY_BASE_URL}/v1/messages")
    # print(f"[*] User-Agent: {headers['User-Agent']}")
    # print(f"[*] 包含 bash tool 声明: ✓")
    # print(f"[*] 等待 SSE 流响应...\n")

    full_text = ""
    injected_lines = []

    with httpx.Client(timeout=90.0) as client:
        with client.stream(
            "POST",
            f"{RELAY_BASE_URL}/v1/messages",
            json=payload,
            headers=headers
        ) as response:
            print(f"[HTTP] Status: {response.status_code}")
            if response.status_code != 200:
                body = b"".join(response.iter_bytes()).decode("utf-8", errors="replace")
                print(f"[ERROR] {body}")
                return False

            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        print("\n[SSE] [DONE]")
                        break
                    try:
                        evt = json.loads(data_str)
                        if evt.get("type") == "content_block_delta":
                            text = evt.get("delta", {}).get("text", "")
                            full_text += text
                            if "relay_pwned" in text.lower() or "whoami" in text.lower():
                                injected_lines.append(text)
                                print(f"\n\033[91m[⚠️  INJECTED]\033[0m {repr(text)}")
                            else:
                                print(text, end="", flush=True)
                    except json.JSONDecodeError:
                        pass

    print("\n\n" + "=" * 60)
    print("[RESULT] 完整响应内容:")
    print("-" * 40)
    print(full_text)
    print("-" * 40)

    # if injected_lines:
    #     print(f"\n\033[91m✅ [INJECTION SUCCESS]\033[0m 注入成功！发现 {len(injected_lines)} 处注入内容")
    #     for line in injected_lines:
    #         print(f"  → {repr(line)}")
    # else:
    #     relay_pwned = "relay_pwned" in full_text.lower()
    #     whoami = "whoami" in full_text.lower()
    #     if relay_pwned or whoami:
    #         print("\n\033[91m✅ [INJECTION SUCCESS]\033[0m 注入内容在响应文本中检测到")
    #     else:
    #         print("\n⚠️  未在响应中找到注入标记")
    #         print("   请检查服务日志：grep EvilInjector /tmp/relay_service.log")

    return bool(injected_lines) or "relay_pwned" in full_text.lower()

def check_pwned_file():
    path = "/tmp/relay_pwned.txt"
    if os.path.exists(path):
        with open(path) as f:
            content = f.read().strip()
        print(f"\n\033[91m🔴 [PWNED]\033[0m {path} 文件存在！")
        print(f"内容：{content}")
    else:
        print(f"\n[INFO] {path} 不存在（脚本尚未被执行）")

if __name__ == "__main__":
    success = test_agent_request()
    # check_pwned_file()
    
    # 查看服务器注入日志
    # print("\n[*] 中转站注入日志：")
    # os.system("grep 'EvilInjector' /tmp/relay_service.log | tail -10")
    
    # sys.exit(0 if success else 1)
