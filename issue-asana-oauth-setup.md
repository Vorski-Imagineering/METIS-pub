# Issue: Asana MCP OAuth Setup Blocked - redirect_uri Mismatch

## Summary
Setting up Asana MCP integration via mcp-remote is blocked because the OAuth `redirect_uri` parameter is hardcoded to `localhost:3334` despite specifying `--callback-url`. This prevents the OAuth flow from working with nginx proxy at `https://hermes.the-gathering.earth/oauth/callback`.

## Status
**Blocked** - OAuth callback URL mismatch

## Installed Components

### 1. mcp-remote Package
- **Location:** `npx -y mcp-remote@latest`
- **Command in config.yaml:**
```yaml
mcp_servers:
  asana:
    enabled: true
    command: "npx"
    args:
      - "-y"
      - "mcp-remote@latest"
      - "https://mcp.asana.com/v2/mcp"
      - "3334"
      - "--static-oauth-client-info"
      - '{"client_id":"1214397903250164","client_secret":"9e7044101bd62c014801da6758b090e4"}'
      - "--resource"
      - "https://mcp.asana.com/v2"
      - "--callback-url"
      - "https://hermes.the-gathering.earth/oauth/callback"
```

### 2. Nginx Configuration
**File:** `/etc/nginx/sites-available/hermes.the-gathering.earth.conf`

```nginx
upstream mcp_oauth_callback {
    server 127.0.0.1:3334;
    keepalive 16;
}

# Shared OAuth callback endpoint for MCP servers
location /oauth/callback {
    proxy_pass http://mcp_oauth_callback/oauth/callback;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```



## Server File Paths

### Configuration Files
- **Hermes config:** `/opt/hermes/.hermes/config.yaml` (lines 310-343 contain mcp_servers config)
- **Nginx config:** `/etc/nginx/sites-available/hermes.the-gathering.earth.conf`
- **Nginx symlink:** `/etc/nginx/sites-enabled/hermes.the-gathering.earth.conf` → `../sites-available/hermes.the-gathering.earth.conf`

### mcp-remote Installation
- **Command path:** `/opt/hermes/.local/bin/npx`
- **Node modules cache:** `/opt/hermes/.npm/_npx/`
- **mcp-remote package:** `/opt/hermes/.npm/_npx/<hash>/node_modules/mcp-remote/`

### Working Directory
- **Repo location:** `/opt/hermes/Vorski-Imagineering/METIS-issues/`
- **Current branch:** `main`

## What Was Tried

### Attempt 1: Standard mcp-remote with --callback-url
```bash
npx -y mcp-remote@latest 'https://mcp.asana.com/v2/mcp' '3334' \
  --static-oauth-client-info '{"client_id":"1214397903250164","client_secret":"9e7044101bd62c014801da6758b090e4"}' \
  --callback-url 'https://hermes.the-gathering.earth/oauth/callback'
```

**Result:** OAuth URL generated with incorrect redirect_uri:
```
https://app.asana.com/-/oauth_authorize?...&redirect_uri=http%3A%2F%2Flocalhost%3A3334%2Foauth%2Fcallback...
```

### Attempt 2: Additional callback parameters
```bash
--callback-host 'hermes.the-gathering.earth'
--callback-port '443'
--callback-path '/oauth/callback'
```

**Result:** Still generates `localhost:3334` redirect_uri; crashes on port 443 due to permissions.

### Attempt 3: Manual callback URL construction
Manually modified the OAuth URL to use correct redirect_uri:
```
redirect_uri=https%3A%2F%2Fhermes.the-gathering.earth%2Foauth%2Fcallback
```

**Result:** Code mismatch error because PKCE challenge is tied to original request.

## Where It's Breaking

### Root Cause
The `--callback-url` parameter in mcp-remote v0.1.x does NOT control the `redirect_uri` in the OAuth authorization URL. It's used for a different purpose (likely callback server binding), but the OAuth URL still defaults to `http://localhost:3334/oauth/callback`.

### Error Message
```
Authorization error: InvalidGrantError: The `code` provided was invalid.
```

This occurs because:
1. Asana redirects to `https://hermes.the-gathering.earth/oauth/callback?code=xxx`
2. mcp-remote expects callbacks at `http://localhost:3334/oauth/callback`
3. Even if nginx proxies correctly, the PKCE `code_verifier` doesn't match

## Required Fix

**Option A:** Wait for mcp-remote to fix `--callback-url` to properly set redirect_uri

**Option B:** Implement workaround:
1. Nginx subdomain to handle localhost redirects
2. Custom reverse proxy that rewrites the OAuth response HTML
3. Manual OAuth flow with proper redirect_uri

## Asana OAuth Details
- **Client ID:** 1214397903250164
- **Authorization URL:** `https://app.asana.com/-/oauth_authorize`
- **Token URL:** `https://app.asana.com/-/oauth_token`
- **MCP Server:** `https://mcp.asana.com/v2/mcp`

---
*Created: 2026-04-30 09:06*
*Assign to: Sajjad*
