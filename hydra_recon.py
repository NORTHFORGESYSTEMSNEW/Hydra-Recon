import pyfiglet
import dns.resolver
import requests
import whois
import socket
import sys
import json
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date, timezone

# Global Configuration & Styling
RED = '\033[31m'
YELLOW = '\033[33m'
RESET = '\033[0m'
GREY = '\033[90m'
GREEN = '\033[32m'
CYAN = '\033[36m'

# Common ports probed during surface mapping
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB',
    3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL', 6379: 'Redis',
    8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
}

# Recommended HTTP security headers and what they protect against
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'Enforces HTTPS (HSTS)',
    'Content-Security-Policy': 'Mitigates XSS / injection',
    'X-Frame-Options': 'Clickjacking protection',
    'X-Content-Type-Options': 'MIME-sniffing protection',
    'Referrer-Policy': 'Controls referrer leakage',
    'Permissions-Policy': 'Restricts browser features',
}

# Fingerprints used to identify WAF / CDN vendors from response headers
WAF_SIGNATURES = {
    'cloudflare': 'Cloudflare',
    'cf-ray': 'Cloudflare',
    'akamai': 'Akamai',
    'x-akamai': 'Akamai',
    'sucuri': 'Sucuri',
    'x-sucuri-id': 'Sucuri',
    'incapsula': 'Imperva Incapsula',
    'x-iinfo': 'Imperva Incapsula',
    'barracuda': 'Barracuda',
    'awselb': 'AWS ELB / WAF',
    'x-amz-cf-id': 'AWS CloudFront',
    'fastly': 'Fastly',
    'x-fastly': 'Fastly',
}


def _json_default(obj):
    """Make whois/datetime objects JSON serializable."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


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
        self.results = {
            'target': self.target,
            'ip': self.ip,
            'scanned_at': datetime.now(timezone.utc).isoformat(),
        }

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
        records = {}
        for rtype in ['A', 'MX', 'NS', 'TXT', 'SOA']:
            try:
                answers = self.resolver.resolve(self.target, rtype)
                values = [str(x) for x in answers]
                records[rtype] = values
                print(f"  {YELLOW}[+]{RESET} {rtype}: {', '.join(values)}")
            except: pass
        self.results['dns'] = records

    def whois_audit(self):
        print(f"\n{RED}[*] RUNNING WHOIS AUDIT...{RESET}")
        try:
            w = whois.whois(self.target)
            print(f"  {YELLOW}[+]{RESET} Registrar: {w.registrar}")
            print(f"  {YELLOW}[+]{RESET} Created: {w.creation_date}")
            print(f"  {YELLOW}[+]{RESET} Organization: {w.org}")
            self.results['whois'] = {
                'registrar': w.registrar,
                'creation_date': w.creation_date,
                'organization': w.org,
            }
        except:
            print(f"  {GREY}[-] WHOIS data protected or unreachable.{RESET}")
            self.results['whois'] = None

    def network_topology(self):
        print(f"\n{RED}[*] MAPPING NETWORK TOPOLOGY...{RESET}")
        if not self.ip: return
        try:
            r = requests.get(f"http://ip-api.com/json/{self.ip}", timeout=5).json()
            print(f"  {YELLOW}[+]{RESET} ASN: {r.get('as')}")
            print(f"  {YELLOW}[+]{RESET} ISP: {r.get('isp')}")
            print(f"  {YELLOW}[+]{RESET} Physical Location: {r.get('city')}, {r.get('country')}")
            self.results['network'] = {
                'asn': r.get('as'),
                'isp': r.get('isp'),
                'city': r.get('city'),
                'country': r.get('country'),
            }
        except: pass

    def reverse_dns(self):
        print(f"\n{RED}[*] RESOLVING REVERSE DNS (PTR)...{RESET}")
        if not self.ip:
            print(f"  {GREY}[-] No IP available for reverse lookup.{RESET}")
            return
        try:
            host = socket.gethostbyaddr(self.ip)[0]
            print(f"  {YELLOW}[+]{RESET} PTR: {host}")
            self.results['reverse_dns'] = host
        except:
            print(f"  {GREY}[-] No PTR record found.{RESET}")
            self.results['reverse_dns'] = None

    def port_scan(self):
        print(f"\n{RED}[*] SCANNING SURFACE PORTS...{RESET}")
        if not self.ip:
            print(f"  {GREY}[-] No IP available for port scan.{RESET}")
            return
        open_ports = []

        def _probe(port):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            try:
                if s.connect_ex((self.ip, port)) == 0:
                    return port
            except: pass
            finally:
                s.close()
            return None

        with ThreadPoolExecutor(max_workers=20) as pool:
            futures = {pool.submit(_probe, p): p for p in COMMON_PORTS}
            for fut in as_completed(futures):
                port = fut.result()
                if port:
                    open_ports.append(port)

        if open_ports:
            for port in sorted(open_ports):
                print(f"  {YELLOW}[+]{RESET} {port}/tcp OPEN ({COMMON_PORTS[port]})")
        else:
            print(f"  {GREY}[-] No common ports responded.{RESET}")
        self.results['open_ports'] = {p: COMMON_PORTS[p] for p in sorted(open_ports)}

    def subdomain_ghosting(self):
        print(f"\n{RED}[*] SHADOWING SUBDOMAINS (SSL TRANSPARENCY)...{RESET}")
        try:
            url = f"https://crt.sh/?q=%.{self.target}&output=json"
            data = requests.get(url, timeout=12).json()
            subs = sorted(set(e['name_value'].lower() for e in data))
            print(f"  {YELLOW}[+]{RESET} Found {len(subs)} unique subdomains. Top results:")
            for s in subs[:12]: print(f"    - {s}")
            self.results['subdomains'] = subs
        except:
            print(f"  {GREY}[-] SSL Log service timeout.{RESET}")
            self.results['subdomains'] = []

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
            self.results['infrastructure'] = {
                'server': h.get('Server', 'Not Disclosed'),
                'x_powered_by': h.get('X-Powered-By', 'Not Disclosed'),
                'cloud': cloud,
            }
        except: pass

    def waf_detection(self):
        print(f"\n{RED}[*] PROBING FOR WAF / CDN SHIELDING...{RESET}")
        try:
            r = requests.get(f"https://{self.target}", timeout=5, headers=self.headers)
            blob = ' '.join(f"{k}:{v}" for k, v in r.headers.items()).lower()
            detected = sorted({vendor for sig, vendor in WAF_SIGNATURES.items() if sig in blob})
            if detected:
                for vendor in detected:
                    print(f"  {YELLOW}[+]{RESET} Shield Detected: {vendor}")
            else:
                print(f"  {GREY}[-] No known WAF/CDN signature found.{RESET}")
            self.results['waf'] = detected
        except:
            print(f"  {GREY}[-] WAF probe unreachable.{RESET}")
            self.results['waf'] = []

    def http_security_headers(self):
        print(f"\n{RED}[*] AUDITING HTTP SECURITY HEADERS...{RESET}")
        try:
            r = requests.get(f"https://{self.target}", timeout=5, headers=self.headers)
            present, missing = {}, []
            for header, purpose in SECURITY_HEADERS.items():
                if header in r.headers:
                    present[header] = r.headers[header]
                    print(f"  {YELLOW}[+]{RESET} {header}: {GREEN}PRESENT{RESET} ({purpose})")
                else:
                    missing.append(header)
                    print(f"  {YELLOW}[+]{RESET} {header}: {RED}MISSING{RESET} ({purpose})")
            self.results['security_headers'] = {'present': present, 'missing': missing}
        except:
            print(f"  {GREY}[-] Security header probe unreachable.{RESET}")
            self.results['security_headers'] = None

    def wayback_history(self):
        print(f"\n{RED}[*] RECOVERING WAYBACK MACHINE ARTIFACTS...{RESET}")
        try:
            url = (
                "http://web.archive.org/cdx/search/cdx"
                f"?url={self.target}/*&output=json&fl=original&collapse=urlkey&limit=15"
            )
            data = requests.get(url, timeout=10).json()
            urls = [row[0] for row in data[1:]] if data else []
            if urls:
                print(f"  {YELLOW}[+]{RESET} Archived {len(urls)} unique paths. Sample:")
                for u in urls[:12]:
                    print(f"    - {u}")
            else:
                print(f"  {GREY}[-] No archived snapshots found.{RESET}")
            self.results['wayback'] = urls
        except:
            print(f"  {GREY}[-] Wayback Machine unreachable.{RESET}")
            self.results['wayback'] = []

    def security_audit(self):
        print(f"\n{RED}[*] AUDITING SECURITY POLICIES...{RESET}")
        files = {}
        # Check files
        for f in ['robots.txt', 'security.txt', 'sitemap.xml']:
            try:
                r = requests.get(f"https://{self.target}/{f}", timeout=3, headers=self.headers)
                detected = r.status_code == 200
                files[f] = detected
                status = f"{GREEN}DETECTED{RESET}" if detected else f"{GREY}HIDDEN{RESET}"
                print(f"  {YELLOW}[+]{RESET} /{f}: {status}")
            except: pass

        # Check Mail Security
        mail_policies = []
        try:
            txt = self.resolver.resolve(self.target, 'TXT')
            for t in txt:
                if 'spf' in str(t).lower() or 'dmarc' in str(t).lower():
                    mail_policies.append(str(t))
                    print(f"  {YELLOW}[+]{RESET} Mail Policy: {str(t)[:60]}...")
        except: pass
        self.results['security_audit'] = {'files': files, 'mail_policies': mail_policies}

    # --- Reporting ---
    def export_report(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(self.results, fh, indent=2, default=_json_default)
            print(f"\n{GREEN}[+] Report saved to: {path}{RESET}")
        except Exception as e:
            print(f"\n{RED}[!] Failed to write report: {e}{RESET}")


# --- Strategy orchestration ---
def run_passive(recon):
    recon.dns_intelligence()
    recon.whois_audit()
    recon.network_topology()
    recon.reverse_dns()


def run_infra(recon):
    recon.port_scan()
    recon.subdomain_ghosting()
    recon.infra_fingerprint()
    recon.waf_detection()
    recon.http_security_headers()
    recon.security_audit()
    recon.wayback_history()


def run_full(recon):
    run_passive(recon)
    run_infra(recon)


MODES = {'passive': run_passive, 'infra': run_infra, 'full': run_full}


def execute(target, mode, output=None, show_banner=True):
    recon = HydraRecon(target)
    if show_banner:
        recon.banner()
    MODES[mode](recon)
    if output:
        recon.export_report(output)
    print(f"\n{RED}[!] RECONNAISSANCE PROTOCOL COMPLETE.{RESET}")
    return recon


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog='hydra_recon',
        description='HYDRA-RECON v3.0 - OSINT reconnaissance framework by NorthForge Systems.',
    )
    parser.add_argument('-t', '--target', help='Target domain (skips interactive prompt).')
    parser.add_argument('-m', '--mode', choices=list(MODES), default='full',
                        help='Intelligence strategy to execute (default: full).')
    parser.add_argument('-o', '--output', help='Write structured JSON report to this path.')
    parser.add_argument('--no-banner', action='store_true', help='Suppress the ASCII banner.')
    return parser.parse_args(argv)


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
        print(f"1. [PASSIVE]  DNS, WHOIS, Geolocation, Reverse DNS")
        print(f"2. [INFRA]    Ports, Subdomains, Tech-Stack, WAF, Security Headers, Wayback")
        print(f"3. [FULL]     Execute All OSINT Modules (Recommended)")
        print(f"4. [CANCEL]   Abort Mission")

        choice = input(f"\n{RED}HYDRA > {RESET}").strip()

        if choice == '1':
            run_passive(recon)
        elif choice == '2':
            run_infra(recon)
        elif choice == '3':
            run_full(recon)
        else:
            print(f"{RED}[!] Operation Cancelled.{RESET}")
            return

        save = input(f"\n{YELLOW}[?] Save JSON report? (filename or blank to skip): {RESET}").strip()
        if save:
            recon.export_report(save)

        print(f"\n{RED}[!] RECONNAISSANCE PROTOCOL COMPLETE.{RESET}")
        input("\nPress Enter to exit...")

    except KeyboardInterrupt:
        print(f"\n{RED}[!] Emergency Shutdown Initiated.{RESET}")
    except Exception as e:
        print(f"\n{RED}[!] Critical Error: {e}{RESET}")


def main():
    args = parse_args(sys.argv[1:])
    if args.target:
        try:
            execute(args.target, args.mode, output=args.output, show_banner=not args.no_banner)
        except KeyboardInterrupt:
            print(f"\n{RED}[!] Emergency Shutdown Initiated.{RESET}")
        except Exception as e:
            print(f"\n{RED}[!] Critical Error: {e}{RESET}")
    else:
        main_menu()


if __name__ == "__main__":
    main()
