import pyfiglet
import dns.resolver
import requests
import whois
import socket
import sys
import time
import json
import os
from bs4 import BeautifulSoup

# Global Configuration & Styling
RED = '\033[31m'
YELLOW = '\033[33m'
RESET = '\033[0m'
GREY = '\033[90m'
GREEN = '\033[32m'
CYAN = '\033[36m'

class HydraRecon:
    """
    Advanced OSINT Framework by NorthForge Systems.
    Designed for professional intelligence gathering and reconnaissance.
    """
    def __init__(self, target):
        self.target = self._normalize_target(target)
        self.ip = self._resolve_ip()
        self.resolver = self._init_resolver()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) HYDRA-RECON/3.0'}

    def _normalize_target(self, target):
        return target.replace("https://", "").replace("http://", "").split("/")[0].strip()

    def _resolve_ip(self):
        try: return socket.gethostbyname(self.target)
        except: return None

    def _init_resolver(self):
        res = dns.resolver.Resolver()
        res.nameservers = ['8.8.8.8', '1.1.1.1']
        res.timeout = 2
        res.lifetime = 2
        return res

    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        f = pyfiglet.Figlet(font='slant')
        print(RED + f.renderText('HYDRA-RECON') + RESET)
        print(RED + "      [ Development By NorthForge Systems ]" + RESET)
        print(GREY + f"\n[!] Mission Target: {self.target} ({self.ip})" + RESET)
        print(GREY + "[!] Status: Operational | License: GPLv3\n" + RESET)

    # --- Intelligence Modules ---
    def dns_intelligence(self):
        print(f"{RED}[*] EXTRACTING DNS INTELLIGENCE...{RESET}")
        for rtype in ['A', 'MX', 'NS', 'TXT', 'SOA']:
            try:
                answers = self.resolver.resolve(self.target, rtype)
                print(f"  {YELLOW}[+]{RESET} {rtype}: {', '.join([str(x) for x in answers])}")
            except: pass

    def whois_audit(self):
        print(f"\n{RED}[*] RUNNING WHOIS AUDIT...{RESET}")
        try:
            w = whois.whois(self.target)
            print(f"  {YELLOW}[+]{RESET} Registrar: {w.registrar}")
            print(f"  {YELLOW}[+]{RESET} Created: {w.creation_date}")
            print(f"  {YELLOW}[+]{RESET} Organization: {w.org}")
        except: print(f"  {GREY}[-] WHOIS data protected or unreachable.{RESET}")

    def network_topology(self):
        print(f"\n{RED}[*] MAPPING NETWORK TOPOLOGY...{RESET}")
        if not self.ip: return
        try:
            r = requests.get(f"http://ip-api.com/json/{self.ip}", timeout=5).json()
            print(f"  {YELLOW}[+]{RESET} ASN: {r.get('as')}")
            print(f"  {YELLOW}[+]{RESET} ISP: {r.get('isp')}")
            print(f"  {YELLOW}[+]{RESET} Physical Location: {r.get('city')}, {r.get('country')}")
        except: pass

    def subdomain_ghosting(self):
        print(f"\n{RED}[*] SHADOWING SUBDOMAINS (SSL TRANSPARENCY)...{RESET}")
        try:
            url = f"https://crt.sh/?q=%.{self.target}&output=json"
            data = requests.get(url, timeout=12).json()
            subs = sorted(set(e['name_value'].lower() for e in data))
            print(f"  {YELLOW}[+]{RESET} Found {len(subs)} unique subdomains. Top results:")
            for s in subs[:12]: print(f"    - {s}")
        except: print(f"  {GREY}[-] SSL Log service timeout.{RESET}")

    def infra_fingerprint(self):
        print(f"\n{RED}[*] SNIFFING INFRASTRUCTURE FINGERPRINTS...{RESET}")
        try:
            r = requests.get(f"https://{self.target}", timeout=5, headers=self.headers)
            h = r.headers
            print(f"  {YELLOW}[+]{RESET} Server: {h.get('Server', 'Not Disclosed')}")
            print(f"  {YELLOW}[+]{RESET} Power: {h.get('X-Powered-By', 'Not Disclosed')}")
            
            # Cloud/CDN detection
            srv = h.get('Server', '').lower()
            cloud = "Independent/Legacy"
            if 'cloudflare' in srv: cloud = "Cloudflare"
            elif 'aws' in srv or 'amazon' in srv: cloud = "Amazon Web Services"
            elif 'google' in srv: cloud = "Google Cloud Platform"
            print(f"  {YELLOW}[+]{RESET} Infrastructure: {cloud}")
        except: pass

    def security_audit(self):
        print(f"\n{RED}[*] AUDITING SECURITY POLICIES...{RESET}")
        # Check files
        for f in ['robots.txt', 'security.txt', 'sitemap.xml']:
            try:
                r = requests.get(f"https://{self.target}/{f}", timeout=3, headers=self.headers)
                status = f"{GREEN}DETECTED{RESET}" if r.status_code == 200 else f"{GREY}HIDDEN{RESET}"
                print(f"  {YELLOW}[+]{RESET} /{f}: {status}")
            except: pass
        
        # Check Mail Security
        try:
            txt = self.resolver.resolve(self.target, 'TXT')
            for t in txt:
                if 'spf' in str(t).lower() or 'dmarc' in str(t).lower():
                    print(f"  {YELLOW}[+]{RESET} Mail Policy: {str(t)[:60]}...")
        except: pass

def main_menu():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        f = pyfiglet.Figlet(font='slant')
        print(RED + f.renderText('HYDRA-RECON') + RESET)
        print(RED + "      [ Development By NorthForge Systems ]" + RESET + "\n")
        
        target = input(f"{YELLOW}[?] Enter Target Domain: {RESET}").strip()
        if not target: return

        recon = HydraRecon(target)
        recon.banner()

        print(f"{CYAN}CHOOSE INTELLIGENCE STRATEGY:{RESET}")
        print(f"1. [PASSIVE]  DNS, WHOIS, Geolocation")
        print(f"2. [INFRA]    Subdomains, Tech-Stack, Cloud Detection")
        print(f"3. [FULL]     Execute All OSINT Modules (Recommended)")
        print(f"4. [CANCEL]   Abort Mission")

        choice = input(f"\n{RED}HYDRA > {RESET}").strip()

        if choice == '1':
            recon.dns_intelligence()
            recon.whois_audit()
            recon.network_topology()
        elif choice == '2':
            recon.subdomain_ghosting()
            recon.infra_fingerprint()
            recon.security_audit()
        elif choice == '3':
            recon.dns_intelligence()
            recon.whois_audit()
            recon.network_topology()
            recon.subdomain_ghosting()
            recon.infra_fingerprint()
            recon.security_audit()
        else:
            print(f"{RED}[!] Operation Cancelled.{RESET}")
            return

        print(f"\n{RED}[!] RECONNAISSANCE PROTOCOL COMPLETE.{RESET}")
        input("\nPress Enter to exit...")

    except KeyboardInterrupt:
        print(f"\n{RED}[!] Emergency Shutdown Initiated.{RESET}")
    except Exception as e:
        print(f"\n{RED}[!] Critical Error: {e}{RESET}")

if __name__ == "__main__":
    main_menu()
