#!/usr/bin/env python3
"""
Taak RESTCONF - End-to-end automatisering
Router: LAB-RA04-C02-R01 (172.17.4.65)
"""

import sys
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEVICE_IP  = "172.17.4.65"
USERNAME   = "admin"
PASSWORD   = "pxl"
BASE_URL   = "https://{}/restconf/data/Cisco-IOS-XE-native:native".format(DEVICE_IP)
HEADERS    = {
    "Content-Type": "application/yang-data+json",
    "Accept":       "application/yang-data+json",
}

GITHUB_URL = "https://raw.githubusercontent.com/BennyPetersPXL/yang/refs/heads/main/taak_restconf/taak_restconf_ios_xe_config.json"

def pretty_print_json(data):
    """Basisvaardigheid: JSON pretty-print via json.dumps met indent."""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        return json.dumps(data, indent=2)
    except Exception:
        return str(data)


def parse_json(data):
    """Basisvaardigheid: JSON response deserialiseren naar Python dictionary."""
    result = {}
    if "Cisco-IOS-XE-native:hostname" in data:
        result["hostname"] = data["Cisco-IOS-XE-native:hostname"]
    if "Cisco-IOS-XE-native:GigabitEthernet" in data:
        result["interfaces"] = [
            {
                "naam": i.get("name"),
                "ip":   i.get("ip", {}).get("address", {})
                         .get("primary", {}).get("address", "?")
            }
            for i in data["Cisco-IOS-XE-native:GigabitEthernet"]
        ]
    return result


def controleer_status(naam, response):
    """Basisvaardigheid: HTTP statuscodes controleren en tonen."""
    code = response.status_code
    if code in [200, 201, 204]:
        print("    HTTP {} - {} geslaagd".format(code, naam))
    else:
        print("    HTTP {} - {} mislukt".format(code, naam))
        print("    Details: {}".format(response.text[:200]))
        sys.exit(1)


def put(url, body):
    return requests.put(
        url, auth=(USERNAME, PASSWORD),
        headers=HEADERS, json=body,
        verify=False, timeout=15
    )


def verificatie(url, naam):
    """Basisvaardigheid: GET response ophalen, pretty-print en parsen."""
    r = requests.get(
        url, auth=(USERNAME, PASSWORD),
        headers=HEADERS, verify=False, timeout=15
    )
    print("\n    GET {} - HTTP {}".format(naam, r.status_code))
    if r.status_code == 200 and r.text:
        data = r.json()
        print("    Response (pretty-print JSON):")
        print("    " + "-" * 40)
        for regel in pretty_print_json(data).splitlines()[:15]:
            print("    " + regel)
        print("    " + "-" * 40)
        parsed = parse_json(data)
        if parsed:
            print("    Geparseerde datastructuur (Python dictionary):")
            for k, v in parsed.items():
                print("      {}: {}".format(k, v))


def main():
    print("=" * 45)
    print("Taak RESTCONF - {}".format(DEVICE_IP))
    print("=" * 45)

    # Stap 1: Config ophalen van GitHub (single source of truth)
    print("\n[1] Config ophalen van GitHub")
    try:
        r = requests.get(GITHUB_URL, timeout=15)
        r.raise_for_status()
        config = r.json()
    except Exception as e:
        sys.exit("FOUT: {}".format(e))
    print("    {} bytes opgehaald".format(len(r.text)))

    # Stap 2: Config parsen (deserialiseren: JSON naar Python dictionary)
    print("\n[2] Config parsen")
    print("    hostname:  {}".format(config["hostname"]))
    for intf in config["interfaces"]:
        print("    interface: Gi{} - {}".format(intf["name"], intf["address"]))

    # Stap 3: Hostname deployen
    print("\n[3] Hostname deployen via RESTCONF PUT")
    r = put("{}/hostname".format(BASE_URL),
            {"Cisco-IOS-XE-native:hostname": config["hostname"]})
    controleer_status("hostname", r)

    # Stap 4: Interfaces deployen
    print("\n[4] Interfaces deployen via RESTCONF PUT")
    for intf in config["interfaces"]:
        body = {"Cisco-IOS-XE-native:GigabitEthernet": [{
            "name":        intf["name"],
            "description": intf["description"],
            "ip": {"address": {"primary": {
                "address": intf["address"],
                "mask":    intf["mask"]
            }}}
        }]}
        r = put("{}/interface/GigabitEthernet={}".format(BASE_URL, intf["name"]), body)
        controleer_status("Gi{}".format(intf["name"]), r)

    # Stap 5: OSPF deployen
    print("\n[5] OSPF deployen via RESTCONF PUT")
    ospf = config["ospf"]
    body = {"Cisco-IOS-XE-ospf:ospf": [{
        "id":        ospf["id"],
        "router-id": ospf["router_id"],
        "network":   [{"ip": n["ip"], "mask": n["mask"], "area": n["area"]}
                      for n in ospf["networks"]]
    }]}
    r = put("{}/router/ospf={}".format(BASE_URL, ospf["id"]), body)
    controleer_status("OSPF", r)

    # Stap 6: Verificatie via RESTCONF GET
    print("\n[6] Verificatie via RESTCONF GET")
    verificatie("{}/hostname".format(BASE_URL), "hostname")
    verificatie("{}/interface".format(BASE_URL), "interfaces")

    print("\nDeployment afgerond.")


if __name__ == "__main__":
    main()
