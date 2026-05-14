# Taak RESTCONF

Automatisering via RESTCONF/YANG op een Cisco IOS-XE router.

## Bestanden

- `taak_restconf_ios_xe_config.json` - YANG JSON configuratie (single source of truth)
- `taak_restconf_deploy.py` - Python deployment script

## Werkwijze

1. Script haalt JSON config op van GitHub
2. RESTCONF verbinding via HTTPS poort 443
3. Hostname, interfaces en OSPF deployen via PUT
4. HTTP statuscodes controleren per stap
5. Verificatie via RESTCONF GET

## Uitvoeren

```powershell
python taak_restconf_deploy.py
```
