# Operaciones de filesystem

Este paquete reúne las funciones que realizan trabajo sobre el workspace. Cada operación recibe un `root: pathlib.Path` y una ruta relativa; antes de acceder al filesystem debe resolverla con `workspace.internal.path.resolve`.

## Operaciones

| Grupo | Funciones |
| --- | --- |
| Información | `exists`, `stat`, `list`, `walk`, `glob`, `grep`, `list_allowed` |
| Lectura | `read`, `read_range`, `head`, `tail`, `read_many`, `read_media` |
| Escritura | `write`, `write_media`, `append`, `replace_lines`, `edit_text`, `edit_text_many`, `truncate` |
| Gestión | `mkdir`, `rmdir`, `delete_file`, `copy`, `copy_tree`, `move` |

Las operaciones no aplican `chmod` ni `chown`: el acceso y la propiedad de los archivos dependen del usuario efectivo del proceso y de los permisos del filesystem montado.

## Convenciones

- Las rutas deben ser relativas al `root`; las absolutas se rechazan.
- `glob` usa la sintaxis de `pathlib`. Para recorrer subdirectorios use `**`, por ejemplo `**/*.md`.
- `walk`, `glob` y `grep` devuelven iteradores para que el consumidor pueda limitar o procesar resultados progresivamente.
- `grep` requiere el ejecutable `rg` (ripgrep) disponible en el entorno.
- `edit_text` localiza el texto a reemplazar por contenido exacto (no por número de línea) y admite `dry_run=True` para previsualizar el diff sin escribir en disco.
- `edit_text_many` aplica una lista de `TextEdit` en secuencia sobre una copia en memoria; si alguna falla, no se escribe nada (todo o nada).
- `read_many` continúa aunque falle la lectura de algún path individual; el error queda en el resultado correspondiente en vez de abortar el lote.
- `list_allowed` siempre devuelve una lista de un elemento (`[root]`), ya que el workspace soporta un único root configurado.

El adaptador MCP impone límites de resultados a las operaciones que devuelven iteradores; la biblioteca core no impone esos límites por sí misma.
