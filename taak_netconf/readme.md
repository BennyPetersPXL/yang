# Taak NETCONF - YANG configuratie deployment

## Beschrijving

Dit project automatiseert een volledige Cisco IOS-XE netwerkconfiguratie via **NETCONF** en **YANG**.
Het Python script haalt een XML configuratiebestand op van GitHub (single source of truth) en deployt
dit via NETCONF op een Cisco IOS-XE router.

---

## Bestanden

| Bestand | Beschrijving |
|---------|-------------|
| `taak_netconf_deploy.py` | Python script — haalt config op en deployt via NETCONF |
| `taak_netconf_ios_xe_config.xml` | YANG-gebaseerde XML configuratie (single source of truth) |
| `taak_netconf_deploy_test.py` | Testversie voor virtuele router (192.168.100.20) |
| `taak_netconf_ios_xe_config_test.xml` | Testconfiguratie voor virtuele router |

---

## Vereisten

### Software
- Python 3.x
- pip packages:
```bash
pip install ncclient requests paramiko
```

### Router
- Cisco IOS-XE met NETCONF ingeschakeld:
```
netconf-yang
ip ssh version 2
username admin privilege 15 secret pxl
```

---

## Gebruikte YANG modellen

| Configuratie | YANG model | Namespace |
|-------------|-----------|-----------|
| Hostname | Cisco-IOS-XE-native | http://cisco.com/ns/yang/Cisco-IOS-XE-native |
| Banner | Cisco-IOS-XE-native | http://cisco.com/ns/yang/Cisco-IOS-XE-native |
| Interfaces | Cisco-IOS-XE-native | http://cisco.com/ns/yang/Cisco-IOS-XE-native |
| Loopback | Cisco-IOS-XE-native | http://cisco.com/ns/yang/Cisco-IOS-XE-native |
| OSPF | Cisco-IOS-XE-ospf | http://cisco.com/ns/yang/Cisco-IOS-XE-ospf |

---

## Configuratie die gedeployd wordt

| Onderdeel | Waarde |
|-----------|--------|
| Hostname | LAB-RA04-C02-R01-NETCONF |
| Banner | Geconfigureerd via NETCONF - Network as Code |
| Interface GigabitEthernet0/0/1 | 10.199.65.108/27 |
| Loopback0 | 1.1.1.1/32 |
| OSPF router-id | 1.1.1.1 |
| OSPF area | 0 |

---

## Uitvoering

```bash
# Script downloaden van GitHub
curl -L -o taak_netconf_deploy.py \
  "https://raw.githubusercontent.com/BennyPetersPXL/yang/refs/heads/main/taak_netconf/taak_netconf_deploy.py"

# Uitvoeren
python3 taak_netconf_deploy.py
```

### Verwachte output
```
============================================
Taak NETCONF - 172.17.4.65
============================================

[1] Config ophalen van GitHub
    XXXX bytes opgehaald

[2] NETCONF verbinding openen
    Verbonden, session-id: XX

[3] Deployen via candidate datastore
    Candidate locked
    edit-config geslaagd
    Statusfeedback: <ok/> ontvangen - commit geslaagd

[4] Verificatie via NETCONF GET
    Verbonden, session-id: XX
    Running config (pretty-print XML): ...
    Geparseerde datastructuur (Python dictionary):
    hostname:  LAB-RA04-C02-R01-NETCONF
    interface: Gi0/0/1 - 10.199.65.108

============================================
Deployment afgerond.
============================================
```

---

## Werking van het script

### 1. Config ophalen van GitHub
Het script haalt het XML bestand automatisch op via een HTTP GET request.
GitHub fungeert als **single source of truth** — de config hoeft nooit manueel gekopieerd te worden.

### 2. NETCONF verbinding openen
Verbinding via SSH op poort 830 met `ncclient`. Een ssh-rsa patch zorgt voor
compatibiliteit met oudere IOS-XE versies.

### 3. Deployen via candidate datastore
- Candidate datastore wordt **gelockt** (atomaire operatie)
- `edit-config` stuurt de volledige XML config naar candidate
- `commit` zet de config over naar running
- De router bevestigt met `<ok/>`

### 4. Verificatie
Een tweede NETCONF sessie voert een `get` uit op de running config.
De response wordt **pretty-print** getoond als XML én geparsed naar een Python dictionary.

---

## Foutafhandeling

| Situatie | Actie |
|----------|-------|
| GitHub niet bereikbaar | Script stopt vóór verbinding |
| NETCONF RPC fout | `discard-changes` → `unlock` → script stopt |
| Onverwachte fout | `discard-changes` → `unlock` → script stopt |

De deployment is **atomair**: ofwel de volledige config wordt gecommit, ofwel niets.

---

## Aangetoonde vaardigheden

**Basisvaardigheden:**
- XML pretty-print via `toprettyxml`
- XML deserialiseren naar Python dictionary
- NETCONF `<ok/>` statusfeedback verwerken
- GitHub als single source of truth

**Additionele vaardigheden:**
- End-to-end automatisering via NETCONF
- Candidate datastore met atomaire commit
- Foutafhandeling met `discard-changes`
- Python als automatiseringstaal
