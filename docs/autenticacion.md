# Especificación de Autenticación para MEKA Filesystem MCP

## Objetivo

Implementar soporte para autenticación OAuth/OIDC **sin convertir MEKA Filesystem en un Authorization Server**.

El objetivo del proyecto es que MEKA Filesystem funcione con cualquier proveedor OIDC estándar (Authentik, Keycloak, Auth0, Okta, Azure Entra ID, etc.) y continúe ofreciendo el modo API Key para instalaciones simples.

---

# Principios de diseño

## 1. MEKA Filesystem NO implementa OAuth

No se desarrollará un Authorization Server propio.

MEKA Filesystem únicamente actuará como **OAuth Resource Server**.

Toda la autenticación será responsabilidad de un proveedor OIDC externo.

---

## 2. El proveedor de identidad es intercambiable

El servidor no deberá depender de Authentik.

Authentik será el proveedor utilizado por la infraestructura oficial de MEKA (`meka-infra`), pero cualquier implementación OIDC compatible deberá poder utilizarse mediante configuración.

Ejemplos:

* Authentik
* Keycloak
* Auth0
* Okta
* Azure Entra ID
* cualquier proveedor OIDC estándar

---

## 3. La autenticación será configurable

La configuración usa exclusivamente variables de entorno. No se introducen
archivos YAML ni otros mecanismos de configuración.

Se soportan tres modos excluyentes mediante `MEKA_AUTH_MODE`:

```dotenv
MEKA_AUTH_MODE=none
```

Servidor sin autenticación.

Uso exclusivo para desarrollo.

---

```dotenv
MEKA_AUTH_MODE=api-key
MEKA_API_KEY=<clave-estatica>
```

Modo por defecto.

Utiliza una API Key estática.

Pensado para:

* instalaciones personales
* uso doméstico
* pruebas
* usuarios que no desean instalar un proveedor OAuth.

---

```dotenv
MEKA_AUTH_MODE=oidc
MEKA_OIDC_ISSUER=https://id.example.com/realms/meka
MEKA_OIDC_AUDIENCE=https://archivo.example.com/mcp
MEKA_OIDC_JWKS_URL=https://id.example.com/realms/meka/protocol/openid-connect/certs
MEKA_OIDC_RESOURCE_URL=https://archivo.example.com/mcp
```

Modo empresarial o multiusuario.

Utiliza un proveedor OAuth/OIDC externo.

En modo `oidc`, las cuatro variables `MEKA_OIDC_*` son obligatorias. El
issuer, audience y JWKS deben corresponder al proveedor OIDC elegido;
`MEKA_OIDC_RESOURCE_URL` es la URL pública canónica del endpoint MCP.

---

# Responsabilidad del Resource Server

Cuando `auth.mode = oidc`, MEKA Filesystem únicamente deberá:

* validar la firma del JWT mediante JWKS
* validar `issuer`
* validar `audience`
* validar expiración (`exp`)
* validar scopes
* autorizar el acceso a las herramientas
* publicar OAuth Protected Resource Metadata para descubrimiento MCP
* devolver `401` y `WWW-Authenticate` cuando falta el token o no es válido

No deberá:

* emitir tokens
* realizar login
* almacenar usuarios
* administrar sesiones
* implementar refresh tokens
* implementar consentimiento OAuth

## Scopes

La implementación define únicamente los siguientes scopes:

| Scope | Herramientas |
| --- | --- |
| `filesystem:read` | Existencia, metadata, listado, recorridos, búsqueda, lectura, lectura de Excel y de outline DOCX. |
| `filesystem:write` | Escritura, append, reemplazo de líneas, truncate, creación, copia, movimiento, edición de páginas PDF, escritura de Excel, y creación/edición de DOCX. |
| `filesystem:delete` | Eliminación de archivos y directorios. |

Los scopes controlan herramientas, no workspaces. Una instancia siempre opera
sobre el mismo root configurado, independientemente de la identidad del token.

Toda esa funcionalidad pertenece al Authorization Server.

---

# Compatibilidad con ChatGPT

Esta implementación permitirá utilizar MEKA Filesystem con clientes MCP que requieren OAuth, incluyendo ChatGPT.

El flujo esperado será:

```
ChatGPT
      │
      ▼
Proveedor OAuth (Authentik u otro)
      │
      ▼
Access Token JWT
      │
      ▼
MEKA Filesystem MCP
(Resource Server)
```

---

# Alcance de esta implementación

Implementar únicamente:

* soporte OIDC
* validación de JWT
* validación de scopes
* configuración del proveedor
* integración con FastMCP

No implementar:

* servidor OAuth
* gestión de usuarios
* interfaz de autenticación
* administración de credenciales

---

# Infraestructura oficial de MEKA

La distribución oficial de MEKA utilizará:

```
meka-infra
    ├── Authentik
    ├── Nginx Proxy Manager
    ├── Cloudflared
    └── Portainer
```

Authentik será la implementación de referencia para la infraestructura oficial, pero **MEKA Filesystem no deberá depender de él**.

## Límite de workspace

MEKA Filesystem no es un servicio multi-tenant ni un SaaS. Cada instancia
administra un único workspace definido por su propietario mediante
`MEKA_WORKSPACE_ROOT`.

La identidad autenticada no selecciona ni modifica ese workspace. No se
implementan aislamiento por usuario, mapeo usuario → workspace ni selección
dinámica de roots.

---

# Objetivo final

Mantener un servidor MCP:

* simple de instalar;
* independiente del proveedor de identidad;
* compatible con la especificación OAuth/OIDC para MCP;
* reutilizable por cualquier usuario con el proveedor OIDC de su elección;
* compatible con clientes MCP que requieren OAuth, como ChatGPT.

**No se implementará un Authorization Server propio. Únicamente se implementará el rol de Resource Server conforme a la especificación MCP OAuth/OIDC.**
