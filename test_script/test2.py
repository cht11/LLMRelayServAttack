import anthropic


client = anthropic.Anthropic(
    base_url="http://192.168.50.218:3000/api",
    api_key="cr_14023f302719b4ee810b22ac2868be186be73b8de901e56a8ba100fccbb1d46d",
)

message = client.messages.create(
    model="MiniMax-M2.5",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "写一个安装 nginx 的 bash 脚本"
                }
            ]
        }
    ]
)

for block in message.content:
    if block.type == "thinking":
        print(f"Thinking:\n{block.thinking}\n")
    elif block.type == "text":
        print(f"Text:\n{block.text}\n")