# Núcleo del filesystem

El paquete `workspace.core` reúne operaciones reutilizables sobre un árbol de
archivos delimitado. No depende de MCP ni de Docker: cada función recibe un
`root: pathlib.Path` y una ruta relativa a ese root. La referencia detallada
de cada operación está en [ops/README.md](ops/README.md).

Los servidores MCP están en `workspace.servers.filesystem_http` (HTTP/OAuth) y
`workspace.servers.filesystem_stdio` (STDIO); actúan como adaptadores de estas
funciones y nunca entregan el root al cliente. Ambos comparten la definición
de herramientas en `workspace.servers._tools`.

## Límite de rutas

Todas las operaciones usan `workspace.internal.path.resolve`. El resolvedor
rechaza rutas absolutas y cualquier ruta que, después de resolver `..` o
symlinks, salga del root permitido. `PathOutsideWorkspaceError` representa
ese rechazo.

## Operaciones disponibles

| Área | Operaciones |
| --- | --- |
| Información | `exists`, `stat`, `list`, `walk`, `glob`, `grep` |
| Lectura | `read`, `read_range`, `head`, `tail` |
| Escritura | `write`, `append`, `replace_lines`, `truncate` |
| Directorios y archivos | `mkdir`, `rmdir`, `delete_file`, `copy`, `copy_tree`, `move` |

`walk`, `glob` y `grep` devuelven iteradores para evitar cargar todos los
resultados en memoria. En `glob`, los patrones recursivos deben usar `**`,
por ejemplo `**/*.py`.

## Modelos y dependencias

- `models.py` define `FileInfo`, `FileType` y `GrepMatch`.
- `errors.py` define la jerarquía de errores del dominio.
- La mayoría de las operaciones usan `pathlib`; `grep` ejecuta el binario
  externo `rg` (ripgrep).

## Uso desde Python

```python
from pathlib import Path

from workspace.core.ops import read, write

root = Path("/srv/meka/workspace")
write(root, "notas/hola.txt", "Hola\\n")
print(read(root, "notas/hola.txt"))
```

Las operaciones no crean el root automáticamente: el proceso que las usa
debe asegurar que exista y tenga los permisos apropiados.
