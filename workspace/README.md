# Paquete `workspace`

`workspace` contiene el código Python del proyecto. Se divide en una capa reutilizable de filesystem, componentes internos de soporte y el adaptador de red MCP.

```text
workspace/
├── core/       Operaciones, modelos y errores del dominio
├── internal/   Configuración y políticas internas de seguridad
└── servers/    Aplicación FastMCP expuesta por HTTP
```

## Capas

- [core/](core/README.md) no depende de Docker ni de FastMCP. Sus funciones reciben un root y rutas relativas, por lo que pueden reutilizarse desde Python.
- [internal/](internal/README.md) contiene detalles de implementación, como la configuración del root y la resolución segura de rutas. No es API pública.
- [servers/](servers/README.md) adapta el núcleo a herramientas MCP y aplica autenticación HTTP.

Las dependencias fluyen desde `servers` hacia `core` e `internal`; el núcleo no depende del servidor. Toda ruta de cliente debe pasar por `internal.path.resolve` antes de tocar el filesystem.
