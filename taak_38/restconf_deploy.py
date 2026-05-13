#!/usr/bin/env python3
import sys
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEVICE_IP = "192.168.100.20"
USERNAME  = "cisco"
PASSWORD  = "cisco123"

GITHUB_URL = "https://raw.githubusercontent.com/BennyPetersPXL/yang/refs/heads/main/taak_38/ios_xe_config.json"

BASE_URL = f"https://{DEVICE_IP}/restconf/data/Cisco-IOS-XE-native:native"

HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json",
}

def log_status(naam, response):
    print(f"      Statuscode: {response.status_code}", end=" ")
    if response.status_code in [200, 201, 204]:
        print("✓")
    else:
        print(f"✗\n      [FOUT] {response.text[:300]}")
        sys.exit(1)

def stap1_haal_config_op():
    print("\n[1/4] Config ophalen van GitHub ...")
    try:
        r = requests.get(GITHUB_URL, timeout=15)
        r.raise_for_status()
        config = r.json()
    except Exception as e:
        sys.exit(f"[FOUT] GitHub: {e}")
    print(f"      ✓ {len(r.text)} bytes opgehaald")
    return config["Cisco-IOS-XE-native:native"]

def stap2_hostname(config):
    print("\n[2/4] Hostname deployen ...")
    r = requests.put(
        f"{BASE_URL}/hostname",
        auth=(USERNAME, PASSWORD),
        headers=HEADERS,
        json={"Cisco-IOS-XE-native:hostname": config["hostname"]},
        verify=False, timeout=15
    )
    log_status("hostname", r)

def stap3_interfaces(config):
    print("\n[3/4] Interfaces deployen ...")
    for intf in config["interface"]["GigabitEthernet"]:
        naam = intf["name"]
        print(f"      GigabitEthernet{naam} ...", end=" ")
        r = requests.put(
            f"{BASE_URL}/interface/GigabitEthernet={naam}",
            auth=(USERNAME, PASSWORD),
            headers=HEADERS,
            json={"Cisco-IOS-XE-native:GigabitEthernet": [intf]},
            verify=False, timeout=15
        )
        log_status(f"Gi{naam}", r)

def stap4_ospf(config):
    print("\n[4/4] OSPF deployen ...")
    ospf = config["router"]["Cisco-IOS-XE-ospf:ospf"]
    r = requests.put(
        f"{BASE_URL}/router/ospf=1",
        auth=(USERNAME, PASSWORD),
        headers=HEADERS,
        json={"Cisco-IOS-XE-ospf:ospf": ospf},
        verify=False, timeout=15
    )
    log_status("ospf", r)

def main():
    print("=" * 50)
    print("  Task 38 - RESTCONF/YANG Deployment")
    print(f"  CSR1000v: {DEVICE_IP}")
    print("=" * 50)

    config = stap1_haal_config_op()
    stap2_hostname(config)
    stap3_interfaces(config)
    stap4_ospf(config)

    print("\n✅  Deployment volledig afgerond!")
    print("    → show running-config")
    print("    → show ip interface brief")
    print("    → show ip ospf")

if __name__ == "__main__":
    main()
