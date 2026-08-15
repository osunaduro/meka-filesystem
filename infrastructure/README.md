# Infraestructura y despliegue

Esta carpeta construye y ejecuta el servidor Filesystem MCP en Docker, en dos modos independientes que comparten la misma imagen (`Dockerfile`).

| | [`remote/`](remote/) | [`sandbox/`](sandbox/) |
| --- | --- | --- |
| Propósito | Servidor accesible desde fuera de esta máquina, detrás de tu propio proxy/túnel | Aislar una carpeta local para que un agente trabaje ahí sin poder tocar el resto del disco |
| Red | Red Docker externa `meka-network` (la creás vos, junto con tu proxy/túnel) | Ninguna — standalone, `docker compose up` y listo |
| Puerto | No publicado al host (`expose` interno únicamente) | Publicado solo en `127.0.0.1` — nunca alcanzable desde la red, ni con el firewall abierto |
| Auth soportada | `api-key` u `oidc` (nunca `none`: este modo asume que algo externo lo va a alcanzar) | `api-key` (default) o `none`, si confiás en todo lo que corre en esa máquina. `oidc` no aplica: no hay URL pública que validar |
| Qué NO resolvemos acá | El proxy inverso o túnel en sí (Nginx, Caddy, Cloudflare Tunnel, Tailscale...) — ver el contrato más abajo | Nada extra: es la parte simple |

Ambos modos comparten `Dockerfile` (Python + ripgrep + el paquete) y `generate-api-key.sh`.

## Requisitos comunes

- Docker Engine con Docker Compose.
- Un directorio del host que será el workspace administrado (o la carpeta a aislar, en modo sandbox).

## Modo remoto

```bash
cd infrastructure/remote
cp .env.example .env
docker network create meka-network   # una sola vez, si no existe
../generate-api-key.sh               # copiar el resultado a MEKA_API_KEY en .env
```

Editá `.env` con el directorio a exponer, el token, y la identidad de los archivos creados (`id -u` / `id -g` para tu propio UID/GID):

```dotenv
MEKA_UID=1000
MEKA_GID=1000
MEKA_WORKSPACE_PATH=/srv/meka/workspace
MEKA_API_KEY=un-token-largo-y-secreto
```

Levantar el servicio:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f filesystem-mcp
```

El contenedor escucha internamente en `/mcp/`, sin puerto publicado al host. Vos sos responsable de conectar un proxy inverso HTTPS o un túnel (Nginx, Caddy, Cloudflare Tunnel, Tailscale, lo que uses) a la red `meka-network`, y de que ese proxy/túnel cumpla el contrato de la siguiente sección.

Detener el servicio no borra el contenido del workspace, porque vive en el host:

```bash
docker compose down
```

Para rotar la clave: generá un nuevo token, actualizá `MEKA_API_KEY` en `.env`, y volvé a `docker compose up -d`.

### Contrato para tu proxy o túnel

La imagen ya corre Uvicorn con `--proxy-headers --forwarded-allow-ips "*"`, así que confía en los headers `X-Forwarded-*` que le lleguen. Tu proxy/túnel necesita:

1. **Reenviar el header `Authorization`** tal cual — sin esto, el servidor siempre responde `401` sin importar el modo de auth.
2. **Setear `X-Forwarded-Proto`** con el esquema real (`https`) — si no lo hace, algunos clientes MCP fallan al seguir redirects internos con esquema incorrecto.
3. Usar **HTTP/1.1** hacia el contenedor (el estándar en cualquier proxy moderno).
4. En modo `oidc`: reenviar también las rutas de discovery, en particular `/.well-known/oauth-protected-resource/mcp`, si el cliente MCP las necesita (por ejemplo ChatGPT).

Fuera de eso, cualquier proxy o túnel que cumpla ese contrato sirve — no hay nada específico de Nginx, Caddy, o un producto en particular.

### Modos de autenticación

`MEKA_AUTH_MODE` admite `api-key` (por defecto) y `oidc`. En modo `oidc` sumá las cuatro variables del proveedor:

```dotenv
MEKA_AUTH_MODE=oidc
MEKA_OIDC_ISSUER=https://id.example.com/realms/meka
MEKA_OIDC_AUDIENCE=https://archivo.example.com/mcp
MEKA_OIDC_JWKS_URL=https://id.example.com/realms/meka/protocol/openid-connect/certs
MEKA_OIDC_RESOURCE_URL=https://archivo.example.com/mcp
```

`MEKA_OIDC_RESOURCE_URL` debe ser la URL pública canónica del endpoint MCP (la misma que expone tu proxy/túnel). Ver [../../docs/autenticacion.md](../../docs/autenticacion.md) para la especificación completa.

## Modo sandbox ("jaula")

Para aislar una carpeta local sin exponer nada a internet — útil para que un agente trabaje sobre un directorio de pruebas sin poder tocar el resto de tu sistema:

```bash
cd infrastructure/sandbox
cp .env.example .env
../generate-api-key.sh   # copiar el resultado a MEKA_API_KEY en .env
```

Editá `.env` con la carpeta a aislar:

```dotenv
MEKA_WORKSPACE_PATH=/home/tu-usuario/carpeta-de-pruebas
MEKA_PORT=8787
MEKA_API_KEY=un-token-largo-y-secreto
```

```bash
docker compose up -d --build
```

El servidor queda disponible en `http://127.0.0.1:8787/mcp/` — solo desde esta máquina. No hace falta red externa, proxy, ni túnel: es la configuración entera. La carpeta indicada en `MEKA_WORKSPACE_PATH` es lo único alcanzable a través del servidor; el resolvedor de rutas rechaza salidas con `..`, rutas absolutas o symlinks que escapen de ese directorio.

Si preferís no exigir token en un uso 100% personal, `MEKA_AUTH_MODE=none` es aceptable acá — pero solo porque el puerto está atado a `127.0.0.1` y nunca sale de la máquina.

## Diagnóstico

| Síntoma | Revisar |
| --- | --- |
| `401 Unauthorized` | Token ausente o distinto a `MEKA_API_KEY` (modo `api-key`). |
| `401` en modo `oidc` | Token JWT ausente, expirado, o `issuer`/`audience` no coinciden con el proveedor. |
| `403` en modo `oidc` | Token válido pero sin el scope requerido por la herramienta. |
| `503` | `MEKA_API_KEY` no llegó al contenedor (modo `api-key`). |
| Error de permisos | UID/GID configurado y permisos de `MEKA_WORKSPACE_PATH`. |
| El proxy no resuelve el servicio (modo remoto) | Ambos contenedores deben compartir `meka-network`. |
| Redirect con esquema `http://` incorrecto (modo remoto) | Tu proxy/túnel no está seteando `X-Forwarded-Proto`; ver el contrato más arriba. |
| No conecta en modo sandbox | Confirmá que estás pegándole a `127.0.0.1:<MEKA_PORT>`, no a la IP de red del host. |
| `grep_text` falla | La imagen debe haberse construido con el Dockerfile incluido, que instala ripgrep. |
