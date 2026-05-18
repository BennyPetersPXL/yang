#!/usr/bin/env python3
"""
Taak RESTCONF - Deploy hardware
Router: LAB-RA04-C02-R01 - 172.17.4.65
"""

import sys
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEVICE_IP = "172.17.4.65"
USERNAME  = "admin"
PASSWORD  = "pxl"
BASE_URL  = "https://{}/restconf/data/Cisco-IOS-XE-native:native".format(DEVICE_IP)
HEADERS   = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json",
}

GITHUB_URL = "https://raw.githubusercontent.com/BennyPetersPXL/yang/refs/heads/main/taak_restconf/taak_restconf_ios_xe_config.json"

print("=" * 44)
print("Taak RESTCONF - {}".format(DEVICE_IP))
print("=" * 44)


# [1] Config ophalen van GitHub
print("\n[1] Config ophalen van GitHub")
r = requests.get(GITHUB_URL, timeout=10)
if r.status_code != 200:
    print("    FOUT: GitHub niet bereikbaar ({})".format(r.status_code))
    sys.exit(1)
print("    {} bytes opgehaald".format(len(r.content)))


# [2] Config parsen
print("\n[2] Config parsen")
config = r.json()
print("    hostname:  {}".format(config["hostname"]))
for intf in config["interfaces"]:
    print("    interface: {} - {}".format(intf["name"], intf["address"]))
print("    banner:    {}".format(config.get("banner", "-")))


def put(url, body):
    return requests.put(
        url, auth=(USERNAME, PASSWORD),
        headers=HEADERS, json=body,
        verify=False, timeout=15
    )


def controleer_status(naam, response):
    code = response.status_code
    if code in [200, 201, 204]:
        print("    HTTP {} - {} geslaagd".format(code, naam))
    else:
        print("    HTTP {} - {} mislukt".format(code, naam))
        print("    Details: {}".format(response.text[:300]))
        sys.exit(1)


# [3] Hostname deployen
print("\n[3] Hostname deployen via RESTCONF PUT")
r = put("{}/hostname".format(BASE_URL),
        {"Cisco-IOS-XE-native:hostname": config["hostname"]})
controleer_status("hostname", r)


# [4] Banner deployen
print("\n[4] Banner deployen via RESTCONF PUT")
body = {
    "Cisco-IOS-XE-native:banner": {
        "motd": {"banner": config["banner"]}
    }
}
r = put("{}/banner".format(BASE_URL), body)
controleer_status("banner", r)


# [5] Interfaces deployen
print("\n[5] Interfaces deployen via RESTCONF PUT")
for intf in config["interfaces"]:
    naam = intf["name"]
    if naam.startswith("Loopback"):
        url = "{}/interface/Loopback={}".format(BASE_URL, naam.replace("Loopback", ""))
        body = {
            "Cisco-IOS-XE-native:Loopback": [{
                "name":        int(naam.replace("Loopback", "")),
                "description": intf["description"],
                "ip": {"address": {"primary": {
                    "address": intf["address"],
                    "mask":    intf["mask"]
                }}}
            }]
        }
    else:
        url = "{}/interface/GigabitEthernet={}".format(BASE_URL, naam.replace("/", "%2F"))
        body = {
            "Cisco-IOS-XE-native:GigabitEthernet": [{
                "name":        naam,
                "description": intf["description"],
                "ip": {"address": {"primary": {
                    "address": intf["address"],
                    "mask":    intf["mask"]
                }}}
            }]
        }
    r = put(url, body)
    controleer_status("interface {}".format(naam), r)


# [6] OSPF deployen
print("\n[6] OSPF deployen via RESTCONF PUT")
ospf = config["ospf"]
body = {
    "Cisco-IOS-XE-native:router": {
        "Cisco-IOS-XE-ospf:ospf": [{
            "id":        ospf["id"],
            "router-id": ospf["router_id"],
            "network":   [
                {"ip": n["ip"], "mask": n["mask"], "area": n["area"]}
                for n in ospf["networks"]
            ]
        }]
    }
}
r = put("{}/router".format(BASE_URL), body)
controleer_status("OSPF", r)


print("\n" + "=" * 44)
print("Deployment afgerond!")
print("=" * 44)
