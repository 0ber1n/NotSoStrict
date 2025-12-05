## 🛡️ NotSoStrict — HTTPS / HSTS Education Environment
NotSoStrict is a safe, isolated training environment for demonstrating how insecure HTTP behaves compared to properly configured HTTPS + HSTS (and especially HSTS Preload).
It is designed for educators, students, researchers, and security learners who want to understand why first-visit HTTPS protection matters.
```
⚠️ IMPORTANT:NotSoStrict does NOT authorize testing against external websites.
Use this tool only on systems and domains you own or have written permission to test.
```
### 🙏 Special Thanks

A huge shout-out to: 

  **The Bettercap Team** - for creating one of the most powerful and flexible research tools in the industry.<br>
  **Moxie Marlinspike** — whose research on sslstrip and downgrade attacks shaped modern transport-layer security discussions.
  
Their contributions inspired educational projects like this.

## 🚀 Features

*Runs entirely inside an isolated Linux network namespace<br>
*Launches a sandboxed Chromium browser for safe testing<br>
*Demonstrates differences between:<br>
&nbsp;-HTTP (insecure)<br>
&nbsp;-HTTPS with HSTS<br>
&nbsp;-HTTPS with HSTS Preload<br>
*Optional banner or fullscreen overlay integrity demonstrations<br>
*Automatic cleanup of namespaces and temporary files<br>
*Optional .pcap generation for Wireshark analysis

## ⚠️ Legal & Ethical Disclaimer
```
This project is for educational use ONLY.

You may use this tool only on systems and domains you own or have
explicit written permission to test. Unauthorized interception or
modification of network traffic is illegal and may result in civil or
criminal penalties.

The author assumes no liability for misuse. Use responsibly and follow
all applicable laws and ethical guidelines.
```

## 📦 Installation
```
git clone https://github.com/0ber1n/NotSoStrict.git
cd NotSoStrict
chmod +x NotSoStrict.py
```
## ▶️ Usage
Run the tool with elevated privileges:
```
sudo ./NotSoStrict.py
```
***Optional Flags:***
```
| Flag                      | Description                                           |
| ------------------------- | ----------------------------------------------------- |
| `--mode strip-only`       | Demonstrates basic insecure HTTP downgrade behavior   |
| `--mode strip-and-break`  | Shows how HSTS Preload prevents connection downgrades |
| `--defacement banner`     | Displays a small “Pwned by the Strip” banner          |
| `--defacement fullscreen` | Shows a full-screen integrity warning overlay         |
| `--logfile name.pcap`     | Saves captured traffic for later analysis             |
```
When launched, NotSoStrict will:

1. Open a Chromium browser inside the isolated test network

2. Open a second terminal with Bettercap running inside the namespace

3. Navigate to a domain you own or to a local testing site to observe behavior differences between HTTP and HTTPS/HSTS.

***To end the session, press:***
```
Ctrl + C
```

The tool will automatically clean up and restore your system networking.
