# Analysis and Evaluation of REST-Based Protocols for Programmable Network Management in Virtualized Environments

## Descripción
Trabajo de Fin de Grado centrado en el análisis y evaluación del protocolo 
RESTCONF como mecanismo de gestión programable de redes en entornos 
virtualizados. El proyecto valida el uso de RESTCONF tanto para monitorización 
como para configuración de dispositivos de red (Cisco IOS-XE y Arista cEOS), 
desplegados mediante testbeds containerizados con Containerlab.

## Estructura del repositorio
- `escenario1/` — Validación básica de operaciones RESTCONF (GET, PUT, POST, 
  PATCH, DELETE, HEAD) sobre la interfaz Ethernet1 de un router Arista cEOS.
- `escenario2/` — Aprovisionamiento completo de direccionamiento IP y rutas 
  estáticas mediante RESTCONF sobre una topología de tres routers Arista cEOS.
- `escenario3/` — Automatización RESTCONF en un entorno multi-vendor 
  (Cisco IOS-XE + Arista cEOS), adaptando payloads y modelos YANG según el fabricante.

Cada carpeta contiene su propio README con la explicación detallada del 
escenario, la topología usada y los comandos necesarios para desplegarlo, 
ejecutarlo y validarlo.

## Tecnologías utilizadas
- Containerlab (Cisco IOS-XE CSR1000v, Arista cEOS)
- RESTCONF / NETCONF
- Modelos YANG: OpenConfig (openconfig-interfaces, openconfig-network-instance) 
  e IETF/Cisco nativo (ietf-interfaces, ietf-ip, Cisco-IOS-XE-native)
- Python (requests) para automatización
- curl / jq para pruebas manuales
- Open vSwitch (OVS) para conectividad de capa 2

## Autora
Inés Valdivielso Nogales — Ingeniería de Telecomunicación, UPM (ETSIT)