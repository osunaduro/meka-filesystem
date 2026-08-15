# Despliegue MCP Filesystem

## Requisitos

- Docker Engine y Docker Compose.
- Red Docker externa `meka-network`, compartida con Nginx.
- Un directorio del host que será el workspace completo del cliente.
- Nginx con HTTPS para `archivo.mekaweb.com.ar`.

## 1. Preparar red y workspace

Crear la red sólo si todavía no existe:

```bash
docker network create meka-network
```

Crear el directorio que MCP podrá administrar:

```bash
mkdir -p /srv/meka/workspace
```

Dentro de ese directorio el cliente puede crear cualquier estructura:

```text
/srv/meka/workspace/
├── canciones/
├── documentos/
├── balances/
└── mi-aplicacion-python/
```

## 2. Configurar entorno

Desde `infrastructure`, copiar el ejemplo o completar el `.env` existente:

```bash
cp .env.example .env
./generate-api-key.sh
```

Pegar la clave generada en `.env`:

```dotenv
PROJECT_NAME=meka-filesystem
MEKA_UID=1000
MEKA_GID=1000
MEKA_WORKSPACE_PATH=/srv/meka/workspace
MEKA_AUTH_MODE=api-key
MEKA_API_KEY=pegar-aqui-la-clave-generada
```

`MEKA_AUTH_MODE` admite `api-key` (por defecto), `oidc` y `none`. En modo
`oidc` se añaden las variables `MEKA_OIDC_ISSUER`, `MEKA_OIDC_AUDIENCE`,
`MEKA_OIDC_JWKS_URL` y `MEKA_OIDC_RESOURCE_URL` en lugar de `MEKA_API_KEY`;
ver [autenticacion.md](autenticacion.md).

Usar `id -u` e `id -g` para obtener UID y GID del usuario dueño del workspace.
El archivo `.env` es secreto y no debe versionarse.

## 3. Iniciar

```bash
cd infrastructure
docker compose up -d --build
docker compose ps
docker compose logs -f filesystem-mcp
```

El servicio no publica `ports:` al host. Queda disponible sólo para
contenedores unidos a `meka-network`.

## 4. Configurar Nginx

En el virtual host HTTPS de `archivo.mekaweb.com.ar`:

```nginx
location /mcp/ {
    proxy_pass http://filesystem-mcp:8000/mcp/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Authorization $http_authorization;
}
```

Nginx debe pertenecer a `meka-network`. Docker resuelve el alias
`filesystem-mcp` dentro de esa red.

## 5. Cliente MCP

En modo `api-key`, configurar el endpoint y token:

```text
URL: https://archivo.mekaweb.com.ar/mcp/
Authorization: Bearer <MEKA_API_KEY>
```

En modo `oidc`, el punto de acceso es el mismo (`https://archivo.mekaweb.com.ar/mcp/`),
pero el cliente intercambia tokens con el proveedor OIDC mediante el flujo
OAuth. El servidor publica `/.well-known/oauth-protected-resource/mcp` para el
descubrimiento MCP y valida el JWT y los scopes que el cliente recibe.

## Mantenimiento

Actualizar el servicio:

```bash
cd infrastructure
docker compose up -d --build
```

Detenerlo sin borrar los archivos del cliente:

```bash
docker compose down
```

El workspace se conserva porque está montado desde el host. Para rotar la
clave, generar otra, actualizar `MEKA_API_KEY` en `.env` y ejecutar
`docker compose up -d`.

## Diagnóstico

- Error de red externa: crear `meka-network` y conectar Nginx a ella.
- Error de permisos: revisar `MEKA_UID`, `MEKA_GID` y permisos de
  `MEKA_WORKSPACE_PATH`.
- `401 Unauthorized`: en `api-key`, token ausente o incorrecto; en `oidc`,
  token JWT ausente, expirado o con `issuer`/`audience` no coincidentes.
- `403 Forbidden` en `oidc`: token válido pero sin el scope requerido por la
  herramienta (`filesystem:read`, `filesystem:write` o `filesystem:delete`).
- `503`: `MEKA_API_KEY` no llegó al contenedor (sólo en modo `api-key`).
- Nginx no resuelve `filesystem-mcp`: ambos contenedores no comparten
  `meka-network`.
