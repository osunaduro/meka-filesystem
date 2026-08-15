# Resolución segura de rutas

`workspace.internal.path` implementa el límite de seguridad entre las rutas
que recibe una operación y el filesystem del host. Su única API es
`resolve(root, path)`.

No forma parte de la API pública de la biblioteca. Todas las operaciones de
`workspace.core.ops` deben usarla antes de leer, crear, modificar, copiar o
eliminar una ruta.

## Contrato

```python
from pathlib import Path

from workspace.internal.path import resolve

target = resolve(Path("/data/workspace"), "documentos/nota.txt")
# /data/workspace/documentos/nota.txt
```

- `root` es el directorio raíz autorizado.
- `path` debe ser una ruta relativa a `root`.
- El resultado es un `pathlib.Path` absoluto y normalizado.

El servidor MCP obtiene `root` de `MEKA_WORKSPACE_ROOT`; el cliente nunca
puede elegirlo. Las herramientas MCP solo entregan la ruta relativa a sus
operaciones core.

## Validaciones

El resolvedor aplica estas comprobaciones en este orden:

1. Rechaza las rutas absolutas, como `/etc/passwd`.
2. Une la ruta relativa con `root` y la normaliza mediante `Path.resolve()`.
3. Comprueba que el resultado final siga contenido dentro de `root`.

La segunda y tercera comprobación impiden escapes con `..` y mediante
symlinks. Por ejemplo, si `enlace` apunta fuera del workspace,
`resolve(root, "enlace/secreto.txt")` será rechazada.

| Ruta solicitada | Resultado |
| --- | --- |
| `"notas/hoy.txt"` | Permitida |
| `"./notas/hoy.txt"` | Permitida |
| `"../secreto.txt"` | Rechazada |
| `"/etc/passwd"` | Rechazada |
| `"enlace/fuera.txt"` con un symlink que sale del root | Rechazada |

## Error

Cuando una ruta es absoluta o termina fuera del root, `resolve` lanza
`workspace.core.errors.PathOutsideWorkspaceError`. Las capas superiores no
deben ignorar ese error ni intentar resolver la ruta por otros medios.

## Uso en las operaciones

Las operaciones simples resuelven una ruta, por ejemplo `read`, `write`,
`mkdir` o `delete_file`. Las operaciones con dos rutas, como `copy`, `move` y
`copy_tree`, resuelven de forma independiente origen y destino. Las de
exploración, como `walk`, `glob` y `grep`, resuelven el directorio inicial.

No se debe usar directamente `root / path`, `Path.resolve()` ni otro
resolvedor para rutas que provengan de una herramienta MCP; hacerlo podría
saltar este límite de seguridad.

## Extensión

El paquete se mantiene separado para que futuras políticas relacionadas con
rutas —por ejemplo validación de nombres, enlaces simbólicos o reglas de
acceso— se incorporen en un único lugar, conservando el mismo límite de
seguridad.
