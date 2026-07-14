# Escenario 3: Automatización RESTCONF multi-vendor (Cisco IOS-XE + Arista cEOS)

## Descripción
Este escenario extiende el Escenario 2 a un entorno heterogéneo con un router 
Cisco IOS-XE (CSR1000v) como r1, y dos routers Arista cEOS (r2, r3). El 
objetivo es demostrar cómo adaptar la automatización RESTCONF cuando cada 
fabricante usa modelos YANG y formatos de payload distintos: Cisco usa 
`ietf-interfaces`/`ietf-ip` y el modelo nativo `Cisco-IOS-XE-native` (XML), 
mientras que Arista usa OpenConfig (`openconfig-interfaces`, 
`openconfig-network-instance`) en JSON.

## Plan de direccionamiento
| Router | Interfaz | Dirección |
|---|---|---|
| r1 (Cisco) | GigabitEthernet2 | 192.168.1.1/24 |
| r1 (Cisco) | GigabitEthernet3 | 10.10.10.1/30 |
| r1 (Cisco) | GigabitEthernet4 | 10.10.11.1/30 |
| r2 (Arista) | Ethernet1 | 192.168.2.1/24 |
| r2 (Arista) | Ethernet2 | 10.10.10.2/30 |
| r2 (Arista) | Ethernet3 | 10.10.12.1/30 |
| r3 (Arista) | Ethernet1 | 192.168.3.1/24 |
| r3 (Arista) | Ethernet2 | 10.10.11.2/30 |
| r3 (Arista) | Ethernet3 | 10.10.12.2/30 |

## Requisitos previos
- Containerlab instalado
- Docker en ejecución
- Python 3.x con la librería `requests`
- Imagen de Cisco CSR1000v disponible localmente para Containerlab

## Estructura de archivos
- `configure-routing-restconf.py` — Script final que configura IPs y rutas 
  estáticas en los tres routers, aplicando lógica específica según el vendor 
  (XML/nativo para Cisco, JSON/OpenConfig para Arista)
- Ficheros intermedios de prueba (payloads JSON/XML usados para depurar el 
  formato exacto requerido por cada plataforma antes de consolidar el script final)

## Cómo ejecutarlo

### 1. Desplegar el testbed
Desplegar la topología mixta con Containerlab (ver fichero YAML de topología).

### 2. Configurar direccionamiento IP y rutas estáticas
```bash
python3 configure-routing-restconf.py
```
El script detecta internamente si el router es Cisco IOS-XE o Arista cEOS y 
genera el payload correspondiente (XML + Cisco-IOS-XE-native para r1, JSON + 
OpenConfig para r2 y r3).

### 3. Verificar la configuración
Reutilizar los scripts de verificación del Escenario 2 (`get_interfaces.py`, 
`get_routing_table.py`) adaptados a las interfaces GigabitEthernet de Cisco.

## Notas
- Las rutas estáticas en Cisco IOS-XE requieren prefijo, máscara y next-hop 
  bajo el modelo nativo `Cisco-IOS-XE-native`, en formato XML.
- Las rutas estáticas en Arista cEOS requieren prefijo y next-hop bajo 
  `openconfig-network-instance`, en formato JSON.
- Aunque el objetivo funcional es idéntico en ambos fabricantes, el payload 
  RESTCONF difiere completamente según el modelo YANG del vendor.