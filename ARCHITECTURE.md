# Arquitectura de MEKA Filesystem

> Documento de referencia para comprender la organización interna de MEKA
> Filesystem y el patrón usado por los demás componentes de MEKA Workspace.

## 1. Objetivo del proyecto

MEKA Filesystem es una **biblioteca de operaciones sobre el sistema de
archivos** que puede exponerse mediante **distintos transportes** sin duplicar
la lógica del dominio.

El dominio (`workspace.core`) contiene toda la lógica de negocio. Los
transportes —HTTP/OAuth para clientes remotos y STDIO para clientes locales— son
solo adaptadores que convierten esa lógica en MCP. Cambiar de transporte, o
agregar uno nuevo, no debe tocar el dominio.

## 2. Arquitectura

```
workspace/
├── core/
│   ├── models.py
│   ├── errors.py
│   └── ops/
│
├── internal/
│   ├── config/
│   └── path/
│
└── servers/
    ├── _tools.py
    ├── filesystem_http.py
    ├── filesystem_stdio.py
    └── filesystem_server.py   (alias temporal)
```

### Responsabilidad de cada directorio

| Directorio | Responsabilidad |
| --- | --- |
| `core/` | **Dominio**: operaciones de filesystem, modelos y errores. Independiente de todo transporte. |
| `internal/` | **Infraestructura interna**: configuración de ejecución (`config`) y límite seguro de rutas (`path`). Soporta al dominio y a los transportes; no es API pública. |
| `servers/` | **Adaptadores de transporte**: definición compartida de herramientas y los puntos de entrada MCP. |

- `core/models.py` — modelos del dominio (`FileInfo`, `FileType`, `GrepMatch`…).
- `core/errors.py` — errores del dominio (`PathOutsideWorkspaceError`, etc.).
- `core/ops/` → operaciones puras que reciben `root: Path` + ruta relativa.
- `internal/config/config.py` → `WORKSPACE_ROOT` y configuración de autenticación.
- `internal/path/resolver.py` → evita escapes del workspace (rutas absolutas, `..`, symlinks).
- `servers/_tools.py` → registro único de las 26 herramientas MCP.
- `servers/filesystem_http.py` → transporte HTTP/OAuth.
- `servers/filesystem_stdio.py` → transporte STDIO local.
- `servers/filesystem_server.py` → alias temporal de compatibilidad (`filesystem_http`).

## 3. Dominio

`workspace.core` contiene toda la lógica de negocio. **No conoce**:

- HTTP
- STDIO
- OAuth / JWT
- FastMCP

Es una biblioteca reutilizable **desde cualquier transporte**. Cada operación
recibe el `root` autorizado y una ruta relativa, y es agnóstica al transporte
que la invoque. Toda operación que deba quedar disponible por MCP se expone
desde los adaptadores, nunca desde el core.

## 4. Adaptadores de transporte

| | `filesystem_http.py` | `filesystem_stdio.py` |
| --- | --- | --- |
| Tipo | MCP remoto | MCP local |
| Comunicación | HTTP (Uvicorn) | STDIO (`command` + `args`) |
| Autenticación | OAuth / OIDC, JWT, `api-key` | No (proceso local confiable) |
| Middleware HTTP | Sí | No |
| Clientes | ChatGPT y otros remotos (vía proxy) | Claude Desktop, VS Code, Cursor, Windsurf |

La única diferencia entre ambos es **el transporte y su autenticación**: el
conjunto de herramientas MCP expuestas es idéntico.

## 5. Registro de herramientas

`servers/_tools.py` es **la única ubicación** donde se registran las
herramientas MCP.

Todos los transportes usan la misma función:

```python
from workspace.servers._tools import register_tools

register_tools(mcp)                      # STDIO: sin scopes
register_tools(mcp, scope_guard=_scope)  # HTTP en modo oidc
```

Reglas:

- **Nunca** duplicar definiciones de herramientas.
- Un transporte nuevo debe reutilizar `register_tools()`, no copiarlas.
- `register_tools()` recibe un `scope_guard` opcional que el transporte HTTP
  en modo OIDC inyecta; el transporte STDIO no pasa ninguno.

## 6. Flujo de llamadas

```
        Cliente

 ChatGPT        Claude Desktop
   │                  │
 HTTP/OAuth        STDIO
   │                  │
 filesystem_http  filesystem_stdio
   │                       │
   └──────────┬────────────┘
              │
       register_tools()
              │
       workspace.core.ops
```

## 7. Principios de diseño

- **El dominio nunca depende del transporte.**
- Cada transporte implementa únicamente la **comunicación** y la
  **autenticación** necesarias.
- Las operaciones del dominio existen **una sola vez**.
- Agregar un nuevo transporte **nunca** requiere modificar `workspace.core`.

## 8. Patrón para futuros proyectos

Esta arquitectura es el **estándar** para todos los componentes de MEKA
Workspace. Cada componente seguirá el mismo patrón de *biblioteca de dominio +
adaptadores de transporte*:

- MEKA Filesystem
- MEKA SQLite
- MEKA Calendar
- MEKA CRM
- otros dominios futuros

```
<dominio>/            Biblioteca pura: lógica de negocio, sin transporte.
<dominio>/internal/   Infraestructura (config, seguridad).
<dominio>/servers/    Adaptadores (tools compartidos + http + stdio).
```