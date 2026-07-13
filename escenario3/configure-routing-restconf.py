#!/usr/bin/env python3
"""
configure-routing-restconf.py
─────────────────────────────────────────────────────
Script de automatizacion de la configuracion de
direccionamiento IP y encaminamiento IP estatico
mediante RESTCONF para el escenario:

  routing-testbed-ceos-and-xe /
  static-routing-scenario-restconf-template

Topologia:
  [LAN-1] -- r1 (IOS-XE) -- r2 (cEOS) -- [LAN-2]
                  |               |
                 r3 (cEOS) ───────┘
                  |
              [LAN-3]

Modelos YANG:
  r1: ietf-interfaces + Cisco-IOS-XE-native (XML)
  r2/r3: openconfig-interfaces +
         openconfig-network-instance (JSON)

Uso: python3 configure-routing-restconf.py
─────────────────────────────────────────────────────
"""

import requests
import json
import sys
import urllib3

# Deshabilitar advertencias de certificado autofirmado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIGURACIÓN DE ROUTERS

ROUTERS = {
    "r1": {
        "host": "clab-routing-testbed-r1",
        "port": 443,
        "user": "admin",
        "password": "admin",
        "type": "ios-xe",
    },
    "r2": {
        "host": "clab-routing-testbed-r2",
        "port": 5900,
        "user": "admin",
        "password": "admin",
        "type": "ceos",
    },
    "r3": {
        "host": "clab-routing-testbed-r3",
        "port": 5900,
        "user": "admin",
        "password": "admin",
        "type": "ceos",
    },
}

# PLAN DE DIRECCIONAMIENTO IP

# r1 (IOS-XE): GigabitEthernet2=LAN-1, GigabitEthernet3=r1<->r2, GigabitEthernet4=r1<->r3
R1_INTERFACES = [
    {"name": "GigabitEthernet2", "ip": "192.168.1.1", "prefix": 24},
    {"name": "GigabitEthernet3", "ip": "10.10.10.1",  "prefix": 30},
    {"name": "GigabitEthernet4", "ip": "10.10.11.1",  "prefix": 30},
]

# r2 (cEOS): Ethernet1=LAN-2, Ethernet2=r1<->r2, Ethernet3=r2<->r3
R2_INTERFACES = [
    {"name": "Ethernet1", "ip": "192.168.2.1", "prefix": 24},
    {"name": "Ethernet2", "ip": "10.10.10.2",  "prefix": 30},
    {"name": "Ethernet3", "ip": "10.10.12.1",  "prefix": 30},
]

# r3 (cEOS): Ethernet1=LAN-3, Ethernet2=r1<->r3, Ethernet3=r2<->r3
R3_INTERFACES = [
    {"name": "Ethernet1", "ip": "192.168.3.1", "prefix": 24},
    {"name": "Ethernet2", "ip": "10.10.11.2",  "prefix": 30},
    {"name": "Ethernet3", "ip": "10.10.12.2",  "prefix": 30},
]

# RUTAS ESTÁTICAS

R1_STATIC_ROUTES = [
    {"prefix": "192.168.2.0", "mask": "255.255.255.0", "next_hop": "10.10.10.2"},
    {"prefix": "192.168.3.0", "mask": "255.255.255.0", "next_hop": "10.10.11.2"},
]

R2_STATIC_ROUTES = [
    {"prefix": "192.168.1.0/24", "next_hop": "10.10.10.1"},
    {"prefix": "192.168.3.0/24", "next_hop": "10.10.12.2"},
]

R3_STATIC_ROUTES = [
    {"prefix": "192.168.1.0/24", "next_hop": "10.10.11.1"},
    {"prefix": "192.168.2.0/24", "next_hop": "10.10.12.1"},
]


# FUNCIONES AUXILIARES

def base_url(router):
    r = ROUTERS[router]
    return f"https://{r['host']}:{r['port']}/restconf"

def auth(router):
    r = ROUTERS[router]
    return (r["user"], r["password"])

def headers_xml():
    return {
        "Content-Type": "application/yang-data+xml",
        "Accept":       "application/yang-data+xml",
    }

def headers_json():
    return {
        "Content-Type": "application/yang-data+json",
        "Accept":       "application/yang-data+json",
    }

def log_ok(msg):
    print(f"  OK  {msg}")

def log_err(msg):
    print(f"  ERROR  {msg}", file=sys.stderr)

def patch(url, auth_tuple, headers, body, label):
    resp = requests.patch(url, auth=auth_tuple, headers=headers,
                          data=body, verify=False)
    if resp.status_code in (200, 201, 204):
        log_ok(label)
    else:
        log_err(f"{label} -> HTTP {resp.status_code}: {resp.text[:200]}")

def put(url, auth_tuple, headers, body, label):
    resp = requests.put(url, auth=auth_tuple, headers=headers,
                        data=body, verify=False)
    if resp.status_code in (200, 201, 204):
        log_ok(label)
    else:
        log_err(f"{label} -> HTTP {resp.status_code}: {resp.text[:200]}")


# CONFIGURACIÓN DE INTERFACES — r1 (IOS-XE)
# Modelo: ietf-interfaces / ietf-ip

def netmask_from_prefix(prefix):
    mask = (0xFFFFFFFF >> (32 - prefix)) << (32 - prefix)
    return ".".join([str((mask >> (8 * i)) & 0xFF) for i in [3, 2, 1, 0]])

def configure_interfaces_r1():
    print("[r1] Configurando interfaces (IOS-XE / ietf-interfaces)...")
    url = f"{base_url('r1')}/data/ietf-interfaces:interfaces"
    for iface in R1_INTERFACES:
        netmask = netmask_from_prefix(iface["prefix"])
        body = f"""<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>{iface["name"]}</name>
    <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
      <address>
        <ip>{iface["ip"]}</ip>
        <netmask>{netmask}</netmask>
      </address>
    </ipv4>
  </interface>
</interfaces>"""
        patch(url, auth("r1"), headers_xml(), body,
              f"{iface['name']} -> {iface['ip']}/{iface['prefix']}")


# CONFIGURACIÓN DE INTERFACES — r2/r3 (cEOS)
# Modelo: openconfig-interfaces

def configure_interfaces_ceos(router, interfaces):
    print(f"[{router}] Configurando interfaces (cEOS / OpenConfig)...")
    for iface in interfaces:
        url = (f"{base_url(router)}/data/openconfig-interfaces:interfaces"
               f"/interface={iface['name']}/subinterfaces/subinterface=0"
               f"/openconfig-if-ip:ipv4/addresses/address={iface['ip']}")
        body = json.dumps({
            "openconfig-if-ip:config": {
                "ip":            iface["ip"],
                "prefix-length": iface["prefix"]
            }
        })
        # Cambia PUT por PATCH
        patch(url, auth(router), headers_json(), body,
            f"{iface['name']} -> {iface['ip']}/{iface['prefix']}")


# RUTAS ESTÁTICAS — r1 (IOS-XE)
# Modelo: Cisco-IOS-XE-native

def configure_static_routes_r1():
    print("[r1] Configurando rutas estáticas (IOS-XE / native)...")
    url = f"{base_url('r1')}/data/Cisco-IOS-XE-native:native/ip"
    for route in R1_STATIC_ROUTES:
        body = f"""<ip xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
  <route>
    <ip-route-interface-forwarding-list>
      <prefix>{route["prefix"]}</prefix>
      <mask>{route["mask"]}</mask>
      <fwd-list>
        <fwd>{route["next_hop"]}</fwd>
      </fwd-list>
    </ip-route-interface-forwarding-list>
  </route>
</ip>"""
        patch(url, auth("r1"), headers_xml(), body,
              f"{route['prefix']}/{route['mask']} via {route['next_hop']}")


# RUTAS ESTÁTICAS — r2/r3 (cEOS)
# Modelo: openconfig-network-instance

def configure_static_routes_ceos(router, routes):
    print(f"[{router}] Configurando rutas estáticas (cEOS / OpenConfig)...")
    url = (f"{base_url(router)}/data/openconfig-network-instance:network-instances"
           f"/network-instance=default/protocols"
           f"/protocol=openconfig-policy-types%3ASTATIC,default")
    body = json.dumps({
        "openconfig-network-instance:config": {
            "identifier": "openconfig-policy-types:STATIC",
            "name":       "default"
        },
        "openconfig-network-instance:static-routes": {
            "static": [
                {
                    "prefix": r["prefix"],
                    "config": {"prefix": r["prefix"]},
                    "next-hops": {
                        "next-hop": [{
                            "index":  r["next_hop"],
                            "config": {
                                "index":    r["next_hop"],
                                "next-hop": r["next_hop"]
                            }
                        }]
                    }
                }
                for r in routes
            ]
        }
    })
    patch(url, auth(router), headers_json(), body,
          f"{len(routes)} rutas estaticas configuradas")



# MAIN

def main():
    print("=" * 55)
    print("  Configuracion automatica via RESTCONF")
    print("  Escenario: routing-testbed-ceos-and-xe")
    print("=" * 55)

    # Interfaces
    configure_interfaces_r1()
    configure_interfaces_ceos("r2", R2_INTERFACES)
    configure_interfaces_ceos("r3", R3_INTERFACES)

    # Rutas estáticas
    configure_static_routes_r1()
    configure_static_routes_ceos("r2", R2_STATIC_ROUTES)
    configure_static_routes_ceos("r3", R3_STATIC_ROUTES)

    print("" + "=" * 55)
    print("  Configuracion completada.")
    print("=" * 55)

if __name__ == "__main__":
    main()
