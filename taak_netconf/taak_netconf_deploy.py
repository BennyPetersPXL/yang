#!/usr/bin/env python3
"""
Taak NETCONF - End-to-end automatisering
Router: LAB-RA04-C02-R01 (172.17.4.65)
"""

import sys
import paramiko
import requests
import xml.dom.minidom
import xml.etree.ElementTree as ET
from ncclient import manager
from ncclient.operations import RPCError

DEVICE = {
    "host":           "172.17.4.65",
    "port":           830,
    "username":       "admin",
    "password":       "pxl",
    "hostkey_verify": False,
    "timeout":        30,
    "device_params":  {"name": "iosxe"},
    "look_for_keys":  False,
    "allow_agent":    False,
}

GITHUB_URL = "https://raw.githubusercontent.com/BennyPetersPXL/yang/refs/heads/main/taak_netconf/taak_netconf_ios_xe_config.xml"

def pretty_print_xml(xml_string):
    """Basisvaardigheid: XML pretty-print via toprettyxml."""
    try:
        return xml.dom.minidom.parseString(xml_string).toprettyxml(indent="  ")
    except Exception:
        return xml_string


def parse_xml(xml_string):
    """Basisvaardigheid: XML deserialiseren naar Python dictionary."""
    ns = {"ios": "http://cisco.com/ns/yang/Cisco-IOS-XE-native"}
    root = ET.fromstring(xml_string)
    result = {}
    hostname = root.find(".//ios:hostname", ns)
    if hostname is not None:
        result["hostname"] = hostname.text
    result["interfaces"] = []
    for intf in root.findall(".//ios:GigabitEthernet", ns):
        naam = intf.find("ios:name", ns)
        ip   = intf.find(".//ios:address/ios:primary/ios:address", ns)
        result["interfaces"].append({
            "naam": naam.text if naam is not None else "?",
            "ip":   ip.text   if ip   is not None else "?",
        })
    return result


def ssh_patch():
    """Paramiko patch voor ssh-rsa keys op oudere Cisco toestellen."""
    oi = paramiko.Transport.__init__
    def patch(self, *a, **k):
        oi(self, *a, **k)
        self._preferred_keys = ["ssh-rsa", "rsa-sha2-256", "rsa-sha2-512"]
    paramiko.Transport.__init__ = patch


def verbind():
    """NETCONF verbinding openen via SSH poort 830."""
    ssh_patch()
    try:
        conn = manager.connect(**DEVICE)
    except Exception as e:
        sys.exit("FOUT - Verbinding mislukt: {}".format(e))
    print("    Verbonden, session-id: {}".format(conn.session_id))
    return conn


def deploy(conn, config_xml):
    """Candidate datastore: lock, edit-config, commit. Bij fout: discard-changes."""
    locked = False
    try:
        conn.lock(target="candidate")
        locked = True
        print("    Candidate locked")

        conn.edit_config(target="candidate", config=config_xml)
        print("    edit-config geslaagd")

        response = conn.commit()

        # Basisvaardigheid: NETCONF statusfeedback + pretty-print XML
        print("\n    NETCONF response (pretty-print XML):")
        print("    " + "-" * 40)
        for regel in pretty_print_xml(str(response)).splitlines():
            print("    " + regel)
        print("    " + "-" * 40)

        if "<ok" in str(response):
            print("    Statusfeedback: <ok/> ontvangen - commit geslaagd")

    except RPCError as e:
        # Basisvaardigheid: foutafhandeling met discard-changes
        print("FOUT - {}: {}".format(e.type, e.tag))
        conn.discard_changes()
        print("discard-changes uitgevoerd - running config ongewijzigd")
        sys.exit(1)

    finally:
        if locked:
            conn.unlock(target="candidate")
        conn.close_session()


def verificatie():
    """Basisvaardigheid: GET uitvoeren, pretty-print XML en parsen naar dictionary."""
    conn = verbind()
    filter_xml = """
    <filter type="subtree">
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <hostname/>
        <interface/>
      </native>
    </filter>"""

    resultaat = conn.get_config(source="running", filter=filter_xml)
    conn.close_session()

    # Pretty-print XML tonen
    print("\n    Running config (pretty-print XML):")
    print("    " + "-" * 40)
    for regel in pretty_print_xml(str(resultaat)).splitlines()[:20]:
        print("    " + regel)
    print("    " + "-" * 40)

    # Deserialiseren naar Python dictionary
    parsed = parse_xml(str(resultaat))
    print("\n    Geparseerde datastructuur (Python dictionary):")
    print("    hostname:  {}".format(parsed.get("hostname")))
    for intf in parsed.get("interfaces", []):
        print("    interface: Gi{} - {}".format(intf["naam"], intf["ip"]))


def main():
    print("=" * 45)
    print("Taak NETCONF - {}".format(DEVICE["host"]))
    print("=" * 45)

    # Stap 1: Config ophalen van GitHub (single source of truth)
    print("\n[1] Config ophalen van GitHub")
    try:
        r = requests.get(GITHUB_URL, timeout=15)
        r.raise_for_status()
    except Exception as e:
        sys.exit("FOUT: {}".format(e))
    print("    {} bytes opgehaald".format(len(r.text)))

    # Stap 2: Verbinding openen
    print("\n[2] NETCONF verbinding openen")
    conn = verbind()

    # Stap 3: Deployen via candidate datastore
    print("\n[3] Deployen via candidate datastore")
    deploy(conn, r.text)

    # Stap 4: Verificatie
    print("\n[4] Verificatie via NETCONF GET")
    verificatie()

    print("\nDeployment afgerond.")


if __name__ == "__main__":
    main()
