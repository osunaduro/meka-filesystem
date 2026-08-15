# Implementación MCP Filesystem

## Propósito

Este repositorio es una biblioteca reutilizable de manejo de archivos,
expuesta remotamente mediante MCP. No contiene el concepto de proyecto: las
carpetas son sólo carpetas y el cliente decide su propia organización.

El servidor opera dentro de un único workspace montado desde el host. Una
ruta puede representar una carpeta de documentos, balances, canciones, un
repositorio de código o cualquier otro recurso.

## Arquitectura

```text
Cliente MCP
  → HTTPS / Nginx
    → red Docker meka-network
      → FastMCP / Uvicorn (filesystem-mcp:8000/mcp/)
        → /data/workspace (volumen del host)
          ├── canciones/
          ├── documentos/
          ├── balances/
          └── mi-aplicacion-python/
```

Nginx termina TLS y reenvía `Authorization`. El contenedor MCP no publica
puertos al host.

## Límite de seguridad

`MEKA_WORKSPACE_ROOT` define el único directorio que el servidor puede
administrar. En Docker es `/data/workspace`.

Todas las herramientas reciben rutas relativas a ese root:

```text
create_directory(path="balances/2026")
write_file(path="balances/2026/julio.txt", content="...")
read_file(path="mi-aplicacion-python/README.md")
list_directory(path=".")
```

El resolvedor en `workspace.internal.path` canonicaliza cada ruta y rechaza
paths absolutos que estén fuera del root, `..` y escapes por symlinks. Ninguna
herramienta recibe un root arbitrario desde el cliente.

## Estructura

```text
workspace/
├── core/
│   ├── models.py                 # FileInfo, FileType y GrepMatch
│   ├── errors.py                 # Errores del dominio
│   └── ops/                      # Funciones reutilizables: root + path
├── internal/
│   ├── config/config.py          # MEKA_WORKSPACE_ROOT y UID/GID
│   └── path/resolver.py          # Boundary de seguridad de rutas
└── servers/
    ├── _tools.py                # Definición compartida de las 20 herramientas
    ├── filesystem_http.py       # Adaptador HTTP/OAuth (FastMCP + Uvicorn)
    ├── filesystem_stdio.py      # Adaptador STDIO (clientes locales)
    └── filesystem_server.py     # Alias de compatibilidad temporal

infrastructure/
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── generate-api-key.sh
```

## Biblioteca core

Las operaciones de `workspace.core.ops` no dependen de MCP ni de Docker.
Reciben `root: pathlib.Path` y rutas relativas, por ejemplo:

```python
from pathlib import Path
from workspace.core.ops import read, write

root = Path("/srv/meka/workspace")
write(root, "documentos/nota.txt", "Hola")
content = read(root, "documentos/nota.txt")
```

Esto permite reutilizar el dominio desde otra aplicación Python sin exponerlo
por red. El servidor MCP es sólo un adaptador que obtiene el root desde
configuración y transforma resultados a JSON.

## Herramientas MCP

- Información y exploración: `path_exists`, `stat_path`, `list_directory`,
  `walk_paths`, `glob_paths`, `grep_text`.
- Lectura: `read_file`, `read_file_range`, `read_file_head`, `read_file_tail`.
- Escritura: `write_file`, `append_file`, `replace_file_lines`,
  `truncate_file`.
- Administración: `create_directory`, `remove_directory`,
  `delete_file_path`, `copy_path`, `copy_directory_tree`, `move_path`.

`walk_paths`, `glob_paths` y `grep_text` reciben un límite de resultados;
el máximo permitido es 1000.

## Autenticación

La autenticación es configurable mediante `MEKA_AUTH_MODE` con tres modos
excluyentes: `api-key` (por defecto), `oidc` y `none`. En modo `api-key`, todas
las solicitudes HTTP requieren:

```text
Authorization: Bearer <MEKA_API_KEY>
```

`MEKA_API_KEY` existe sólo en el entorno de ejecución. `.dockerignore` evita
que `infrastructure/.env` entre al contexto de construcción de Docker.

En modo `oidc` el servidor actúa como *Resource Server*: valida el JWT del
cliente (firma JWKS, `issuer`, `audience`, expiración) contra un proveedor
OIDC externo y exige los scopes `filesystem:read`, `filesystem:write` y
`filesystem:delete` por herramienta. Publica
`/.well-known/oauth-protected-resource/mcp` para el descubrimiento MCP. Ver
[autenticacion.md](autenticacion.md).

En modo `none` no se exige autenticación; está pensado solo para desarrollo.

## Capacidades pendientes

No se implementaron todavía `stream`, `write_range` ni `watch`; por lo tanto
no existen como herramientas MCP.
