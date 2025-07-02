#!/usr/bin/env python3
# sslstrip_namespace.py
# Namespace setup, NAT, browser launch, diagnostics, and cleanup.

import subprocess
import time
import os

# Configuration
NAMESPACE = "victim"
VETH_HOST = "v_eth0"
VETH_NS = "a_eth0"
HOST_IP = "10.200.200.1"
NS_IP = "10.200.200.2"
SUBNET = "10.200.200.0/24"
BROWSE_URL = "http://neverssl.com" #This default is set as a good initial test, you can browser as needed.
CHROMIUM_PATH = "/usr/bin/chromium"

def run(cmd, check=True):
    print(f"[+] {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def setup_namespace():
    run(f"ip netns add {NAMESPACE}")
    run(f"ip link add {VETH_HOST} type veth peer name {VETH_NS}")
    run(f"ip link set {VETH_NS} netns {NAMESPACE}")
    run(f"ip addr add {HOST_IP}/24 dev {VETH_HOST}")
    run(f"ip link set {VETH_HOST} up")
    run(f"ip netns exec {NAMESPACE} ip addr add {NS_IP}/24 dev {VETH_NS}")
    run(f"ip netns exec {NAMESPACE} ip link set {VETH_NS} up")
    run(f"ip netns exec {NAMESPACE} ip route add default via {HOST_IP}")
    run(f'ip netns exec {NAMESPACE} bash -c "echo nameserver 1.1.1.1 > /etc/resolv.conf"')

def enable_nat():
    run("sysctl -w net.ipv4.ip_forward=1")
    run(f"iptables -t nat -A POSTROUTING -s {SUBNET} -j MASQUERADE")
    run(f"iptables -t nat -A PREROUTING -i {VETH_HOST} -p tcp --dport 80 -j REDIRECT --to-port 8080")
    run(f"iptables -t nat -A PREROUTING -i {VETH_HOST} -p tcp --dport 443 -j REDIRECT --to-port 8080")

def launch_chromium():
    print("[*] Launching Chromium in namespace...")
    os.system(f"xhost +SI:localuser:{os.getlogin()}")
    run(f"ip netns exec {NAMESPACE} runuser -u {os.getlogin()} -- {CHROMIUM_PATH} --no-sandbox {BROWSE_URL}", check=False)

def diagnostics():
    print("=== SSL Strip Diagnostic Checks ===")
    ipf = open("/proc/sys/net/ipv4/ip_forward").read().strip()
    print(f"[+] IP Forwarding: {'ENABLED' if ipf == '1' else 'DISABLED'}")
    run("iptables -t nat -L PREROUTING -n -v | grep dpt:80 || echo '[!] Missing dpt:80 redirect'")
    run("iptables -t nat -L PREROUTING -n -v | grep dpt:443 || echo '[!] Missing dpt:443 redirect'")
    run(f"ip netns exec {NAMESPACE} ping -c1 -W1 {HOST_IP}", check=False)
    run(f"ip netns exec {NAMESPACE} ping -c1 -W1 1.1.1.1", check=False)
    run(f"ip netns exec {NAMESPACE} getent hosts neverssl.com", check=False)
    run(f"ip netns exec {NAMESPACE} curl -v --max-time 3 http://neverssl.com", check=False)
    print("=== End Diagnostics ===")

def launch_bash_script_in_new_terminal(script_name):
    # Resolve full path of the Bash script in the same folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)

    subprocess.Popen([
        "x-terminal-emulator",
        "-e", f"sudo bash -c 'bash \"{script_path}\"; exec bash'"
    ])

def launch_python_script_in_new_terminal(script_name):
    # Resolve full path of the Python script in the same folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)

    # Open a new terminal, run the script with sudo, then drop into an interactive shell
    subprocess.Popen([
        "x-terminal-emulator", "-e",
        "bash", "-c",
        f"sudo python3 \"{script_path}\"; exec bash"
    ])

def cleanup():
    print("[*] Cleaning up...")
    run(f"ip netns delete {NAMESPACE}", check=False)
    run("iptables -t nat -F", check=False)

def main():
    try:
        setup_namespace()
        enable_nat()
        print("[*] Namespace and NAT are configured.")
        # input("[*] Now run './bettercap_launch.sh' in another terminal and press Enter when Bettercap is running...")
        #launch_bash_script_in_new_terminal("bettercap_launch.sh")
        launch_python_script_in_new_terminal("bettercap_launch.py")
        launch_chromium()
        diagnostics()
        input("[*] Press Enter to clean up and exit...")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
