# Documentación del proyecto

MEKA Filesystem MCP es un servidor MCP autenticado para administrar un único
workspace de archivos. Esta carpeta reúne la documentación de arquitectura,
despliegue y evolución del proyecto.

## Estado actual

El servidor expone herramientas MCP para explorar, leer, escribir, buscar y
administrar archivos dentro de un directorio aislado. Se ejecuta con FastMCP y
Uvicorn en Docker, detrás de un proxy HTTPS.

La autenticación es configurable mediante `MEKA_AUTH_MODE`:

- `api-key` (por defecto): exige un token Bearer estático `MEKA_API_KEY`.
- `oidc`: actúa como *Resource Server* OAuth/OIDC frente a cualquier proveedor
  estándar (Authentik, Keycloak, Auth0, Okta, Azure Entra ID…) y valida los
  scopes `filesystem:read`, `filesystem:write` y `filesystem:delete`.
- `none`: sin autenticación, exclusivo para desarrollo.

Las rutas de los clientes siempre son relativas al workspace configurado. El
resolvedor central rechaza rutas absolutas, escapes con `..` y enlaces
simbólicos que lleven fuera del directorio autorizado.

## Arquitectura

```text
Cliente MCP (remoto)
  → Proxy inverso HTTPS
    → FastMCP / Uvicorn
      → workspace.servers.filesystem_http
        → workspace.servers._tools
          → workspace.core.ops
            → workspace.internal.path.resolve
              → workspace montado en el host

Cliente MCP (local, p. ej. Claude Desktop)
  → STDIO (command + args)
    → workspace.servers.filesystem_stdio
      → workspace.servers._tools
        → workspace.core.ops
          → workspace.internal.path.resolve
            → workspace montado en el host
```

El servidor es un adaptador de red: define herramientas, autenticación y
serialización de respuestas. Las operaciones de archivos viven en el núcleo
reutilizable y no dependen de Docker ni de MCP.

## Estructura del repositorio

| Directorio | Responsabilidad |
| --- | --- |
| `workspace/` | Código Python del servidor, operaciones de filesystem y componentes internos. |
| `workspace/servers/` | Adaptadores de transporte (`filesystem_http`, `filesystem_stdio`) y definición compartida de herramientas (`_tools`). |
| `workspace/core/` | Operaciones reutilizables, modelos y errores del dominio. |
| `workspace/internal/` | Configuración de ejecución y límite seguro de resolución de rutas. |
| `infrastructure/` | Dockerfile, Docker Compose, volumen, usuario del contenedor y red. |
| `home/` | Reserva para persistencia propia futura; hoy no la usa el servicio. |
| `docs/` | Documentación de producto, despliegue y decisiones de arquitectura. |

## Documentos disponibles

- [Implementación MCP](<Implementacion MCP Filesystem.md>): arquitectura del
  servidor, herramientas disponibles y límite de seguridad.
- [Despliegue MCP](<Despliegue MCP Filesystem.md>): requisitos, Docker,
  Nginx, configuración y diagnóstico.
- [Autenticación](autenticacion.md): especificación de los modos `api-key` y
  `oidc`, scopes y rol de Resource Server.
- [Transporte STDIO](<Implementación de transporte STDIO para MEKA Filesystem.md>):
  punto de entrada local para clientes como Claude Desktop, VS Code, Cursor y
  Windsurf.
- [Especificación histórica del dominio](<Filesystem Dominian Specification.md>):
  documento inicial de diseño. Puede describir capacidades que todavía no se
  implementaron y debe leerse como referencia histórica, no como contrato
  operativo actual.

La documentación específica de cada capa está junto al código: consulte los
README de `workspace/`, `workspace/core/`, `workspace/internal/` e
`infrastructure/`.

## Hoja de ruta

Las siguientes iniciativas están planificadas, pero no forman parte de la
versión actual ni deben asumirse como disponibles por los clientes.

### Autenticación OAuth

Implementada como el modo `oidc` de `MEKA_AUTH_MODE`. MEKA Filesystem actúa
como *Resource Server*: valida el JWT (firma via JWKS, `issuer`, `audience`,
expiración) contra un proveedor OIDC externo y autoriza por scopes
`filesystem:read`, `filesystem:write` y `filesystem:delete`. Publica
`/.well-known/oauth-protected-resource/mcp` para el descubrimiento MCP. No
emite tokens ni administra usuarios. Ver [autenticacion.md](autenticacion.md).

Los modos `api-key` (por defecto) y `none` continúan disponibles para
instalaciones simples y desarrollo respectivamente.

### Mejoras futuras del modo OIDC

Quedan como evolución opcional: verificación de scopes más finos por
herramienta, rotación de credenciales y políticas por identidad. Ninguna de
ellas forma parte de la versión actual.

### Sección de documentos con Apache Tika

Se planea incorporar una sección dedicada a documentos basada en Apache Tika.
Su finalidad será extraer texto y metadatos de formatos como PDF, documentos
de oficina y otros archivos compatibles, para ofrecer capacidades de consulta
documental por encima de las operaciones de filesystem.

Esta integración deberá permanecer separada del núcleo de archivos: recibirá
solo rutas ya validadas dentro del workspace, aplicará límites de tamaño y de
tiempo de procesamiento, y expondrá herramientas MCP específicas para
extracción o consulta. Apache Tika no está instalado ni integrado actualmente.
