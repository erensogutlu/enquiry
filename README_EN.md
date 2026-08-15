# 🔍 ENQUIRY — Social Media OSINT Intelligence Tool

[Türkçe](README.md) | [English](README_EN.md)

```
    ███████╗███╗   ██╗ ██████╗ ██╗   ██╗██╗██████╗ ██╗   ██╗
    ██╔════╝████╗  ██║██╔═══██╗██║   ██║██║██╔══██╗╚██╗ ██╔╝
    █████╗  ██╔██╗ ██║██║   ██║██║   ██║██║██████╔╝ ╚████╔╝ 
    ██╔══╝  ██║╚██╗██║██║▄▄ ██║██║   ██║██║██╔══██╗  ╚██╔╝  
    ███████╗██║ ╚████║╚██████╔╝╚██████╔╝██║██║  ██║   ██║   
    ╚══════╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝   ╚═╝   
```

An open-source intelligence (OSINT) tool designed to collect information from social media usernames, email addresses, phone numbers, IP/domain targets, and image files. Fully compatible with Kali Linux and Python 3.8+.

---

## ⚡ Features

| Feature | Description |
|---|---|
| **Username Search** | Asynchronous username scan across 110+ platforms |
| **Email Intelligence** | MX records, Gravatar, GitHub, reputation checks |
| **Phone Number Analysis** | Country, carrier, line type, format details |
| **IP / Domain Analysis** | WHOIS, DNS, GeoIP, port scanning |
| **Image Metadata (EXIF)** | GPS coordinates, camera info, capture date |
| **Profile Scanning** | GitHub, Reddit, Steam, Lichess, Hacker News profiles |
| **Comprehensive Scan** | Run all modules simultaneously in a single command |
| **Report Generation** | Professional reports in JSON and HTML formats |
| **Rich Terminal Output** | Tables, panels, progress bars |
| **Interactive + CLI Mode** | Menu-driven or parameter-based usage |

---

## 🚀 Installation

### Kali Linux (Recommended)

```bash
git clone https://github.com/erensogutlu/enquiry.git
cd enquiry
chmod +x kurulum.sh
sudo bash kurulum.sh
```

### Other Linux Distributions / Windows / macOS

```bash
pip3 install -r requirements.txt
```

### Python Version Compatibility

| Python Version | Status |
|---|---|
| Python 3.8 | [+] Supported |
| Python 3.9 | [+] Supported |
| Python 3.10 | [+] Supported |
| Python 3.11 | [+] Supported |
| Python 3.12 | [+] Supported |
| Python 3.13+ | [+] Supported |

---

## 💻 Usage — Step-by-Step Guide

There are **2 ways** to use Enquiry:

1. **Interactive Mode** → Select options from an interactive menu. Ideal for beginners.
2. **Command Line Mode (CLI)** → Run directly using flags. Ideal for quick execution and scripts.

> 💡 **If no flags/parameters are provided**, Enquiry automatically launches Interactive Mode.

---

### 👤 1. Username Search (110+ Platforms)

**What does it do?** Searches your target username across 110+ platforms including Instagram, Twitter, GitHub, TikTok, and Steam. Checks every platform asynchronously for high performance.

**When to use it?** When you want to discover which platforms a specific username is registered on.

```bash
python3 enquiry.py -k johndoe
```

**Details:**
- `-k` or `--kullanici` → username to search
- The tool scans 110 platforms concurrently and lists profile URLs for matches.

**Example Output:**
```
┌────────────────────────── 🔍 Username Search ────────────────────────────┐
│ Username: johndoe                                                          │
│ Platform Count: 110                                                         │
└────────────────────────────────────────────────────────────────────────────┘
 ⚡ Scanning 110 platforms... ---------------------------------------- 100%

                             [+] Found Profiles
┌─────────────────┬──────────────┬─────────────────────────────────────────┐
│ Platform        │ Category     │ URL                                     │
├─────────────────┼──────────────┼─────────────────────────────────────────┤
│ Instagram       │ social_media │ https://www.instagram.com/johndoe       │
│ GitHub          │ developer    │ https://github.com/johndoe              │
│ Twitter/X       │ social_media │ https://x.com/johndoe                   │
│ Steam           │ gaming       │ https://steamcommunity.com/id/johndoe   │
│ ...             │ ...          │ ...                                     │
└─────────────────┴──────────────┴─────────────────────────────────────────┘

┌──────────────────────────────── 📊 Summary ─────────────────────────────────┐
│ [+] Found: 53  |  [-] Not Found: 57  |  📊 Total: 110                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 📧 2. Email Intelligence

**What does it do?** Checks services registered with the email address, fetches MX records, inspects Gravatar profile, scans GitHub accounts, and evaluates email reputation.

**When to use it?** When gathering intelligence on the person or organization behind an email address.

```bash
python3 enquiry.py -e user@gmail.com
```

**Parameter Breakdown:**

| Parameter | Input | Meaning |
|---|---|---|
| `-e` | `user@gmail.com` | Target email address to analyze |

**What happens during execution?**
1. Validates the email format
2. Queries MX records for the domain (Gmail servers, Outlook servers, etc.)
3. Identifies the email provider (Gmail, Outlook, ProtonMail, etc.)
4. Performs a Gravatar profile lookup
5. Searches GitHub for accounts registered under this email
6. Assesses email reputation (suspicious status, reference count, etc.)

**Example Output:**
```
                     Email Analysis Results
┌──────────────────────┬──────────────────────────────────────────┐
│ Key                  │ Value                                    │
├──────────────────────┼──────────────────────────────────────────┤
│ Email                │ user@gmail.com                           │
│ Username             │ user                                     │
│ Domain               │ gmail.com                                │
│ Provider             │ Google Workspace / Gmail                 │
│ Valid Format         │ [+] Yes                                  │
└──────────────────────┴──────────────────────────────────────────┘
                MX Records
┌─────────────────────────────────┬──────────┐
│ Mail Server                     │ Priority │
├─────────────────────────────────┼──────────┤
│ gmail-smtp-in.l.google.com      │ 5        │
│ alt1.gmail-smtp-in.l.google.com │ 10       │
└─────────────────────────────────┴──────────┘
```

---

### 📱 3. Phone Number Analysis

**What does it do?** Extracts country, carrier, line type (mobile/landline), valid formatting, and timezone from a target phone number.

**When to use it?** When identifying the country and telecom provider of an unknown phone number.

```bash
python3 enquiry.py -t +905551234567
```

**Details:**
- `-t` or `--telefon` → phone number to analyze
- Always input the number in **international format** (starting with `+` and country code)
- Examples: `+1` for USA, `+44` for UK, `+90` for Turkey, `+49` for Germany

**Example Output:**
```
               Phone Number Analysis Results
┌────────────────────────┬─────────────────────────────────────┐
│ Key                    │ Value                               │
├────────────────────────┼─────────────────────────────────────┤
│ Validity               │ [+] Valid                           │
│ International Format   │ +90 555 123 45 67                   │
│ National Format        │ 0555 123 45 67                      │
│ E.164 Format           │ +905551234567                       │
│ Country Code           │ +90                                 │
│ Country / Region       │ Turkey                              │
│ Carrier                │ Turk Telekom                        │
│ Line Type              │ mobile                              │
│ Timezone               │ Europe/Istanbul                     │
└────────────────────────┴─────────────────────────────────────┘
```

> ⚠️ **Invalid number format error?** Make sure to include the `+` sign and international country code (e.g. `+1`, `+90`).

---

### 🌐 4. IP / Domain Analysis

**What does it do?** Performs WHOIS lookup, DNS record analysis, GeoIP geolocation, and essential port scanning for an IP address or domain name.

**When to use it?** When inspecting network infrastructure, ownership, geographic location, open ports, or DNS configuration of a domain/IP.

**a) Domain analysis:**
```bash
python3 enquiry.py -i example.com
```

**b) IP address analysis:**
```bash
python3 enquiry.py -i 8.8.8.8
```

**Parameter Breakdown:**

| Parameter | Input | Meaning |
|---|---|---|
| `-i` | `example.com` or `8.8.8.8` | Target domain or IP address |

**What happens during execution?**
1. Domain target → Resolves IP address
2. IP target → Performs reverse DNS lookup
3. WHOIS lookup → Fetches domain/IP registration details
4. DNS queries → Fetches A, AAAA, MX, NS, TXT, CNAME, SOA records
5. GeoIP → Pinpoints geolocation (country, city, ISP, coordinates)
6. Port scanner → Scans 17 common ports (HTTP, HTTPS, SSH, FTP, MySQL, RDP, etc.)

**Example Output:**
```
                    GeoIP Location Info
┌────────────────────┬─────────────────────────────────────┐
│ 📍 Country         │ United States                       │
│ 🏙️ Region          │ California                          │
│ 🏙️ City            │ Mountain View                       │
│ 🏢 ISP             │ Google LLC                          │
│ 🌐 Coordinates     │ 37.4225, -122.085                   │
└────────────────────┴─────────────────────────────────────┘
                Open Ports
┌──────────┬─────────────────┬────────────┐
│ Port     │ Service         │ Status     │
├──────────┼─────────────────┼────────────┤
│ 80       │ HTTP            │ open       │
│ 443      │ HTTPS           │ open       │
└──────────┴─────────────────┴────────────┘
```

---

### 🖼️ 5. Image Metadata Analysis (EXIF)

**What does it do?** Extracts hidden EXIF metadata embedded inside image files, including GPS coordinates, camera model, lens settings, creation timestamp, and software details.

**When to use it?** When attempting to locate where and when a photograph was taken and with what device.

```bash
python3 enquiry.py -g /path/to/photo.jpg
```

**Details:**
- `-g` or `--gorsel` → absolute or relative path to the image file
- Supports common image formats including JPEG, PNG, and TIFF
- Generates a Google Maps link if GPS coordinates are present

**Example Output:**
```
                 File Info
┌──────────────────────┬─────────────────────────────────────┐
│ File Name            │ photo.jpg                           │
│ Format               │ JPEG                                │
│ Dimensions           │ 4032x3024                           │
│ File Size            │ 3.45 MB                             │
└──────────────────────┴─────────────────────────────────────┘
┌──────────────────────────── [!] GPS Location ───────────────────────────┐
│ 📍 GPS Coordinates Found!                                            │
│                                                                        │
│ Latitude: 41.008238                                                    │
│ Longitude: 28.978359                                                   │
│ 🗺️ Google Maps: https://www.google.com/maps?q=41.008238,28.978359     │
└────────────────────────────────────────────────────────────────────────┘
```

> [!] **Caution:** GPS metadata reveals precise geographic locations where photos were captured. Always process sensitive media responsibly.

---

### 🔎 6. Social Media Profile Scanning

**What does it do?** Queries target usernames directly via API endpoints for GitHub, Reddit, Steam, Lichess, and Hacker News. Unlike general username searches, it fetches **detailed profile data** (bio, follower counts, repositories, karma, etc.).

**When to use it?** When you need in-depth platform-specific user telemetry, activity metrics, and account history.

```bash
python3 enquiry.py -p torvalds
```

**Details:**
- `-p` or `--profil` → username to profile-scan
- **GitHub API:** Name, bio, location, company, repository count, followers, recent repositories
- **Reddit API:** Karma breakdown, premium status, moderation status
- **Steam:** Display name, online status
- **Lichess:** Game statistics, ratings
- **Hacker News:** Karma points, about description

**Example Output:**
```
                            GitHub Profile
┌────────────────────┬─────────────────────────────────────────────────┐
│ 👤 Name            │ Linus Torvalds                                  │
│ 📍 Location        │ Portland, OR                                    │
│ 🏢 Company         │ Linux Foundation                                │
│ 📊 Statistics      │ 📦 12 repos  |  👥 310495 followers  |  👤 0 following│
│ 📅 Account Created │ 2011-09-03                                      │
└────────────────────┴─────────────────────────────────────────────────┘
                               Recent Repositories
┌──────────────────────┬────────────┬────────┬──────────────────────────┐
│ Repository           │ Language   │ ⭐ Stars│ Description              │
├──────────────────────┼────────────┼────────┼──────────────────────────┤
│ linux                │ C          │ 238567 │ Linux kernel source tree │
│ AudioNoise           │ C          │ 4425   │ Random digital audio...  │
└──────────────────────┴────────────┴────────┴──────────────────────────┘
```

---

### 🔥 7. Comprehensive Scan (All Modules)

**What does it do?** Runs all applicable intelligence modules against a single target username in one execution: 110+ platform search + profile deep scans.

**When to use it?** When performing complete target profiling to gather maximum available open-source intelligence.

```bash
python3 enquiry.py --kapsamli johndoe
```

> 💡 This scan may take a few minutes as it concurrently queries 110+ platforms and 5 platform APIs.

---

### 📑 8. Report Generation (Saving Results)

Save scan results automatically in **JSON** or **HTML** report formats:

**a) Save as JSON report:**
```bash
python3 enquiry.py -k johndoe -r json
```

**b) Save as HTML report (viewable in any web browser):**
```bash
python3 enquiry.py -k johndoe -r html
```

**c) Save as both JSON and HTML:**
```bash
python3 enquiry.py -k johndoe -r ikisi
```

**d) Saving in Interactive Mode:**
Upon completing a scan in interactive mode, Enquiry will prompt:
```
💾 Save results as a report? [y/n/json/html/both]:
```

Reports are automatically saved into the `raporlar/` directory with timestamped filenames such as `enquiry_rapor_20260706_153000.json`.

---

### ❓ 9. Help Menu

To view the CLI options and short descriptions:

```bash
python3 enquiry.py -h
```

---

## 🎯 Quick Start — Example Workflow

If you're starting from scratch, run these commands:

```bash
# Step 1: Install dependencies
pip3 install -r requirements.txt

# Step 2: Launch interactive mode (menu-driven)
python3 enquiry.py

# Step 3: Or perform a quick username scan
python3 enquiry.py -k target_username

# Step 4: Run a profile deep scan
python3 enquiry.py -p target_username

# Step 5: Analyze an email address
python3 enquiry.py -e target@gmail.com

# Step 6: Run a comprehensive scan and export both report formats
python3 enquiry.py --kapsamli target_username -r ikisi
```

---

## 🛠️ CLI Parameter Reference

| Long Flag | Short Flag | Required? | Description |
|---|---|---|---|
| `--kullanici` | `-k` | No | Search username across 110+ platforms |
| `--eposta` | `-e` | No | Gather intelligence on an email address |
| `--telefon` | `-t` | No | Analyze phone number details |
| `--ip` | `-i` | No | Perform IP / Domain analysis |
| `--gorsel` | `-g` | No | Extract image EXIF metadata |
| `--profil` | `-p` | No | Deep-scan social media profiles |
| `--kapsamli` | — | No | Run comprehensive multi-module analysis |
| `--rapor` | `-r` | No | Export format: `json`, `html`, or `ikisi` (both) |
| `--surum` | — | No | Show version information |
| `-h` | — | No | Display help menu |

> 💡 **Launching without arguments** opens the interactive terminal UI.

---

## 📁 Project Structure

```
enquiry/
├── enquiry.py              ← Main entry point (CLI + Interactive Menu)
├── moduller/
│   ├── __init__.py         ← Package init
│   ├── kullanici_adi.py    ← 110+ platform async username search module
│   ├── eposta.py           ← Email intelligence module
│   ├── telefon.py          ← Phone number analysis module
│   ├── ip_domain.py        ← IP/Domain analysis module (WHOIS, DNS, GeoIP)
│   ├── gorsel_meta.py      ← Image EXIF/metadata extraction module
│   ├── profil_tarama.py    ← Social media profile deep-scan module
│   └── rapor.py            ← JSON/HTML report generator module
├── veriler/
│   ├── platformlar.json    ← 110 platform URL templates & categories
│   └── eposta_servisleri.json ← Email service API metadata
├── raporlar/               ← Generated reports (created automatically)
├── requirements.txt        ← Python dependencies
├── kurulum.sh              ← Kali Linux automated setup script
├── README.md               ← Documentation (Turkish)
└── README_EN.md            ← Documentation (English)
```

---

## ❓ Frequently Asked Questions (FAQ)

**Q: Why am I getting an error when entering a phone number?**  
Ensure the phone number is formatted in international format with a leading `+` and country code. Example: `+12125551234` (US), `+905551234567` (TR). Entering local numbers like `05551234567` without a country code will fail validation.

**Q: Why does username search take time?**  
Enquiry scans 110 platforms concurrently. Scans usually finish in 15–30 seconds depending on network bandwidth and target response times. Occasional timeouts on certain platforms are normal behavior.

**Q: Are all "Found" profiles guaranteed to be accurate?**  
Enquiry checks for standard HTTP 200 responses. Certain anti-bot or wildcard endpoints may return HTTP 200 for non-existent users (false positives). Always manually verify matched profile links.

**Q: Does email analysis require API keys?**  
Core features (MX records, Gravatar, GitHub lookups) work out of the box without API keys.

**Q: Where are generated reports stored?**  
All exports are written to the `raporlar/` directory with timestamped filenames like `enquiry_rapor_20260706_153000.json`.

**Q: Can Enquiry decrypt encrypted traffic or passwords?**  
No. Enquiry only queries publicly accessible data. It does not exploit vulnerabilities, crack hashes, or perform unauthorized access.

**Q: Does it work on Windows?**  
Yes. You can execute `python enquiry.py` in PowerShell or CMD.

---

## ⚠️ Legal Disclaimer

This tool is created **strictly for educational and lawful OSINT research**.  
Enquiry only collects publicly available data — no unauthorized access or exploitation is attempted.  
Users are **solely responsible** for ensuring compliance with local and international laws when utilizing this tool.  
The developers assume no liability for any misuse or damage caused by this software.

---

## 📜 License

This project is intended for educational purposes.

---

**Developer:** Eren  
**Version:** 1.0.0  
**Platform:** Kali Linux / Python 3.8+
