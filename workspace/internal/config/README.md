# Configuración interna

Este paquete concentra la configuración de ejecución que usa el servidor y
sus componentes internos. No forma parte de la API pública de la biblioteca.

## Configuración actual

`config.py` expone `WORKSPACE_ROOT`, un `pathlib.Path` obtenido de la variable
de entorno `MEKA_WORKSPACE_ROOT`.

`WORKSPACE_ROOT` define el directorio raíz que el servidor MCP puede
administrar. Todas las rutas recibidas por las herramientas son relativas a
ese directorio y el resolvedor de rutas evita que puedan salir de él.

Si `MEKA_WORKSPACE_ROOT` no está definida, el valor por defecto es
`/data/workspace`, que coincide con el volumen montado por Docker Compose.

## Evolución

El directorio se mantiene aunque hoy contenga un único módulo para permitir
agregar configuración interna relacionada —por ejemplo límites operativos,
logging o integración de infraestructura— sin mezclarla con el dominio de
filesystem.
