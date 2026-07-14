# Escenario 1: Validación básica de RESTCONF sobre Ethernet1 (Arista cEOS)

## Descripción
Este escenario valida el comportamiento básico de RESTCONF sobre un único 
router Arista cEOS, ejercitando los métodos HTTP GET, HEAD, PUT, POST, PATCH 
y DELETE contra la interfaz Ethernet1. El objetivo es confirmar que el 
dispositivo acepta correctamente operaciones de lectura y escritura, y validar 
el ciclo de vida completo de un recurso (creación, lectura, borrado) usando 
una interfaz Loopback100 temporal.

## Requisitos previos
- Containerlab instalado
- Docker en ejecución
- Python 3.x con la librería `requests`
- RESTCONF habilitado en el router (vía configuración de arranque)

## Estructura de archivos
- `get_eth1_status.py` — GET: obtiene el estado operacional y contadores de Ethernet1
- `get_system_info.py` — GET: obtiene hostname e información del sistema
- `head.py` — HEAD: comprueba si el recurso existe sin devolver cuerpo
- `put_eth1_description.py` — PUT: reemplaza la configuración completa de Ethernet1
- `post_eth1_description.py` — POST: actualiza parcialmente la descripción de Ethernet1
- `patch_eth1_description.py` — PATCH: modifica un solo campo de la configuración
- `delete_lo100.py` — DELETE: crea, verifica y elimina una interfaz Loopback100

## Cómo ejecutarlo

### 1. Comprobar el estado inicial de la interfaz
```bash
python3 get_system_info.py
python3 get_eth1_status.py
python3 head.py
```

### 2. Probar las operaciones de escritura
```bash
python3 put_eth1_description.py
python3 post_eth1_description.py
python3 patch_eth1_description.py
```

### 3. Validar el ciclo de vida completo de un recurso
```bash
python3 delete_lo100.py
```
Este script crea Loopback100, la lee, la elimina y confirma con un GET final 
que devuelve HTTP 404 (recurso ya no existe).

## Notas
- Todas las peticiones usan autenticación básica (usuario/contraseña admin) 
  y HTTPS con verificación de certificado desactivada (`--insecure` / `verify=False`).
- El modelo YANG utilizado es OpenConfig (`openconfig-interfaces`), que separa 
  los datos en subárboles `config` (lectura-escritura) y `state` (solo lectura).