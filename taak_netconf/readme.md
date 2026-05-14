# Taak NETCONF

Automatisering via NETCONF/YANG op een Cisco IOS-XE router.

## Bestanden

- `taak_netconf_ios_xe_config.xml` - YANG XML configuratie (single source of truth)
- `taak_netconf_deploy.py` - Python deployment script

## Werkwijze

1. Script haalt XML config op van GitHub
2. NETCONF verbinding via SSH poort 830
3. Config wordt gestagеd in de candidate datastore
4. Commit naar running config
5. Bij fout: discard-changes (atomaire rollback)
6. Verificatie via NETCONF GET

## Uitvoeren

```powershell
python taak_netconf_deploy.py
```
