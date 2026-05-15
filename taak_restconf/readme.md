# Taak RESTCONF - YANG configuratie deployment

## Beschrijving

Dit project automatiseert een volledige Cisco IOS-XE netwerkconfiguratie via **RESTCONF** en **YANG**.
Het Python script haalt een JSON configuratiebestand op van GitHub (single source of truth) en deployt
dit via RESTCONF HTTP PUT requests op een Cisco IOS-XE router.

---

## Bestanden

| Bestand | Beschrijving |
|---------|-------------|
| `taak_restconf_deploy.py` | Python script — haalt config op en deployt via RESTCONF |
| `taak_restconf_ios_xe_config.json` | YANG-gebaseerde JSON configuratie (single source of truth) |
| `taak_restconf_deploy_test.py` | Testversie voor virtuele router (192.168.100.20) |
| `taak_restconf_ios_xe_config_test.json` | Testconfiguratie voor virtuele router |

---

## Vereisten

### Software
- Python 3.x
- pip packages:
```bash
pip install requests
```

### Router
- Cisco IOS-XE met RESTCONF ingeschakeld:
```
ip http server
ip http secure-server
restconf
username admin privilege 15 secret pxl
```

---

## Gebruikte YANG modellen

| Configuratie | YANG model | Namespace |
|-------------|-----------|-----------|
| Hostname | Cisco-IOS-XE-native | http://cisco.com/ns/yang/Cisco-IOS-XE-native |
| Banner | Cisco-IOS-XE-native | http://cisco.com/ns/yang/Cisco-IOS-XE-native |
| GigabitEthernet | Cisco-IOS-XE-native | http://cisco.com/ns/yang/Cisco-IOS-XE-native |
| Loopback | Cisco-IOS-XE-native | http://cisco.com/ns/yang/Cisco-IOS-XE-native |
| OSPF | Cisco-IOS-XE-ospf | http://cisco.com/ns/yang/Cisco-IOS-XE-ospf |

---

## Configuratie die gedeployd wordt

| Onderdeel | Waarde |
|-----------|--------|
| Hostname | LAB-RA04-C02-R01-RESTCONF |
| Banner | Geconfigureerd via RESTCONF - Network as Code |
| Interface GigabitEthernet0/0/1 | 10.199.65.108/27 |
| Loopback1 | 2.2.2.2/32 |
| OSPF router-id | 2.2.2.2 |
| OSPF area | 0 |

---

## Uitvoering

```bash
# Script downloaden van GitHub
curl -L -o taak_restconf_deploy.py \
  "https://raw.githubusercontent.com/BennyPetersPXL/yang/refs/heads/main/taak_restconf/taak_restconf_deploy.py"

# Uitvoeren
python3 taak_restconf_deploy.py
```

### Verwachte output
```
============================================
Taak RESTCONF - 172.17.4.65
============================================

[1] Config ophalen van GitHub
    XXXX bytes opgehaald

[2] Config parsen
    hostname:  LAB-RA04-C02-R01-RESTCONF
    interface: 0/0/1 - 10.199.65.108
    interface: Loopback1 - 2.2.2.2
    banner:    Geconfigureerd via RESTCONF - Network as Code

[3] Hostname deployen via RESTCONF PUT
    HTTP 204 - hostname geslaagd

[4] Banner deployen via RESTCONF PUT
    HTTP 204 - banner geslaagd

[5] Interfaces deployen via RESTCONF PUT
    HTTP 204 - interface 0/0/1 geslaagd
    HTTP 201 - interface Loopback1 geslaagd

[6] OSPF deployen via RESTCONF PUT
    HTTP 204 - OSPF geslaagd

============================================
Deployment afgerond!
============================================
```

---

## Werking van het script

### 1. Config ophalen van GitHub
Het script haalt het JSON bestand automatisch op via een HTTP GET request.
GitHub fungeert als **single source of truth** — de config hoeft nooit manueel gekopieerd te worden.

### 2. Config parsen
Het JSON bestand wordt gedeserialiseerd naar een Python dictionary.
Alle onderdelen (hostname, banner, interfaces, OSPF) worden uitgelezen en getoond.

### 3-6. Deployen via RESTCONF PUT
Elk onderdeel wordt apart gedeployd via een HTTPS PUT request naar het juiste YANG pad:

| Stap | RESTCONF pad |
|------|-------------|
| Hostname | `/restconf/data/Cisco-IOS-XE-native:native/hostname` |
| Banner | `/restconf/data/Cisco-IOS-XE-native:native/banner` |
| GigabitEthernet | `/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={id}` |
| Loopback | `/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback={id}` |
| OSPF | `/restconf/data/Cisco-IOS-XE-native:native/router` |

---

## HTTP statuscodes

| Code | Betekenis |
|------|-----------|
| 200 | OK — resource opgehaald |
| 201 | Created — nieuwe resource aangemaakt (bv. nieuwe Loopback) |
| 204 | No Content — bestaande resource bijgewerkt |
| 401 | Unauthorized — verkeerde credentials |
| 404 | Not Found — YANG pad bestaat niet |

---

## Foutafhandeling

| Situatie | Actie |
|----------|-------|
| GitHub niet bereikbaar | Script stopt vóór deployment |
| HTTP 4xx/5xx | Foutmelding getoond + script stopt |

---

## Verschil met NETCONF

| | NETCONF | RESTCONF |
|-|---------|----------|
| Transport | SSH poort 830 | HTTPS poort 443 |
| Formaat | XML | JSON |
| Operatie | edit-config + commit | HTTP PUT per onderdeel |
| Datastore | Candidate → Running | Rechtstreeks Running |
| Atomair | Ja (candidate commit) | Nee (per PUT request) |

---

## Aangetoonde vaardigheden

**Basisvaardigheden:**
- JSON pretty-print via `json.dumps`
- JSON deserialiseren naar Python dictionary
- HTTP statuscodes verwerken en tonen
- GitHub als single source of truth

**Additionele vaardigheden:**
- End-to-end automatisering via RESTCONF
- HTTPS PUT requests per YANG pad
- Python als automatiseringstaal
