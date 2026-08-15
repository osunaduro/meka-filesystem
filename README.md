# MEKA Filesystem MCP

Servidor MCP autenticado y biblioteca Python para administrar archivos dentro de un único workspace aislado. Permite leer, escribir, buscar, explorar y organizar archivos sin exponer el resto del filesystem del host.

El núcleo (`workspace.core`) es una **biblioteca Python pura**, sin ninguna dependencia de MCP, HTTP o Docker. Sobre ella se construyeron adaptadores que la exponen de varias formas, según lo que necesites:

- **STDIO local**, sin autenticación (el proceso confía en quien lo lanza) — para Claude Desktop, Claude Code, VS Code, Cursor, Windsurf.
- **HTTP remoto**, con autenticación por `api-key` (un token fijo que vos generás) u **OIDC** como *Resource Server* real (validando JWT contra un proveedor externo: Authentik, Keycloak, Auth0, Okta, Azure Entra ID…) — para exponerlo desde donde quieras, con tu propio proxy o túnel.
- **Docker**, en dos modos: uno pensado para exponerlo a internet detrás de tu infraestructura, y otro para aislar una carpeta local como "jaula" de trabajo, sin tocar el resto del sistema.
- **Extensión de Claude Desktop (.mcpb)**, instalable con un clic.

## Características

- 26 herramientas MCP para lectura, escritura, exploración y administración de archivos, incluyendo binarios (imágenes, audio) y edición por contenido con diff y modo dry-run.
- Rutas limitadas a un workspace configurado; protección frente a rutas absolutas, `..` y escapes mediante symlinks.
- Autenticación configurable en tres modos: `none`, `api-key` y `oidc`.
- Scopes `filesystem:read`, `filesystem:write` y `filesystem:delete` que controlan las herramientas en modo OIDC.
- UID/GID configurables en Docker para conservar la propiedad correcta en el host.

## Herramientas MCP

| Área | Herramientas |
| --- | --- |
| Información | `path_exists`, `stat_path`, `list_directory`, `list_allowed_directories`, `walk_paths`, `glob_paths`, `grep_text` |
| Lectura | `read_file`, `read_files`, `read_file_range`, `read_file_head`, `read_file_tail`, `read_media_file` |
| Escritura | `write_file`, `write_media_file`, `append_file`, `replace_file_lines`, `edit_file_text`, `edit_file_text_many`, `truncate_file` |
| Administración | `create_directory`, `remove_directory`, `delete_file_path`, `copy_path`, `copy_directory_tree`, `move_path` |

Notas sobre algunas herramientas menos obvias:

- `edit_file_text` reemplaza texto localizándolo por contenido exacto (no por número de línea), con `dry_run` para previsualizar el diff sin escribir, y `expected_occurrences` para evitar reemplazos ambiguos.
- `edit_file_text_many` aplica varias ediciones de ese tipo sobre el mismo archivo de forma atómica: si alguna falla, no se escribe nada.
- `read_files` lee varios archivos en una sola llamada; un fallo en uno no aborta el resto.
- `read_media_file` / `write_media_file` son la vía para binarios (imágenes, audio, PDFs, lo que sea): base64 + MIME type adivinado por extensión.
- `walk_paths`, `glob_paths` y `grep_text` devuelven como máximo 1000 resultados. Para búsquedas recursivas con `glob_paths`, use patrones como `**/*.py`.

## Inicio rápido con Docker

Dos modos, misma imagen, distinta forma de correrla — ver [infrastructure/README.md](infrastructure/README.md) para el detalle completo:

- **[`infrastructure/remote/`](infrastructure/remote/)** — el servidor queda accesible desde fuera de esta máquina, detrás de tu propio proxy inverso o túnel (Nginx, Caddy, Cloudflare Tunnel, Tailscale…). Requiere una red Docker externa (`meka-network`) y `MEKA_AUTH_MODE=api-key` u `oidc`.
- **[`infrastructure/sandbox/`](infrastructure/sandbox/)** — aísla una carpeta local para que un agente trabaje ahí sin poder tocar el resto del disco. Standalone, sin red externa ni proxy: el puerto queda atado a `127.0.0.1`, nunca alcanzable desde afuera.

```bash
# Modo remoto
cd infrastructure/remote
cp .env.example .env && docker network create meka-network && ../generate-api-key.sh
# editar .env, luego:
docker compose up -d --build

# Modo sandbox ("jaula")
cd infrastructure/sandbox
cp .env.example .env && ../generate-api-key.sh
# editar .env con la carpeta a aislar, luego:
docker compose up -d --build
```

## Autenticación

`MEKA_AUTH_MODE` selecciona el mecanismo de autenticación del servidor. Los tres modos son excluyentes.

| Modo | Uso | Configuración |
| --- | --- | --- |
| `api-key` | Por defecto. Instalaciones personales, domésticas o de prueba. | `MEKA_API_KEY` |
| `oidc` | Empresarial o multiusuario, con un proveedor OAuth/OIDC externo. | `MEKA_OIDC_ISSUER`, `MEKA_OIDC_AUDIENCE`, `MEKA_OIDC_JWKS_URL`, `MEKA_OIDC_RESOURCE_URL` |
| `none` | Solo desarrollo, o modo sandbox estrictamente local (127.0.0.1). | — |

### Modo api-key (por defecto)

```dotenv
MEKA_AUTH_MODE=api-key
MEKA_API_KEY=un-token-largo-y-secreto
```

Cada solicitud HTTP debe enviar:

```text
Authorization: Bearer <MEKA_API_KEY>
```

El servidor responde `401` si falta el token, no usa el esquema `Bearer` o no coincide.

### Modo oidc

MEKA Filesystem actúa únicamente como *Resource Server*; la autenticación es responsabilidad del proveedor OIDC. No emite tokens ni gestiona usuarios.

```dotenv
MEKA_AUTH_MODE=oidc
MEKA_OIDC_ISSUER=https://id.example.com/realms/meka
MEKA_OIDC_AUDIENCE=https://archivo.example.com/mcp
MEKA_OIDC_JWKS_URL=https://id.example.com/realms/meka/protocol/openid-connect/certs
MEKA_OIDC_RESOURCE_URL=https://archivo.example.com/mcp
```

El servidor valida la firma del JWT contra el JWKS, `issuer`, `audience` y expiración. Define tres scopes que controlan las herramientas:

| Scope | Herramientas |
| --- | --- |
| `filesystem:read` | Existencia, metadata, listado, recorridos, búsqueda y lectura (texto y binaria). |
| `filesystem:write` | Escritura, append, edición por contenido o línea, truncate, creación, copia y movimiento. |
| `filesystem:delete` | Eliminación de archivos y directorios. |

Publique además `/.well-known/oauth-protected-resource/mcp` para el descubrimiento MCP (utilizable por clientes como ChatGPT).

La especificación completa está en [docs/autenticacion.md](docs/autenticacion.md).

### Modo none

```dotenv
MEKA_AUTH_MODE=none
```

Desactiva toda autenticación. Solo para desarrollo, o para el modo sandbox de Docker cuando el puerto está atado a `127.0.0.1` y confiás en todo lo que corre en esa máquina. Nunca en modo remoto.

## Seguridad y alcance

`MEKA_WORKSPACE_ROOT` define el único árbol de archivos que puede administrar el servicio. El cliente no puede indicar otro root: todas las rutas se resuelven y validan dentro de ese directorio, rechazando rutas absolutas, `..` y symlinks que escapen del root.

El token protege el endpoint, pero no reemplaza los permisos del filesystem. El directorio montado debe permitir lectura y escritura al UID/GID configurado para el contenedor.

## Uso local con STDIO

El proyecto soporta dos transportes MCP que comparten las mismas herramientas:

- **HTTP/OAuth** (`workspace.servers.filesystem_http`): servidor remoto, para ChatGPT y clientes remotos.
- **STDIO** (`workspace.servers.filesystem_stdio`): ejecución local por `command` + `args`, para Claude Desktop, Claude Code, VS Code, Cursor y Windsurf.

Para ejecutar el adaptador local directamente:

```bash
python3 workspace/servers/filesystem_stdio.py
```

O, si tiene instalado el paquete:

```bash
meka-filesystem-stdio
```

Registro en Claude Desktop (`~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "meka-filesystem": {
      "command": "python3",
      "args": ["/ruta/al/proyecto/workspace/servers/filesystem_stdio.py"]
    }
  }
}
```

El proceso local opera sobre `MEKA_WORKSPACE_ROOT` (o `/data/workspace` por
defecto). Como el transporte local es confiable, no exige autenticación HTTP.

### Como extensión de Claude Desktop (.mcpb)

También puede instalarse con un clic empaquetado como extensión `.mcpb`. Ver [`build_mcpb.sh`](build_mcpb.sh) — la documentación completa del empaquetado (manifest, publicación en el directorio de Anthropic) queda pendiente.

## Uso como biblioteca Python

```python
from pathlib import Path

from workspace.core.ops import read, write

root = Path("/srv/meka/workspace")
write(root, "notas/hola.txt", "Hola\n")
print(read(root, "notas/hola.txt"))
```

Consulte [workspace/core/README.md](workspace/core/README.md) para el núcleo y sus operaciones. Al usar la biblioteca directamente, el llamador debe proporcionar un root existente y autorizado.

## Estructura

```text
workspace/           Código Python: adaptadores de servidor, núcleo y componentes internos
  core/               Biblioteca pura: operaciones de filesystem, modelos, errores — sin transporte
  servers/            filesystem_http.py (HTTP/OAuth), filesystem_stdio.py (STDIO), _tools.py
infrastructure/
  remote/             Docker Compose para exponer el servidor a internet (detrás de tu propio proxy/túnel)
  sandbox/            Docker Compose standalone para aislar una carpeta local, sin red externa
docs/                 Especificación, implementación y despliegue ampliados
```

## Documentación

- [Arquitectura](ARCHITECTURE.md): organización interna, dominio y adaptadores de transporte; patrón para los proyectos de MEKA Workspace.
- [Índice de documentación y hoja de ruta](docs/README.md)
- [Despliegue e integración con proxy inverso](<docs/Despliegue MCP Filesystem.md>)
- [Arquitectura e implementación](<docs/Implementacion MCP Filesystem.md>)
- [Transporte STDIO](<docs/Implementación de transporte STDIO para MEKA Filesystem.md>)
- [Autenticación](docs/autenticacion.md)
- [Infraestructura (modo remoto y sandbox)](infrastructure/README.md)
- [Límite de seguridad de rutas](workspace/internal/path/README.md)

## Desarrollo

El proyecto requiere Python 3.11 o superior. Sus dependencias de ejecución están definidas en `pyproject.toml`; `grep_text` requiere además el binario `rg` (ripgrep), incluido en la imagen Docker.

Instale las dependencias de test y ejecute la suite:

```bash
python3 -m pip install -e '.[test]'
python3 -m pytest -q
```

Los tests cubren la configuración de los tres modos de autenticación, el middleware `api-key` (401 / pase de acceso), el comportamiento del Resource Server OIDC (scopes y ruta de descubrimiento), y las operaciones del núcleo (`core/ops`): edición por contenido, edición atómica en lote, lectura en lote y lectura/escritura binaria.

## Contacto

¿Dudas, bugs o sugerencias? Abrí un Issue en este repositorio.

## Licencia

MIT © 2026 MEKAweb (Martín Osuna). Ver [LICENSE](LICENSE).
