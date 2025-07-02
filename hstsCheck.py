#!/usr/bin/env python3
import argparse
import csv
import re
import sys

import requests

def parse_hsts(header: str):
    """Return (max_age, includeSubDomains, preload), with 'X' if missing."""
    max_age = "X"
    inc = "X"
    pre = "X"

    m = re.search(r"max-age\s*=\s*([0-9]+)", header, re.IGNORECASE)
    if m:
        max_age = m.group(1)

    if re.search(r"includesubdomains", header, re.IGNORECASE):
        inc = "Yes"

    if re.search(r"preload", header, re.IGNORECASE):
        pre = "Yes"

    return max_age, inc, pre

def check_url(url: str, timeout: float = 10.0):
    try:
        # HEAD may be faster; fall back to GET if no HSTS in HEAD
        r = requests.head(url, allow_redirects=True, timeout=timeout)
        hsts = r.headers.get("Strict-Transport-Security", "")
        if not hsts:
            r = requests.get(url, allow_redirects=True, timeout=timeout)
            hsts = r.headers.get("Strict-Transport-Security", "")
        if not hsts:
            return ("X", "X", "X")
        return parse_hsts(hsts)
    except Exception:
        return ("X", "X", "X")

def main():
    parser = argparse.ArgumentParser(
        description="Check URLs for HSTS directives and output CSV"
    )
    parser.add_argument("urls_file", help="File with one URL per line")
    args = parser.parse_args()

    writer = csv.writer(sys.stdout)
    writer.writerow(["url", "max-age", "includeSubDomains", "preload"])

    with open(args.urls_file) as f:
        for line in f:
            url = line.strip()
            if not url or url.startswith("#"):
                continue
            # ensure scheme
            if not re.match(r"https?://", url, re.IGNORECASE):
                url = "https://" + url
            max_age, inc, pre = check_url(url)
            writer.writerow([url, max_age, inc, pre])

if __name__ == "__main__":
    main()
