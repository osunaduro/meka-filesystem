# Servidores MCP

Este paquete contiene los adaptadores de transporte para el dominio filesystem.
Cada adaptador crea una aplicación FastMCP que expone las mismas 35 herramientas,
definidas una sola vez en `_tools.py`.

## Contenido

| Archivo | Transporte | Uso |
| --- | --- | --- |
| `_tools.py` | — | Definición compartida de las 35 herramientas y helpers de serialización. |
| `filesystem_http.py` | HTTP / OAuth | Servidor remoto ejecutado con Uvicorn (ChatGPT y otros clientes remotos). |
| `filesystem_stdio.py` | STDIO | Punto de entrada local para Claude Desktop, VS Code, Cursor, Windsurf. |
| `filesystem_server.py` | HTTP | Alias temporal de compatibilidad que re-exporta `filesystem_http`. |

## Responsabilidades

- Exponen las mismas 35 herramientas MCP en ambos transportes.
- Obtienen el root autorizado desde `MEKA_WORKSPACE_ROOT`.
- Convierten modelos internos a respuestas serializables.
- Limitan resultados de búsquedas y recorridos a un máximo de 1000 elementos.
- El adaptador HTTP autentica cada solicitud según `MEKA_AUTH_MODE`:
  - `api-key`: exige `Authorization: Bearer <MEKA_API_KEY>` mediante `BearerTokenMiddleware`.
  - `oidc`: actúa como *Resource Server* OAuth, valida el JWT con el proveedor y exige los scopes `filesystem:read`, `filesystem:write` y `filesystem:delete` por herramienta.
  - `none`: no exige autenticación (solo desarrollo).
- El adaptador STDIO no autentica: el proceso local es el cliente autorizado.

Los servidores no implementan por su cuenta las operaciones de archivos ni la
validación de rutas: delegan en `workspace.core.ops` e `workspace.internal.path`.
Esto mantiene la política de seguridad centralizada y permite reutilizar el
núcleo sin exponer una red.

En modo `oidc` el adaptador HTTP publica
`/.well-known/oauth-protected-resource/mcp` para el descubrimiento MCP. La
especificación está en [docs/autenticacion.md](../../docs/autenticacion.md).

La ejecución de producción del transporte HTTP está definida en
[infrastructure/docker-compose.yml](../../infrastructure/docker-compose.yml).
