#!/usr/bin/env python3
"""
Taak NETCONF - Deploy hardware
Router: LAB-RA04-C02-R01 - 172.17.4.65
"""

import sys
import requests
import xml.dom.minidom
import xml.etree.ElementTree as ET
from ncclient import manager
from ncclient.operations import RPCError
import paramiko

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

print("=" * 44)
print("Taak NETCONF - {}".format(DEVICE["host"]))
print("=" * 44)


def pretty_print_xml(xml_string):
    """Basisvaardigheid: XML pretty-print via toprettyxml."""
    try:
        return xml.dom.minidom.parseString(xml_string).toprettyxml(indent="  ")
    except Exception:
        return xml_string


def parse_xml(xml_string):
    """Basisvaardigheid: XML deserialiseren naar Python dictionary."""
    ns = {"ios": "http://cisco.com/ns/yang/Cisco-IOS-XE-native"}
    try:
        root = ET.fromstring(xml_string)
    except Exception:
        return {}
    result = {}
    hostname = root.find(".//ios:hostname", ns)
    if hostname is not None:
        result["hostname"] = hostname.text
    result["interfaces"] = []
    for intf in root.findall(".//ios:GigabitEthernet", ns):
        naam = intf.find("ios:name", ns)
        ip   = intf.find(".//ios:address/ios:primary/ios:address", ns)
        result["interfaces"].append({
            "naam": "Gi" + (naam.text if naam is not None else "?"),
            "ip":   ip.text if ip is not None else "?",
        })
    return result


def ssh_patch():
    """Patch voor oudere IOS-XE ssh-rsa key exchange."""
    transport = paramiko.transport.Transport
    original  = transport._preferred_keys
    if "ssh-rsa" not in original:
        transport._preferred_keys = ["ssh-rsa"] + list(original)


# [1] Config ophalen van GitHub
print("\n[1] Config ophalen van GitHub")
r = requests.get(GITHUB_URL, timeout=10)
if r.status_code != 200:
    print("    FOUT: GitHub niet bereikbaar ({})".format(r.status_code))
    sys.exit(1)
xml_config = r.text
print("    {} bytes opgehaald".format(len(r.content)))


# [2] NETCONF verbinding openen
print("\n[2] NETCONF verbinding openen")
ssh_patch()
try:
    conn = manager.connect(**DEVICE)
    print("    Verbonden, session-id: {}".format(conn.session_id))
except Exception as e:
    print("    FOUT: {}".format(e))
    sys.exit(1)


# [3] Deployen via candidate datastore
print("\n[3] Deployen via candidate datastore")
try:
    conn.lock(target="candidate")
    print("    Candidate locked")

    conn.edit_config(target="candidate", config=xml_config)
    print("    edit-config geslaagd")

    reply = conn.commit()
    xml_reply = pretty_print_xml(str(reply))

    print("\n    NETCONF response (pretty-print XML):")
    print("    " + "-" * 38)
    for line in xml_reply.splitlines():
        print("    " + line)
    print("    " + "-" * 38)

    if "<ok/>" in str(reply):
        print("    Statusfeedback: <ok/> ontvangen - commit geslaagd")
    else:
        print("    FOUT: geen <ok/> ontvangen")
        conn.discard_changes()
        conn.unlock(target="candidate")
        sys.exit(1)

except RPCError as e:
    print("    RPC FOUT: {}".format(e))
    conn.discard_changes()
    conn.unlock(target="candidate")
    sys.exit(1)

conn.close_session()


# [4] Verificatie via NETCONF GET
print("\n[4] Verificatie via NETCONF GET")
ssh_patch()
try:
    conn2 = manager.connect(**DEVICE)
    print("    Verbonden, session-id: {}".format(conn2.session_id))

    filter_xml = """
<filter type="subtree">
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname/>
    <interface/>
  </native>
</filter>"""

    result = conn2.get(filter=filter_xml)
    xml_data = pretty_print_xml(str(result))

    print("\n    Running config (pretty-print XML):")
    print("    " + "-" * 38)
    for line in xml_data.splitlines()[:30]:
        print("    " + line)
    print("    " + "-" * 38)

    parsed = parse_xml(str(result))
    print("\n    Geparseerde datastructuur (Python dictionary):")
    print("    hostname: ", parsed.get("hostname", "?"))
    for intf in parsed.get("interfaces", []):
        print("    interface: {} - {}".format(intf["naam"], intf["ip"]))

    conn2.close_session()

except Exception as e:
    print("    Verificatie mislukt: {}".format(e))


print("\n" + "=" * 44)
print("Deployment afgerond.")
print("=" * 44)
