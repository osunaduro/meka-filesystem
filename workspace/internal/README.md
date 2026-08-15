# Componentes internos

Este paquete reúne infraestructura interna del dominio filesystem. Sus módulos dan soporte al servidor y a las operaciones core, pero no se consideran parte de una API estable para consumidores externos.

## Contenido

| Paquete | Responsabilidad |
| --- | --- |
| [config/](config/README.md) | Obtiene la configuración de ejecución, hoy el root del workspace. |
| [path/](path/README.md) | Resuelve y valida rutas para que no salgan del workspace autorizado. |

La separación evita que detalles como variables de entorno o políticas de seguridad se filtren al núcleo de operaciones. Si se agregan nuevos módulos internos, deben mantener esta misma orientación: servir a la implementación, no crear una segunda API pública.
