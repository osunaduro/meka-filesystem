# Implementación de transporte STDIO para MEKA Filesystem

## Objetivo

Agregar soporte para **MCP sobre STDIO** al proyecto **meka-filesystem**, manteniendo la arquitectura existente.

La implementación **no debe modificar ni romper** el servidor HTTP actual, ya que éste continúa siendo utilizado por ChatGPT y otros clientes remotos.

El objetivo es permitir que clientes como **Claude Desktop**, **VS Code**, **Cursor**, **Windsurf** u otros clientes compatibles con MCP puedan ejecutar el servidor localmente mediante:

* command
* args
* comunicación por STDIO

---

# Arquitectura actual

El proyecto ya posee una separación entre:

* Dominio (workspace/core)
* Configuración (workspace/internal)
* Transporte (workspace/servers)

La lógica del negocio **no debe duplicarse**.

Todas las operaciones existentes deben continuar viviendo en:

```
workspace/core/ops/
```

Por ejemplo:

* read
* write
* grep
* copy
* mkdir
* move
* stat
* walk
* etc.

Estas operaciones deben seguir siendo la única fuente de verdad.

---

# Objetivo de la implementación

Crear un nuevo servidor MCP para STDIO.

Ejemplo de estructura:

```
workspace/

    servers/

        filesystem_server.py      ← servidor HTTP existente

        filesystem_stdio.py       ← NUEVO
```

El nuevo servidor debe registrar exactamente las mismas herramientas MCP que el servidor HTTP.

No debe existir lógica duplicada.

---

# Requisitos

## NO modificar

No eliminar:

* filesystem_server.py

No modificar el funcionamiento del servidor HTTP.

Debe seguir funcionando exactamente igual.

---

## Crear un servidor STDIO

Crear un servidor independiente que:

* cree una instancia FastMCP

* registre todas las herramientas existentes

* ejecute el servidor utilizando STDIO

No debe incluir:

* Starlette
* Middleware HTTP
* Bearer Middleware
* JWT
* OAuth
* RemoteAuthProvider
* Rutas HTTP
* Uvicorn

Nada relacionado con transporte HTTP.

---

# Reutilización del dominio

Cada herramienta debe llamar exactamente a las funciones existentes.

Ejemplo conceptual:

```
@mcp.tool
def read_file(...):

    return read(...)
```

Nunca reimplementar:

* lectura
* escritura
* búsqueda
* copias

Toda esa lógica ya existe.

---

# Configuración

El servidor STDIO debe seguir utilizando:

```
workspace/internal/config
```

para obtener:

* WORKSPACE_ROOT

y cualquier otra configuración necesaria.

No deben existir dos mecanismos distintos para localizar el workspace.

---

# Organización

Si durante la implementación se detecta código repetido entre:

* filesystem_server.py
* filesystem_stdio.py

extraer únicamente el código compartido a funciones reutilizables.

No modificar la API pública.

---

# Resultado esperado

El proyecto deberá soportar dos transportes:

```
                 workspace.core

                       ▲

         ┌─────────────┴─────────────┐

         │                           │

filesystem_server.py        filesystem_stdio.py

         │                           │

      HTTP/OAuth                  STDIO

         │                           │

      ChatGPT                 Claude Desktop
                              Cursor
                              VSCode
                              Windsurf
```

El dominio debe ser completamente independiente del transporte.

---

# Compatibilidad

El servidor STDIO debe poder registrarse en Claude Desktop mediante:

```
~/.config/Claude/claude_desktop_config.json
```

utilizando un bloque similar a:

```json
{
  "mcpServers": {
    "meka-filesystem": {
      "command": "python3",
      "args": [
        "/ruta/al/proyecto/workspace/servers/filesystem_stdio.py"
      ]
    }
  }
}
```

No asumir rutas absolutas.

---

# Criterios de aceptación

La implementación será correcta si:

* El servidor HTTP continúa funcionando sin cambios.
* El servidor STDIO inicia correctamente desde línea de comandos.
* Claude Desktop detecta el servidor como un MCP local.
* Todas las herramientas actualmente disponibles vía HTTP están disponibles también por STDIO.
* No existe duplicación significativa de lógica de negocio.
* La arquitectura mantiene una clara separación entre **dominio** y **transporte**.

La prioridad es preservar la arquitectura existente y agregar un nuevo adaptador de transporte, no rediseñar el proyecto.



## Reorganización de los puntos de entrada

Actualmente el proyecto posee un único punto de entrada:

```text
workspace/servers/filesystem_server.py
```

Como el proyecto pasará a soportar **dos transportes distintos**, este archivo deja de representar correctamente su responsabilidad.

Se deberá reorganizar de la siguiente manera:

```text
workspace/
└── servers/
    ├── filesystem_http.py      ← reemplaza a filesystem_server.py
    ├── filesystem_stdio.py     ← nuevo punto de entrada para clientes locales
    └── __init__.py
```

### Requisitos

* Renombrar `filesystem_server.py` a `filesystem_http.py`.
* Crear `filesystem_stdio.py`.
* Actualizar todas las referencias internas que importen `filesystem_server`.
* No modificar la API pública del dominio (`workspace.core`).
* Ambos puntos de entrada deberán exponer exactamente el mismo conjunto de herramientas MCP.
* La única diferencia entre ambos deberá ser el transporte (HTTP/OAuth vs. STDIO).

El objetivo es que el proyecto identifique claramente cada adaptador de transporte y facilite la incorporación de nuevos transportes en el futuro.

