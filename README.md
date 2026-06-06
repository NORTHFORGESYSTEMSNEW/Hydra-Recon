# HYDRA-RECON v3.0

![License](https://img.shields.io/badge/License-GPLv3-red.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Development](https://img.shields.io/badge/Development-NorthForge%20Systems-black)

**HYDRA-RECON** is a high-performance OSINT (Open Source Intelligence) framework designed for silent reconnaissance. It aggregates data from multiple public sources to provide a comprehensive architectural overview of any target domain.

## Features
- **DNS Shadowing**: Recursive extraction of A, MX, NS, TXT, and SOA records.
- **SSL Transparency Ghosting**: Extracts subdomains from public certificate logs (crt.sh).
- **Network Topology**: Real-time ASN, ISP, and Geolocation mapping.
- **Reverse DNS (PTR)**: Resolves the PTR record for the target IP.
- **Surface Port Scanning**: Threaded probe of common service ports (FTP, SSH, HTTP, RDP, databases, ...).
- **Infrastructure Fingerprinting**: Detection of Cloud providers (AWS, Cloudflare, GCP) and server stacks.
- **WAF / CDN Detection**: Signature-based fingerprinting of shielding vendors (Cloudflare, Akamai, Sucuri, Imperva, Fastly, ...).
- **HTTP Security Header Audit**: Flags missing HSTS, CSP, X-Frame-Options, and other hardening headers.
- **Wayback Machine Recovery**: Pulls historical archived URLs from the Internet Archive CDX API.
- **Security Audit**: Automated discovery of robots.txt, security policies, and mail security (SPF/DMARC).
- **JSON Report Export**: Save the full structured intelligence output to a file for later analysis.
- **Scriptable CLI**: Run non-interactively with command-line flags for automation.

## Installation
```bash
git clone https://github.com/NORTHFORGESYSTEMSNEW/Hydra-Recon.git
cd Hydra-Recon
pip install -r requirements.txt
```

## Usage

### Interactive mode
```bash
python hydra_recon.py
```

### Scriptable (CLI) mode
```bash
# Full sweep against a target
python hydra_recon.py -t example.com

# Passive-only intelligence, no banner
python hydra_recon.py -t example.com --mode passive --no-banner

# Infrastructure modules and export a JSON report
python hydra_recon.py -t example.com --mode infra -o report.json
```

| Flag | Description |
|------|-------------|
| `-t`, `--target` | Target domain (skips the interactive prompt). |
| `-m`, `--mode` | Strategy to run: `passive`, `infra`, or `full` (default: `full`). |
| `-o`, `--output` | Write a structured JSON report to the given path. |
| `--no-banner` | Suppress the ASCII banner. |

## Legal Disclaimer & Responsibility
**NorthForge Systems** and its developers assume **ZERO LIABILITY** for the use of this tool. 
- This software is for **Educational and Authorized Security Research only**.
- Use against targets without explicit permission is illegal and strictly prohibited.
- The user is solely responsible for compliance with local and international laws.
- **By running this software, you agree that any legal consequences arising from its misuse fall entirely on the operator.**

## License
Distributed under the **GNU General Public License v3.0 (GPLv3)**. See `LICENSE` for more information.
