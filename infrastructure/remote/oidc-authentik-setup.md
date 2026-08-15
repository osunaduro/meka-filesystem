# OIDC — MEKA Filesystem en Authentik

Provider/Application creados en Authentik (`https://auth.mekaweb.com.ar`) para exponer `archivo.mekaweb.com.ar` a clientes OAuth (Claude web/Android, ChatGPT, etc.).

- Application slug: `meka-filesystem`
- Provider: "MEKA Filesystem" (pk 1)
- Client type: confidential
- Client ID: `rAzXQclaDqQGJO6YlE9aWAmfkAfFzaA01gX3vYgf`
- Client Secret: `eCXM1u2vqijm1skewTGklBTOffsHIrlllvixDQTgj4xNFp3pL8OZpaf4NX7gGw3toJqrt9joIHT3xIfkA9oiJCZklBnehRmLNjeqS5lk0V6omz3LuQTwslLsZXtooiTI`
- Redirect URI configurado: regex `^https://claude\.ai/.*$` (provisorio — la versión de Authentik instalada, 2025.2.4, no soporta registro dinámico de clientes, así que no sabemos la ruta exacta que usa Claude hasta probarlo. Si al agregar el conector en Claude falla el redirect, avisame la URL exacta del error y ajusto este regex a la ruta real, más restrictivo).

`filesystem-mcp` quedó en modo `oidc` (`meka-filesystem/infrastructure/remote/.env`):

```
MEKA_OIDC_ISSUER=https://auth.mekaweb.com.ar/application/o/meka-filesystem/
MEKA_OIDC_AUDIENCE=rAzXQclaDqQGJO6YlE9aWAmfkAfFzaA01gX3vYgf
MEKA_OIDC_JWKS_URL=https://auth.mekaweb.com.ar/application/o/meka-filesystem/jwks/
MEKA_OIDC_RESOURCE_URL=https://archivo.mekaweb.com.ar/mcp
```

`MEKA_OIDC_AUDIENCE` es el `client_id` (no una URL) porque Authentik en esta versión no soporta "resource indicators" (RFC 8707) — el claim `aud` del JWT que emite es siempre el client_id. Es válido igual: MEKA Filesystem solo compara que el `aud` del token coincida con lo configurado.

## Para agregar el conector en Claude (web o Android)

1. En claude.ai: Configuración → Conectores → Agregar conector personalizado.
2. URL: `https://archivo.mekaweb.com.ar/mcp/`
3. Si pide iniciar sesión automáticamente (vía descubrimiento OAuth): debería redirigir a Authentik para loguearte con el usuario admin (`proyectos@mekaweb.com.ar`) u otro usuario que crees ahí.
4. Si pide Client ID / Client Secret manualmente (esperable, por la falta de auto-registro): usar los valores de arriba.
5. Si el login redirige mal o da error de "redirect_uri inválida": copiarme el mensaje/URL exacta para ajustar el provider en Authentik.

## Pendiente

- Authentik está en 2025.2.4 (última disponible: 2026.5.6). Versiones más nuevas podrían agregar registro dinámico de clientes, lo que simplificaría este flujo. No se actualizó en esta sesión — evaluar aparte.
- El `client_secret` queda en texto plano en este archivo y en el `.env` de meka-filesystem. Mismo nivel de sensibilidad que el resto de `meka-infra/.env` — no versionar en git sin cifrar.
