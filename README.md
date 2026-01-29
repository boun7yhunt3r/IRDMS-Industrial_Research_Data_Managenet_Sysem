# Shepard Local Setup Guide (Windows 11 + WSL2)

Quick guide to run Shepard on Windows 11 using Docker Desktop and WSL2.

## Prerequisites

- Windows 11
- 32GB RAM recommended (8GB minimum)
- Pc with good specs :)

## 1. Install WSL2

```powershell
# Run in PowerShell (Admin)
wsl --install
```

Restart your PC.

## 2. Install Docker Desktop

Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

**Enable WSL2 integration:**
1. Docker Desktop → Settings → Resources → WSL Integration
2. Enable integration with your WSL distro (e.g., Ubuntu)
3. Apply & Restart

**Verify in WSL:**
```bash
docker --version
docker compose version
```

## 3. Clone Shepard Repository

```bash
cd ~
git clone https://gitlab.com/dlr-shepard/shepard.git
cd shepard/infrastructure
```

## 4. Create Data Directories

```bash
mkdir -p ~/shepard-data/{backend/logs,backend/config,neo4j/{logs,plugins,data},mongodb/{db,configdb},timescaledb}
chmod -R 777 ~/shepard-data
```

## 5. Update docker-compose.yml

### Fix Volume Paths

Replace all `/opt/shepard/` paths with `/home/YOUR_USERNAME/shepard-data/`

**Example changes:**
```yaml
backend:
  volumes:
    - /home/YOUR_USERNAME/shepard-data/backend/logs:/deployments/logs
    - /home/YOUR_USERNAME/shepard-data/backend/config:/home/jboss/.shepard

neo4j:
  volumes:
    - /home/YOUR_USERNAME/shepard-data/neo4j/logs:/logs
    - /home/YOUR_USERNAME/shepard-data/neo4j/plugins:/plugins
    - /home/YOUR_USERNAME/shepard-data/neo4j/data:/var/lib/neo4j/data

mongodb:
  volumes:
    - /home/YOUR_USERNAME/shepard-data/mongodb/db:/data/db
    - /home/YOUR_USERNAME/shepard-data/mongodb/configdb:/data/configdb

timescaledb:
  volumes:
    - /home/YOUR_USERNAME/shepard-data/timescaledb:/var/lib/postgres/data
```

### Adjust Memory Settings (if 16GB RAM)

```yaml
backend:
  environment:
    JAVA_OPTS: "-Xms2G -Xmx2G"

neo4j:
  environment:
    NEO4J_server_memory_heap_initial__size: 2G
    NEO4J_server_memory_heap_max__size: 2G
    NEO4J_server_memory_pagecache_size: 3G

mongodb:
  command: --wiredTigerCacheSizeGB 1.0
```

### Add Keycloak Service

```yaml
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    container_name: shepard-keycloak
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
      KC_HTTP_PORT: 8180
    ports:
      - "8180:8180"
    command: start-dev --http-port=8180
    networks:
      - shepard
    volumes:
      - keycloak_data:/opt/keycloak/data
```

### Add Volume Declaration (at bottom)

```yaml
volumes:
  keycloak_data:
  grafana-storage: {}
```

### Expose Frontend and Backend Ports

```yaml
frontend:
  ports:
    - "3000:3000"

backend:
  ports:
    - "8080:8080"
```

## 6. Create .env File

```bash
cp .env.example .env
nano .env
```

**Minimal .env configuration:**

```bash
# URLs
BACKEND_URL=http://localhost:8080/
FRONTEND_URL=http://localhost:3000/

# Frontend Auth
FRONTEND_AUTH_SECRET= ****Fill_in*****
CLIENT_ID= ****Fill_in*****
SESSION_REFRESH_INTERVAL= ****Fill_in*****

# OIDC (will be updated after Keycloak setup)
OIDC_AUTHORITY= ****Fill_in*****
OIDC_PUBLIC= ****Fill_in*****
OIDC_ROLE= ****Fill_in*****

# Neo4j
NEO4J_PW= ****Fill_in*****

# MongoDB
MONGO_ROOT_USERNAME= ****Fill_in*****
MONGO_ROOT_PASSWORD= ****Fill_in*****
MONGO_DATABASE= ****Fill_in*****
MONGO_USERNAME= ****Fill_in*****
MONGO_PASSWORD= ****Fill_in*****

# PostgreSQL
POSTGRES_DB= ****Fill_in*****
POSTGRES_USER= ****Fill_in*****
POSTGRES_PASSWORD= ****Fill_in*****
POSTGRES_SHEPARD_USER= ****Fill_in*****
POSTGRES_SHEPARD_USER_PW= ****Fill_in*****

# Features
SHEPARD_SPATIAL_DATA_ENABLED= ****Fill_in*****
SHEPARD_MIGRATION_MODE_ENABLED= ****Fill_in*****
SHEPARD_AUTOCONVERT_INT= ****Fill_in*****

# Monitoring
GRAFANA_ADMIN_USERNAME= ****Fill_in*****
GRAFANA_ADMIN_PASSWORD= ****Fill_in*****

# Docker profiles
COMPOSE_PROFILES=

# InfluxDB
INFLUX_PW= ****Fill_in*****
```

Generate a secure secret:
```bash
openssl rand -base64 32
```

## 7. Start Shepard

```bash
docker compose pull
docker compose up -d
```

Wait ~60 seconds for all services to start.

**Verify all containers are running:**
```bash
docker ps
```

## 8. Configure Keycloak

### Access Keycloak Admin
Open: `http://localhost:8180/admin`

Login: `admin` / `admin`

### Set Frontend URL
1. **Realm Settings** → **General**
2. **Frontend URL:** `http://localhost:8180`
3. **Save**

### Create Client
1. **Clients** → **Create client**
2. **General Settings:**
   - Client ID: `shepard-frontend`
   - Client Protocol: `openid-connect`
   - **Next**
3. **Capability config:**
   - Client authentication: **OFF**
   - Standard flow: **ON**
   - **Next**
4. **Login settings:**
   - Root URL: `http://localhost:3000`
   - Valid redirect URIs: `http://localhost:3000/api/auth/callback/oidc`
   - Valid post logout redirect URIs: `http://localhost:3000`
   - Web origins: `http://localhost:3000`
   - **Save**

### Get OIDC Public Key
1. **Realm Settings** → **Keys**
2. Find **RS256** with **Use: SIG**
3. Click **Public key** button
4. Copy the entire key (starts with `MII...`)

### Update .env with Public Key
```bash
nano .env
```

Update:
```bash
OIDC_PUBLIC= ****Fill_in*****
```

**Restart containers:**
```bash
docker compose down
docker compose up -d
```

### Create Test User
1. Keycloak Admin → **Users** → **Add user**
2. Username: `testuser`
3. **Save**
4. **Credentials** tab:
   - Set password: `password`
   - Temporary: **OFF**
   - **Save**

## 9. Access Shepard

Open: `http://localhost:3000`

Click **Sign in** → Login with `testuser` / `password`

## Service URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8080 |
| Keycloak | http://localhost:8180 |
| Neo4j | bolt://localhost:7687 |

## Troubleshooting

### "Client not found" error
- Verify client `shepard-frontend` exists in Keycloak
- Check `CLIENT_ID` in `.env` matches exactly

### "Invalid Authentication" error
- Verify `OIDC_PUBLIC` key is correct (copy from Keycloak Keys)
- Restart containers after changing `.env`

### Frontend can't reach Keycloak
- Use `OIDC_AUTHORITY=http://shepard-keycloak:8180/...` (not localhost)
- Ensure Keycloak Frontend URL is set to `http://localhost:8180`

### Keycloak settings lost on restart
- Verify `keycloak_data` volume exists in docker-compose.yml
- Don't use `docker compose down -v` (removes volumes)

### Check logs
```bash
docker logs infrastructure-frontend-1
docker logs infrastructure-backend-1
docker logs shepard-keycloak
```

## Stop Shepard

```bash
docker compose down
```

## Complete Reset (deletes all data)

```bash
docker compose down -v
rm -rf ~/shepard-data/*
```

## Notes

- This setup is for **local development only**
- No SSL/TLS encryption
- Default passwords should be changed for production
- Keycloak runs in development mode (`start-dev`)


This setup guide was created to document the local installation process for Shepard on Windows 11 with WSL2. It is based on the official Shepard deployment documentation and adapted for Windows/WSL environments.

Shepard Project License
Shepard is developed by DLR (German Aerospace Center). Check the official Shepard repository for license information.

© 2025 [Aravind Asha]. All rights reserved.
This guide may not be reproduced or distributed without permission.
