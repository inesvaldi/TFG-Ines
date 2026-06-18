#!/usr/bin/env python3
"""
get_all_routers.py
Consulta direccionamiento IP y/o tabla de encaminamiento de TODOS los
routers del testbed static-routing en un solo comando.

Uso:
  python3 get_all_routers.py [--query interfaces|routes|all]
                              [--port <PUERTO>] [--user <USUARIO>] [--password <PASSWORD>]
                              [--only-ip] [--protocol static|rib|all]

Ejemplos:
  python3 get_all_routers.py
  python3 get_all_routers.py --query interfaces --only-ip
  python3 get_all_routers.py --query routes
  python3 get_all_routers.py --query routes --protocol rib
"""

import argparse
import subprocess
import sys
import requests
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()


# Nombres de los routers en containerlab

ROUTER_NAMES = ["r1", "r2", "r3"]
CLAB_PREFIX  = "clab-routing-testbed"

RESTCONF_BASE = "https://{host}:{port}/restconf/data"
HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json"
}


def get_router_ips():
    """Obtiene las IPs de gestion de los routers dinamicamente via docker inspect."""
    routers = {}
    for name in ROUTER_NAMES:
        try:
            result = subprocess.run(
                ["sudo", "docker", "inspect",
                 f"{CLAB_PREFIX}-{name}",
                 "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"],
                capture_output=True, text=True, timeout=5
            )
            ip = result.stdout.strip()
            if ip:
                routers[name] = ip
            else:
                print(f"[WARN] No se pudo obtener IP de {name}, comprueba que el testbed esta desplegado.")
        except Exception as e:
            print(f"[WARN] Error obteniendo IP de {name}: {e}")
    return routers


def restconf_get(host, port, user, password, path):
    url = RESTCONF_BASE.format(host=host, port=port) + path
    resp = requests.get(url, auth=HTTPBasicAuth(user, password),
                        headers=HEADERS, verify=False, timeout=10)
    resp.raise_for_status()
    return resp.json()


def query_interfaces(host, port, user, password, only_ip=False):
    data = restconf_get(host, port, user, password,
                        "/openconfig-interfaces:interfaces")
    ifaces = data.get("openconfig-interfaces:interface", [])
    results = []
    for iface in ifaces:
        name  = iface.get("name", "?")
        state = iface.get("state", {})
        admin = state.get("admin-status", "?")
        oper  = state.get("oper-status", "?")
        ips = []
        for sub in iface.get("subinterfaces", {}).get("subinterface", []):
            for addr in (sub.get("openconfig-if-ip:ipv4", {})
                            .get("addresses", {}).get("address", [])):
                ips.append(f"{addr.get('ip','')}/{addr.get('state',{}).get('prefix-length','')}")
            for addr in (sub.get("openconfig-if-ip:ipv6", {})
                            .get("addresses", {}).get("address", [])):
                ips.append(f"[v6]{addr.get('ip','')}/{addr.get('state',{}).get('prefix-length','')}")
        if only_ip and not ips:
            continue
        results.append({"name": name, "admin": admin, "oper": oper, "ips": ips})
    return results


def print_interfaces(ifaces):
    print(f"\n  {'Interfaz':<18} {'Admin':<8} {'Oper':<8} Direcciones IP")
    print(f"  {'-'*18} {'-'*8} {'-'*8} {'-'*25}")
    for i in ifaces:
        ip_str = ", ".join(i["ips"]) if i["ips"] else "(sin IP)"
        print(f"  {i['name']:<18} {i['admin']:<8} {i['oper']:<8} {ip_str}")


def query_static_routes(host, port, user, password, vrf="default"):
    data = restconf_get(host, port, user, password,
                        f"/openconfig-network-instance:network-instances"
                        f"/network-instance={vrf}/protocols"
                        f"/protocol=STATIC,STATIC/static-routes")
    routes = []
    for rt in data.get("openconfig-network-instance:static", []):
        prefix = rt.get("prefix", "?")
        for nh in rt.get("next-hops", {}).get("next-hop", []):
            gw = nh.get("config", {}).get("next-hop", "?")
            routes.append({"prefix": prefix, "protocol": "STATIC", "gateway": gw})
    return routes


def query_rib(host, port, user, password, vrf="default"):
    data = restconf_get(host, port, user, password,
                        f"/openconfig-network-instance:network-instances"
                        f"/network-instance={vrf}/afts")
    routes = []
    for entry in (data.get("openconfig-network-instance:afts", {})
                      .get("ipv4-unicast", {})
                      .get("fib-entries", {})
                      .get("fib-entry", [])):
        prefix  = entry.get("ip-prefix", "?")
        origin  = entry.get("state", {}).get("origin-protocol", "?")
        gw_list = []
        for nh in entry.get("next-hops", {}).get("next-hop", []):
            gw    = nh.get("state", {}).get("ip-address", "")
            iface = nh.get("interface-ref", {}).get("state", {}).get("interface", "")
            gw_list.append(gw or iface or "local")
        routes.append({"prefix": prefix, "protocol": origin,
                       "gateway": ", ".join(gw_list) or "direct"})
    return routes


def print_routes(routes):
    print(f"\n  {'Prefijo':<22} {'Protocolo':<16} Gateway")
    print(f"  {'-'*22} {'-'*16} {'-'*20}")
    for r in routes:
        print(f"  {r['prefix']:<22} {r['protocol']:<16} {r['gateway']}")


def main():
    parser = argparse.ArgumentParser(
        description="Consulta masiva RESTCONF de todos los routers del testbed")
    parser.add_argument("--query",    default="all",
                        choices=["interfaces", "routes", "all"],
                        help="Que consultar: interfaces | routes | all (default: all)")
    parser.add_argument("--port",     default=5900,   type=int,
                        help="Puerto RESTCONF (default: 5900)")
    parser.add_argument("--user",     default="admin")
    parser.add_argument("--password", default="admin", dest="password")
    parser.add_argument("--only-ip",  action="store_true",
                        help="(interfaces) mostrar solo interfaces con IP")
    parser.add_argument("--protocol", default="static",
                        choices=["static", "rib", "all"],
                        help="(routes) fuente de rutas: static | rib | all (default: static)")
    args = parser.parse_args()

    routers = get_router_ips()
    if not routers:
        print("[ERROR] No se encontraron routers. Comprueba que el testbed esta desplegado.")
        sys.exit(1)

    for name, ip in routers.items():
        print(f"\n{'#'*65}")
        print(f"#  Router: {name.upper()}  ({ip})")
        print(f"{'#'*65}")

        if args.query in ("interfaces", "all"):
            print("\n[Interfaces IP]")
            try:
                ifaces = query_interfaces(ip, args.port, args.user, args.password,
                                          only_ip=args.only_ip)
                print_interfaces(ifaces)
            except requests.exceptions.ConnectionError:
                print(f"  [ERROR] Sin conexion a {ip}:{args.port}")
            except requests.exceptions.HTTPError as e:
                print(f"  [ERROR] HTTP {e.response.status_code}")
            except Exception as e:
                print(f"  [ERROR] {e}")

        if args.query in ("routes", "all"):
            print("\n[Tabla de encaminamiento]")
            try:
                routes = []
                if args.protocol in ("static", "all"):
                    routes += query_static_routes(ip, args.port, args.user, args.password)
                if args.protocol in ("rib", "all"):
                    routes += query_rib(ip, args.port, args.user, args.password)
                print_routes(routes)
            except requests.exceptions.ConnectionError:
                print(f"  [ERROR] Sin conexion a {ip}:{args.port}")
            except requests.exceptions.HTTPError as e:
                print(f"  [ERROR] HTTP {e.response.status_code}")
            except Exception as e:
                print(f"  [ERROR] {e}")

    print(f"\n{'#'*65}\n")


if __name__ == "__main__":
    main()