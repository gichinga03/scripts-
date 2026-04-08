import subprocess

# Test if a binary is available on the local system
def is_binary_available(binary):
    return subprocess.call(["which", binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

# Try to copy text to clipboard (if pyperclip is installed)
def copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        print("[+] Payload copied to clipboard!")
    except ImportError:
        print("[!] pyperclip not installed. Clipboard copy not available.")

# Export payload to a file
def export_payload(payload, filename):
    with open(filename, 'w') as f:
        f.write(payload)
    print(f"[+] Payload saved to {filename}") 