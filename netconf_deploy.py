#!/usr/bin/env python3
import sys
import paramiko
import requests
from ncclient import manager
from ncclient.operations import RPCError

DEVICE = {
    "host":           "192.168.100.20",
    "port":           830,
    "username":       "cisco",
    "password":       "cisco123!",
    "hostkey_verify": False,
    "timeout":        30,
    "device_params":  {"name": "iosxe"},
    "look_for_keys":  False,
    "allow_agent":    False,
}

GITHUB_RAW_URL = "https://raw.githubusercontent.com/BennyPetersPXL/yang/refs/heads/main/ios_xe_config.xml"


def stap1_haal_config_op():
    print("[1/5] Config ophalen van GitHub ...")
    try:
        r = requests.get(GITHUB_RAW_URL, timeout=15)
        r.raise_for_status()
    except Exception as e:
        sys.exit(f"[FOUT] GitHub: {e}")
    print(f"      {len(r.text)} bytes opgehaald")
    return r.text


def stap2_verbind():
    print("[2/5] Verbinding maken ...")
    oi = paramiko.Transport.__init__
    def p(self, *a, **k):
        oi(self, *a, **k)
        self._preferred_keys = ["ssh-rsa", "rsa-sha2-256", "rsa-sha2-512"]
    paramiko.Transport.__init__ = p
    try:
        conn = manager.connect(**DEVICE)
    except Exception as e:
        sys.exit(f"[FOUT] {e}")
    print(f"      Verbonden (session: {conn.session_id})")
    return conn


def stap3_tot_5_deploy(conn, xml):
    locked = False
    try:
        print("[3/5] Locken ...")
        conn.lock(target="candidate")
        locked = True
        print("      Locked")
        print("[4/5] edit-config ...")
        conn.edit_config(target="candidate", config=xml)
        print("      OK")
        print("[5/5] Commit ...")
        conn.commit()
        print("      Commit geslaagd!")
    except RPCError as e:
        print(f"[FOUT] {e}")
        try:
            conn.discard_changes()
            print("      discard-changes OK")
        except Exception:
            pass
        sys.exit(1)
    finally:
        if locked:
            try:
                conn.unlock(target="candidate")
            except Exception:
                pass
        conn.close_session()


def main():
    print("=" * 50)
    print("  Task 36 - NETCONF/YANG Deployment")
    print("=" * 50)
    xml = stap1_haal_config_op()
    conn = stap2_verbind()
    stap3_tot_5_deploy(conn, xml)
    print("Deployment afgerond!")


if __name__ == "__main__":
    main()
