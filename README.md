## 🛡️ NotSoStrict — HTTPS / HSTS Education Environment

NotSoStrict is a safe, isolated training environment for demonstrating how insecure HTTP behaves compared to properly configured HTTPS + HSTS (and especially HSTS Preload).
It is designed for educators, students, researchers, and security learners who want to understand why first-visit HTTPS protection matters.

```
⚠️ IMPORTANT:
NotSoStrict does NOT authorize testing against external websites.
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

---

## 🆕 Version 3.0 — DNS HTTPS / SVCB Awareness

Modern browsers no longer rely solely on redirects or HSTS to upgrade connections.

NotSoStrict v3.0 introduces an optional DNS-based demonstration mode to show:

- How DNS HTTPS (type 65) and SVCB (type 64) records can remove the first-request downgrade window
- Why removing DNS signals alone does **not** guarantee downgrade
- How browser-side HTTPS upgrade heuristics now influence downgrade viability

---

## 🧠 DNS Mode (Optional)

When DNS mode is enabled:

- DNS HTTPS (type 65) and SVCB (type 64) records are suppressed
- A / AAAA records continue to resolve normally
- The victim browser sees DNS as *silent* about HTTPS

To isolate DNS behavior for teaching purposes, browser HTTPS upgrade heuristics are disabled **only while DNS mode is enabled**.

### Browser Features Disabled Only in DNS Mode

```
HttpsFirstMode
HttpsFirstBalancedModeAutoEnable
HttpsUpgrades
DnsOverHttps
UseDnsHttpsSvcbAlpn
```

These changes **do not weaken TLS** and model real-world environments such as captive portals,
enterprise-managed browsers, kiosks, and OT / ICS systems.

---

## ✅ Why This Demo Is Honest

NotSoStrict does not claim that downgrade attacks work universally.

Instead, it demonstrates:

- Why TLS stripping historically worked
- Why HSTS and preload permanently stop downgrade attacks
- Why DNS HTTPS / SVCB records close the early downgrade window
- Why modern browsers may still upgrade even when DNS is silent

What this demo does **not** claim:

- That TLS stripping works against HSTS or preload
- That DNS suppression alone forces downgrade
- That modern browsers are broken

This makes the project a faithful, real-world representation of modern transport security behavior.

---

## 🎯 Threat Model

**1. Legacy / Optional HTTPS**
- No HSTS
- No preload
- No DNS HTTPS records  
→ Downgrade behavior is observable

**2. Modern Public Internet**
- DNS HTTPS / SVCB present  
- Browser HTTPS-first heuristics active  
→ HTTP never occurs, downgrade fails

**3. Constrained / Managed Environments**
- Captive portals
- Enterprise-managed browsers
- Kiosks / OT systems
- Pre-login VPN or NAC environments  
→ Downgrade behavior may be observable again

---

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

### Dependencies

*Use the PreflightChecker.py to check if you have all dependencies*

This has only been tested and used on Debian so far.

**Core Packages**<br>
-Python 3 (standard library only)<br>
-iproute2 — provides ip for namespaces, veth pairs, routing<br>
-iptables — used for NAT and port redirection inside the lab<br>
-Bettercap v2.41.0 or higher — required for proxy + inject functionality<br>
-Chromium (chromium or chromium-browser) — isolated browser environment<br>
-xhost — allows the sandboxed Chromium instance to use the host X session<br>
-A terminal emulator available as x-terminal-emulator<br>
-sudo/root access — required for namespaces and NAT rules<br>

**Optional (Recommended) Tools**<br>
-Wireshark — for analyzing .pcap captures<br>
-curl — for diagnostics inside the namespace<br>
-iputils-ping — basic connectivity checks<br>

---

### 🐧 Ubuntu 24.04 Notes (Important)

- `dbus-x11` is **required** for Chromium to launch inside a network namespace:
```
sudo apt update
sudo apt install dbus-x11
```

- Chromium **must NOT be the Snap version** due to Snap sandbox isolation.

Install the APT version instead:

```
sudo snap remove chromium
sudo add-apt-repository ppa:xtradeb/apps -y
sudo apt update
```

Create pin file:
```
Package: *
Pin: release o=LP-PPA-xtradeb-apps
Pin-Priority: 1001
```

Install and verify:
```
sudo apt install chromium
which chromium
```

Expected:
```
/usr/bin/chromium
```

---

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
| `--dns-mode filter-https` | Suppresses DNS HTTPS / SVCB records                   |
| `--defacement banner`     | Displays a small “Pwned by the Strip” banner          |
| `--defacement fullscreen` | Shows a full-screen integrity warning overlay         |
| `--logfile name.pcap`     | Saves captured traffic for later analysis             |
```

When launched, NotSoStrict will:

1. Open a Chromium browser inside the isolated test network
2. Open a second terminal with Bettercap running inside the namespace
3. Navigate to a domain you own or to a local testing site to observe behavior differences between HTTP and HTTPS/HSTS

***To end the session, press:***
```
Ctrl + C
```

The tool will automatically clean up and restore your system networking.

## Visual Environment Diagram

                           +------------------------+
                           |        INTERNET        |
                           +-----------+------------+
                                       ^
                                       |
                              (NAT, routing, etc)
                                       |
                             +---------+----------+
                             |        HOST        |
                             |  (your real OS)    |
                             +---------+----------+
                                       |
                            Host veth: v_eth0 (10.200.100.1)
                                       |
                          iptables REDIRECT :80/:443 -> 8080
                                       |
                           +-----------v------------+
                           |      Bettercap        |
                           |   (HTTP proxy 8080)   |
                           +-----------+-----------+
                                       |
                          (acts as gateway / MITM only
                           for the isolated namespace)
                                       |
                ==============================================
                |        LINUX NETWORK NAMESPACE "victim"     |
                |                                             |
                |   +------------------------------+          |
                |   |        Chromium Browser      |          |
                |   |     (victim application)     |          |
                |   +---------------+--------------+          |
                |                   |                         |
                |      ns veth: a_eth0 (10.200.100.2)          |
                |                   |                         |
                +-------------------+-------------------------+

Key points:
- The victim namespace has its *own* network stack (interfaces, routes, DNS).
- Traffic from Chromium → a_eth0 → v_eth0 (host) never touches your normal host apps directly.
- On the host, iptables redirects only traffic from v_eth0 on TCP/80 (and optionally 443) into Bettercap.
- The rest of your host networking remains unaffected and isolated from the lab environment.
