# Directorio `home`

Este directorio está reservado por la convención de proyectos MEKA para datos persistentes del proyecto: archivos generados, logs, cachés, bases de datos o configuración local que deba sobrevivir a la recreación de un entorno.

No contiene código fuente ni forma parte del paquete Python distribuido.

## Estado en este proyecto

El servicio Filesystem MCP no usa ni monta `home/` actualmente. Su persistencia real es el directorio del host indicado por `MEKA_WORKSPACE_PATH`, que Docker monta como `/data/workspace` dentro del contenedor.

Por ello, no guarde aquí archivos que deban ser gestionados por MCP: colóquelos en el workspace externo configurado para el servicio.

El directorio se conserva para mantener la estructura estándar del proyecto y para una posible persistencia propia futura que no deba exponerse por MCP.
