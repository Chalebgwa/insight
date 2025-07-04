# Insight Web Pentesting Suite

![Insight Banner](logo.png)  
*Advanced web security assessment toolkit for professionals*

## Overview

**Insight** is a comprehensive command-line web penetration testing suite designed for security professionals. It combines multiple scanning techniques into a unified, professional interface with advanced visualization features. With its polished terminal UI and powerful capabilities, Insight helps security teams conduct thorough web security assessments efficiently.

## Key Features

### 🛠️ Comprehensive Scanning Capabilities
- **Port Scanning**: Identify open ports and services
- **Subdomain Enumeration**: Discover hidden subdomains
- **Directory Bruteforcing**: Find hidden paths and files
- **SSL/TLS Analysis**: Detect certificate issues and vulnerabilities
- **Security Header Auditing**: Grade HTTP header security
- **Vulnerability Scanning**: Detect SQLi, XSS, and other common threats

### ✨ Professional Interface
- **Animated Progress Bars**: Real-time scanning visualization
- **Color-Coded Results**: Instant severity recognition
- **Bordered Tables**: Professional data presentation
- **Unicode Icons**: Modern status indicators
- **Executive Summary**: Quick overview of findings

### ⚡ Performance Optimized
- **Asynchronous Scanning**: Configurable concurrency
- **Smart Resource Management**: Efficient memory handling
- **Polite Scanning**: Respectful request throttling
- **Randomized User Agents**: Evade basic detection systems

## Installation

### Requirements
- Python 3.7+
- Pip package manager

### Quick Install
```bash
git clone https://github.com/yourusername/insight.git
cd insight
pip install -r requirements.txt
chmod +x insight.py
```

### Using Pip
```bash
pip install insight-pentest
```

## Usage

### Basic Scan
```bash
./insight.py -u https://target.com
```

### Full Assessment
```bash
./insight.py -u https://target.com \
  -d path/to/dir_wordlist.txt \
  -s path/to/subdomain_wordlist.txt \
  -p 80 443 8080 \
  -e .php .bak .old \
  -c 3 \
  -o report.json
```

### Command Options
| Option | Description | Default |
|--------|-------------|---------|
| `-u URL` | Target URL (required) | |
| `-d FILE` | Directory brute-force wordlist | |
| `-s FILE` | Subdomain enumeration wordlist | |
| `-p PORTS` | Ports to scan (space separated) | 21,22,80,443,... |
| `-e EXTS` | File extensions for brute-force | .php,.html,.txt |
| `-m MAX_TASKS` | Maximum concurrent tasks | 30 |
| `-c DEPTH` | Crawling depth | 2 |
| `-o FILE` | JSON output file | |

## Modules Overview

### 1. Port Scanner
- Scans 25+ common ports
- Service detection
- Real-time progress display

### 2. Subdomain Enumerator
- Wildcard DNS detection
- Concurrent DNS resolution
- Live results streaming

### 3. Directory Bruteforcer
- Customizable extensions
- Status code and size analysis
- Progress visualization

### 4. SSL/TLS Analyzer
- Certificate validation
- Vulnerability detection (POODLE, weak ciphers)
- Expiration monitoring
- Protocol analysis

### 5. Security Header Auditor
- Checks 8+ critical security headers
- Provides letter-grade assessment (A+ to F)
- Detailed compliance reporting

### 6. Vulnerability Scanner
- SQL injection pattern detection
- Cross-site scripting (XSS) indicators
- Path traversal vulnerabilities
- Command injection risks
- Sensitive data exposure

## Sample Output

### Port Scanning Results
```
✓ Port 22/tcp open (SSH)
✓ Port 80/tcp open (HTTP)
✓ Port 443/tcp open (HTTPS)
✗ Port 8080/tcp closed
```

### Security Header Grading
```
Security Header Score: 85.7% - A (Good)
```

### Vulnerability Summary
```
┌───────────────────────┬──────────────────────────────┬──────────────────────────┐
│ Type                  │ URL                          │ Vulnerability            │
├───────────────────────┼──────────────────────────────┼──────────────────────────┤
│ CONTENT               │ https://target.com/search    │ SQL Injection            │
│ URL                   │ https://target.com/profile?  │ XSS Vulnerability        │
└───────────────────────┴──────────────────────────────┴──────────────────────────┘
```

## Recommended Wordlists

For optimal results, use high-quality wordlists:
- [SecLists](https://github.com/danielmiessler/SecLists)
- [Assetnote Wordlists](https://wordlists.assetnote.io/)
- [fuzzdb](https://github.com/fuzzdb-project/fuzzdb)

Example setup:
```bash
git clone https://github.com/danielmiessler/SecLists.git
./insight.py -u https://target.com \
  -d SecLists/Discovery/Web-Content/raft-large-directories.txt \
  -s SecLists/Discovery/DNS/subdomains-top1million-5000.txt
```

## Contribution

We welcome contributions! Please follow these steps:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Disclaimer

> This tool is intended for security testing and educational purposes only. Always obtain proper authorization before scanning any systems. The developers assume no liability and are not responsible for any misuse or damage caused by this program.

## Support

For issues and feature requests, please [open an issue](https://github.com/chalebgwa/insight/issues).

---

**Insight Web Pentesting Suite** © 2025 - Security made visible  
[![GitHub Stars](https://img.shields.io/github/stars/chalebgwa/insight?style=social)](https://github.com/chalebgwa/insight) 
[![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)](https://python.org) 
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
