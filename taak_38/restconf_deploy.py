#!/usr/bin/env python3
"""
Task 38 - RESTCONF/YANG Deployment
====================================
Haalt JSON config op van GitHub en deployt
via RESTCONF PUT op een Cisco IOS-XE toestel.
"""

import sys
import json
import requests
import urllib3

# SSL warnings uitschakelen (self-signed cert op CSR1000v)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ──────────────────────────────────────────────
# INSTELLINGEN
# ──────────────────────────────────────────────
DEVICE_IP  = "192.168.100.20"
USERNAME   = "cisco"
PASSWORD   = "cisco123!"

GITHUB_URL = "https://raw.githubusercontent.com/BennyPetersPXL/yang/refs/heads/main/taak_38/ios_xe_config.json"

RESTCONF_URL = f"https://{DEVICE_IP}/restconf/data/Cisco-IOS-XE-native:native"

HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json",
}
# ──────────────────────────────────────────────


def stap1_haal_config_op():
    print("\n[1/3] Config ophalen van GitHub ...")
    print(f"      URL: {GITHUB_URL}")
    try:
        r = requests.get(GITHUB_URL, timeout=15)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        sys.exit("[FOUT] Kan GitHub niet bereiken.")
    except requests.exceptions.HTTPError as e:
        sys.exit(f"[FOUT] GitHub HTTP fout: {e}")

    try:
        config = r.json()
    except json.JSONDecodeError:
        sys.exit("[FOUT] Opgehaald bestand is geen geldige JSON.")

    print(f"      ✓ Config opgehaald ({len(r.text)} bytes)")
    return config


def stap2_deploy(config):
    print(f"\n[2/3] Config deployen via RESTCONF PUT ...")
    print(f"      URL: {RESTCONF_URL}")

    try:
        r = requests.put(
            RESTCONF_URL,
            auth=(USERNAME, PASSWORD),
            headers=HEADERS,
            json=config,
            verify=False,
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        sys.exit("[FOUT] Kan router niet bereiken. Is RESTCONF actief?")
    except requests.exceptions.Timeout:
        sys.exit("[FOUT] Timeout bij verbinding met router.")

    stap3_controleer_status(r)


def stap3_controleer_status(response):
    print(f"\n[3/3] HTTP statuscode controleren ...")
    print(f"      Statuscode: {response.status_code}")

    if response.status_code in [200, 201, 204]:
        print("      ✓ Deployment geslaagd!")
        if response.text:
            print(f"      Response: {response.text[:200]}")
    elif response.status_code == 400:
        print(f"      [FOUT] Ongeldige config (400 Bad Request)")
        print(f"      Details: {response.text[:300]}")
        sys.exit(1)
    elif response.status_code == 401:
        sys.exit("[FOUT] Verkeerde credentials (401 Unauthorized)")
    elif response.status_code == 404:
        sys.exit("[FOUT] RESTCONF pad niet gevonden (404 Not Found)")
    elif response.status_code == 409:
        print(f"      [FOUT] Conflict in configuratie (409)")
        print(f"      Details: {response.text[:300]}")
        sys.exit(1)
    else:
        print(f"      [FOUT] Onverwachte statuscode: {response.status_code}")
        print(f"      Details: {response.text[:300]}")
        sys.exit(1)


def main():
    print("=" * 50)
    print("  Task 38 - RESTCONF/YANG Deployment")
    print(f"  CSR1000v: {DEVICE_IP}")
    print("=" * 50)

    config = stap1_haal_config_op()
    stap2_deploy(config)

    print("\n✅  Deployment volledig afgerond!")
    print("    Verifieer op de router:")
    print("    → show running-config")
    print("    → show ip interface brief")
    print("    → show ip ospf")


if __name__ == "__main__":
    main()
