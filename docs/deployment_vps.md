# Guía de instalación y despliegue en VPS

## Alcance
Este documento describe la instalación, configuración y despliegue del backend Django + DRF + Channels y su panel admin en un VPS. Incluye servicios, base de datos, seguridad, monitoreo y mantenimiento.

## Requisitos previos del sistema
- VPS con Ubuntu 22.04 LTS o Debian 12
- 2 vCPU, 4 GB RAM, 20 GB disco (mínimo recomendado)
- Acceso SSH con usuario sudo
- Dominio o subdominio para el panel (opcional pero recomendado)

## Dependencias de software
- Python 3.11+
- PostgreSQL 14+ (recomendado en producción)
- Redis 6+
- Nginx o Apache como reverse proxy
- Node.js (solo si luego se agrega frontend separado)

### Dependencias opcionales por motor
- MySQL/MariaDB: servidor MySQL y headers de cliente
- Oracle: Oracle Instant Client y SDK
- SQL Server: ODBC Driver 18 for SQL Server
- MongoDB: MongoDB 6+ y acceso a puerto 27017

## Variables de entorno
Crear archivo `.env` en `/opt/parallax/backend/.env`:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=example.com,api.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://admin.example.com,https://api.example.com
DOMAIN_DB_BACKEND=postgres
DB_NAME=parallax_admin
DB_USER=parallax
DB_PASSWORD=strong-password
DB_HOST=127.0.0.1
DB_PORT=5432
SQLITE_PATH=/opt/parallax/backend/db.sqlite3
MYSQL_DRIVER=pymysql
DJANGO_DB_BACKEND=sqlite
MONGO_URI=mongodb://127.0.0.1:27017
MONGO_DB=parallax_admin
REDIS_URL=redis://127.0.0.1:6379/0
PLUGIN_SHARED_SECRETS={"api-key-1":"shared-secret-1"}
PLUGIN_ALLOWED_DRIFT_SECONDS=60
PLUGIN_EVENT_TTL_SECONDS=300
```

## Instalación paso a paso

### 1) Crear usuario del sistema
> Puedes usar cualquier nombre de usuario, se usará `parallax` en ésta guía.

```bash
sudo adduser --disabled-password --gecos "" parallax
sudo usermod -aG sudo parallax
```

### 2) Instalar dependencias base
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential \
    postgresql postgresql-contrib redis-server nginx git
```

### 3) Crear directorio de despliegue
```bash
sudo mkdir -p /opt/parallax/backend
sudo chown -R parallax:parallax /opt/parallax/backend
```

### 4) Clonar el proyecto
```bash
sudo -u parallax git clone https://github.com/Parallax-Development/AdminTools-Backend.git /opt/parallax/backend
```

### 5) Crear entorno virtual e instalar dependencias
```bash
sudo -u parallax python3 -m venv /opt/parallax/backend/.venv
sudo -u parallax /opt/parallax/backend/.venv/bin/pip install -U pip
sudo -u parallax /opt/parallax/backend/.venv/bin/pip install -r /opt/parallax/backend/requirements.txt
```

## Configuración de base de datos

### PostgreSQL (producción)
> Cambia `parallax_admin`, `parallax` y `strong-password` por tus propios valores.

```bash
sudo -u postgres psql
CREATE DATABASE parallax_admin;
CREATE USER parallax WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE parallax_admin TO parallax;
\q
```

### Migraciones
```bash
cd /opt/parallax/backend
sudo -u parallax /opt/parallax/backend/.venv/bin/python manage.py migrate
```

## Configuración de servicios web

### Opción A: Nginx + Daphne (recomendado)

#### Servicio systemd para Daphne
Crear `/etc/systemd/system/parallax-backend.service`:

```service
[Unit]
Description=Parallax Backend ASGI
After=network.target

[Service]
User=parallax
Group=parallax
WorkingDirectory=/opt/parallax/backend
EnvironmentFile=/opt/parallax/backend/.env
ExecStart=/opt/parallax/backend/.venv/bin/daphne -b 127.0.0.1 -p 8000 parallax_admin.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activar y arrancar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable parallax-backend
sudo systemctl start parallax-backend
```

#### Nginx reverse proxy
Crear `/etc/nginx/sites-available/parallax-backend`:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Acceso al admin de Django:
- URL: https://api.example.com/admin/
- Si el frontend y el backend comparten dominio, configura un proxy específico para /admin/ en el servidor del frontend.

Habilitar sitio y recargar Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/parallax-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Opción B: Apache + mod_proxy_wstunnel
Requiere `mod_proxy` y `mod_proxy_wstunnel` habilitados.

```bash
sudo a2enmod proxy proxy_http proxy_wstunnel
sudo systemctl reload apache2
```

VirtualHost básico:
```apache
ProxyPreserveHost On
ProxyPass / http://127.0.0.1:8000/
ProxyPassReverse / http://127.0.0.1:8000/
ProxyPass /ws/ ws://127.0.0.1:8000/ws/
```

## Configuración de firewall y seguridad

### UFW básico
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Recomendaciones adicionales
- Habilitar HTTPS con Let’s Encrypt (certbot)
- Rotación de logs con logrotate
- Usuario dedicado sin login directo (SSH solo para admin)
- Desactivar DEBUG en producción

## Comandos de construcción y despliegue

### Build inicial
```bash
cd /opt/parallax/backend
sudo -u parallax /opt/parallax/backend/.venv/bin/python manage.py migrate
sudo -u parallax /opt/parallax/backend/.venv/bin/python manage.py check
```

### Despliegue (actualización)
```bash
cd /opt/parallax/backend
sudo -u parallax git pull
sudo -u parallax /opt/parallax/backend/.venv/bin/pip install -r requirements.txt
sudo -u parallax /opt/parallax/backend/.venv/bin/python manage.py migrate
sudo systemctl restart parallax-backend
```

## Scripts de automatización

### deploy.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
cd /opt/parallax/backend
git pull
/opt/parallax/backend/.venv/bin/pip install -r requirements.txt
/opt/parallax/backend/.venv/bin/python manage.py migrate
/opt/parallax/backend/.venv/bin/python manage.py check
systemctl restart parallax-backend
```

### rollback.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
cd /opt/parallax/backend
git fetch --all
git checkout <COMMIT_HASH>
/opt/parallax/backend/.venv/bin/pip install -r requirements.txt
/opt/parallax/backend/.venv/bin/python manage.py migrate
/opt/parallax/backend/.venv/bin/python manage.py check
systemctl restart parallax-backend
```

## Verificación y testing post-instalación
- Validar estado del servicio:
  - `systemctl status parallax-backend`
- Validar salud de Django:
  - `/opt/parallax/backend/.venv/bin/python manage.py check`
- Probar API:
  - `curl http://api.example.com/api/users/active/`
- Probar WebSocket:
  - `wscat -c ws://api.example.com/ws/admin/`

## Monitoreo y logs

### Logs del servicio
```bash
journalctl -u parallax-backend -f
```

### Métricas recomendadas
- Uso de CPU/RAM (node_exporter)
- Latencia de requests (Nginx logs)
- Conexiones WebSocket activas
- Redis memory usage
- Slow queries en PostgreSQL

## Mantenimiento y actualización
- Actualizar dependencias: `pip list --outdated`
- Backups de PostgreSQL diarios:
  - `pg_dump -U parallax parallax_backend > backup.sql`
- Rotación de logs con logrotate
- Revisar alertas y métricas semanalmente

## Troubleshooting

### 1) Error 502 en Nginx
Posible causa: Daphne no está corriendo o puerto incorrecto.
- Revisar `systemctl status parallax-admin`
- Verificar puerto 8000

### 2) WebSocket se desconecta
Posible causa: proxy mal configurado o headers Upgrade faltantes.
- Verificar configuración Nginx y `proxy_set_header Upgrade`

### 3) Error de migraciones
Posible causa: credenciales DB incorrectas.
- Validar variables de entorno y conexión a PostgreSQL

### 4) Eventos duplicados desde el plugin
Posible causa: event_id no es único o TTL muy bajo.
- Verificar generación de event_id en plugin
- Ajustar PLUGIN_EVENT_TTL_SECONDS
