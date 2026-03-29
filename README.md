# HYDRA-RECON v3.0

![License](https://img.shields.io/badge/License-GPLv3-red.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Development](https://img.shields.io/badge/Development-NorthForge%20Systems-black)

**HYDRA-RECON** is a high-performance OSINT (Open Source Intelligence) framework designed for silent reconnaissance. It aggregates data from multiple public sources to provide a comprehensive architectural overview of any target domain.

## Features
- **DNS Shadowing**: Recursive extraction of A, MX, NS, TXT, and SOA records.
- **SSL Transparency Ghosting**: Extracts subdomains from public certificate logs (crt.sh).
- **Network Topology**: Real-time ASN, ISP, and Geolocation mapping.
- **Infrastructure Fingerprinting**: Detection of Cloud providers (AWS, Cloudflare, GCP) and server stacks.
- **Security Audit**: Automated discovery of robots.txt, security policies, and mail security (SPF/DMARC).

## Installation
```bash
git clone https://github.com/yourusername/hydra-recon.git
cd hydra-recon
pip install -r requirements.txt
```

## Usage
```bash
python hydra_recon.py
```

## Legal Disclaimer & Responsibility
**NorthForge Systems** and its developers assume **ZERO LIABILITY** for the use of this tool. 
- This software is for **Educational and Authorized Security Research only**.
- Use against targets without explicit permission is illegal and strictly prohibited.
- The user is solely responsible for compliance with local and international laws.
- **By running this software, you agree that any legal consequences arising from its misuse fall entirely on the operator.**

## License
Distributed under the **GNU General Public License v3.0 (GPLv3)**. See `LICENSE` for more information.
