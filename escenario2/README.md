# Escenario 2: Direccionamiento IP y rutas estáticas vía RESTCONF (Arista cEOS)

## Descripción
Este escenario despliega una topología de tres routers Arista cEOS (r1, r2, r3) 
conectados en forma de triángulo, con tres LANs locales y tres switches OVS. 
Todo el direccionamiento IP y las rutas estáticas se configuran desde cero 
mediante RESTCONF, usando los modelos OpenConfig `openconfig-interfaces` y 
`openconfig-network-instance`. Se valida la configuración con lectura de 
interfaces, tablas de rutas y pruebas de conectividad extremo a extremo.

## Plan de direccionamiento
| Router | Interfaz | Dirección |
|---|---|---|
| r1 | Ethernet1 | 192.168.1.1/24 |
| r1 | Ethernet2 | 10.10.10.1/30 |
| r1 | Ethernet3 | 10.10.11.1/30 |
| r2 | Ethernet1 | 192.168.2.1/24 |
| r2 | Ethernet2 | 10.10.10.2/30 |
| r2 | Ethernet3 | 10.10.12.1/30 |
| r3 | Ethernet1 | 192.168.3.1/24 |
| r3 | Ethernet2 | 10.10.11.2/30 |
| r3 | Ethernet3 | 10.10.12.2/30 |

## Requisitos previos
- Containerlab instalado
- Docker en ejecución
- Python 3.x con la librería `requests`

## Estructura de archivos
- `routing-testbed.yaml` — Definición de la topología en Containerlab
- `deploy-routing-testbed.sh` — Despliega el testbed
- `destroy-routing-testbed.sh` — Elimina el testbed
- `configure_routing.py` — Configura IPs de interfaz y rutas estáticas en los 3 routers vía RESTCONF
- `get_interfaces.py` — Consulta estado administrativo/operacional e IPs de las interfaces
- `get_routing_table.py` — Consulta la tabla de rutas (RIB) del VRF por defecto
- `get_all_routers.py` — Descubre las IPs de gestión y consulta los tres routers en una sola ejecución
- `r1.txt`, `r2.txt`, `r3.txt` — Configuración de arranque de cada router para habilitar RESTCONF

## Cómo ejecutarlo

### 1. Desplegar el testbed
```bash
sudo ./deploy-routing-testbed.sh
```

### 2. Configurar direccionamiento IP y rutas estáticas
```bash
python3 configure_routing.py
```

### 3. Verificar la configuración aplicada
```bash
python3 get_interfaces.py
python3 get_routing_table.py
python3 get_all_routers.py
```

### 4. Probar conectividad extremo a extremo
Desde un host de una LAN, hacer ping a un host de otra LAN para confirmar 
el enrutamiento a través de los routers intermedios (2 saltos).

### 5. Eliminar el testbed
```bash
sudo ./destroy-routing-testbed.sh
```

## Notas
- El nombre del protocolo estático debe escribirse en mayúsculas (`STATIC`) 
  y el índice del next-hop debe empezar en 1 (no en 0), según lo requiere 
  el modelo OpenConfig implementado por Arista cEOS.