import anthropic

client = anthropic.Anthropic(
    base_url="http://192.168.50.218:3000/api/v1/messages",
    # api_key="cr_14023f302719b4ee810b22ac2868be186be73b8de901e56a8ba100fccbb1d46d",
    api_key="cr_4ed27837ed3c7c477358b0ab7663a56904dc48fdf53eb8e19178c0a233e21c60"
)

message = client.messages.create(
    model="ccr,MiniMax-M2.5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}],
)

text = next(b.text for b in message.content if b.type == "text")

print("STATUS: OK")
print("MODEL:", message.model)
print("REPLY:", text)
print("TOKENS: in=%d out=%d" % (message.usage.input_tokens, message.usage.output_tokens))
