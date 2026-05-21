# 🔑 Cómo Renovar el Access Token de Meta

El access token expira periódicamente (cada 1-2 horas para tokens cortos, 60 días para tokens largos). Cuando veas este error:

```
Error validating access token: Session has expired
```

Necesitás renovar el token. Acá está cómo hacerlo:

## Método Rápido (Recomendado)

### 1. Andá al Graph API Explorer
https://developers.facebook.com/tools/explorer/

### 2. Seleccioná tu app
- En el dropdown "Meta App", elegí tu app creada

### 3. Agregá permisos
Click en "Permissions" y agregá:
- `ads_read`
- `ads_management`
- `business_management`

### 4. Generá el token
- Click en "Generate Access Token"
- Autorizá los permisos
- **Copiá el token** que aparece

### 5. Actualizá el .env

Abrí el archivo `.env` y reemplazá la línea:

```bash
ACCESS_TOKEN=tu_nuevo_token_aqui
```

### 6. Listo!

Ahora ejecutá de nuevo:
```bash
./run_ads.sh
```

---

## Obtener Token de Larga Duración (60 días)

Si querés un token que dure más tiempo:

### Opción A: Desde Graph API Explorer

1. Después de generar el token corto (pasos arriba)
2. Click en el ícono de información (ⓘ) al lado del token
3. Click en "Extend Access Token"
4. Copiá el nuevo token extendido
5. Actualizá `.env`

### Opción B: Usando curl

```bash
curl -i -X GET "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=TU_APP_ID&client_secret=TU_APP_SECRET&fb_exchange_token=TU_TOKEN_CORTO"
```

Reemplazá:
- `TU_APP_ID`: tu App ID
- `TU_APP_SECRET`: tu App Secret
- `TU_TOKEN_CORTO`: el token que acabás de generar

Te va a devolver un `access_token` de larga duración.

---

## Verificar si un token está vivo

```bash
curl -X GET "https://graph.facebook.com/debug_token?input_token=TU_TOKEN&access_token=TU_TOKEN"
```

Te dirá:
- Si está válido
- Cuándo expira
- Qué permisos tiene

---

## Automatizar renovación (Opcional)

Para clientes donde corres pauta activamente y no querés renovar manualmente cada 60 días:

### Usar Business System User Token (No expira)

1. En Business Manager:
   - Settings → Business Settings
   - Users → System Users
   - Create System User
   - Assign ad account access
   - Generate token

Este token **no expira** pero requiere configuración más compleja.

---

## Troubleshooting

### "Token is invalid"
→ Generá uno nuevo desde Graph API Explorer

### "Permissions not granted"
→ Verificá que agregaste `ads_read` y `ads_management`

### "Ad account not found"
→ Verificá que el `AD_ACCOUNT_ID` en `.env` es correcto

---

**Renovación recomendada:** Cada mes, generá un token nuevo de 60 días para evitar que expire en medio de un reporte.
