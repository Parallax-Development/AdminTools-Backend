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

## Variables de entorno
Crear archivo `.env` en `/opt/parallax-admin/.env`:

```
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=example.com,api.example.com
USE_POSTGRES=true
POSTGRES_DB=parallax_admin
POSTGRES_USER=parallax
POSTGRES_PASSWORD=strong-password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
PLUGIN_SHARED_SECRETS={"api-key-1":"shared-secret-1"}
PLUGIN_ALLOWED_DRIFT_SECONDS=60
PLUGIN_EVENT_TTL_SECONDS=300
```

## Instalación paso a paso

### 1) Crear usuario del sistema
> Puedes usar cualquier nombre de usuario, se usará `parallax` en ésta guía.

```
sudo adduser --disabled-password --gecos "" parallax
sudo usermod -aG sudo parallax
```

### 2) Instalar dependencias base
```
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential \
    postgresql postgresql-contrib redis-server nginx git
```

### 3) Crear directorio de despliegue
```
sudo mkdir -p /opt/parallax-admin
sudo chown -R parallax:parallax /opt/parallax-admin
```

### 4) Clonar el proyecto
```
sudo -u parallax git clone https://github.com/DarkBladeDev/Parallax-AdminTools.git /opt/parallax-admin
```

### 5) Crear entorno virtual e instalar dependencias
```
sudo -u parallax python3 -m venv /opt/parallax-admin/.venv
sudo -u parallax /opt/parallax-admin/.venv/bin/pip install -U pip
sudo -u parallax /opt/parallax-admin/.venv/bin/pip install -r /opt/parallax-admin/requirements.txt
```

## Configuración de base de datos

### PostgreSQL (producción)
> Cambia `parallax_admin`, `parallax` y `strong-password` por tus propios valores.

```
sudo -u postgres psql
CREATE DATABASE parallax_admin;
CREATE USER parallax WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE parallax_admin TO parallax;
\q
```

### Migraciones
```
cd /opt/parallax-admin
sudo -u parallax /opt/parallax-admin/.venv/bin/python manage.py migrate
```

## Configuración de servicios web

### Opción A: Nginx + Daphne (recomendado)

#### Servicio systemd para Daphne
Crear `/etc/systemd/system/parallax-admin.service`:

```
[Unit]
Description=Parallax Admin ASGI
After=network.target

[Service]
User=parallax
Group=parallax
WorkingDirectory=/opt/parallax-admin
EnvironmentFile=/opt/parallax-admin/.env
ExecStart=/opt/parallax-admin/.venv/bin/daphne -b 127.0.0.1 -p 8000 parallax_admin.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activar y arrancar:
```
sudo systemctl daemon-reload
sudo systemctl enable parallax-admin
sudo systemctl start parallax-admin
```

#### Nginx reverse proxy
Crear `/etc/nginx/sites-available/parallax-admin`:

```
server {
    listen 80;
    server_name example.com;

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

Habilitar sitio:
```
sudo ln -s /etc/nginx/sites-available/parallax-admin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Opción B: Apache + mod_proxy_wstunnel
Requiere `mod_proxy` y `mod_proxy_wstunnel` habilitados.

```
sudo a2enmod proxy proxy_http proxy_wstunnel
sudo systemctl reload apache2
```

VirtualHost básico:
```
ProxyPreserveHost On
ProxyPass / http://127.0.0.1:8000/
ProxyPassReverse / http://127.0.0.1:8000/
ProxyPass /ws/ ws://127.0.0.1:8000/ws/
```

## Configuración de firewall y seguridad

### UFW básico
```
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
```
cd /opt/parallax-admin
sudo -u parallax /opt/parallax-admin/.venv/bin/python manage.py migrate
sudo -u parallax /opt/parallax-admin/.venv/bin/python manage.py check
```

### Despliegue (actualización)
```
cd /opt/parallax-admin
sudo -u parallax git pull
sudo -u parallax /opt/parallax-admin/.venv/bin/pip install -r requirements.txt
sudo -u parallax /opt/parallax-admin/.venv/bin/python manage.py migrate
sudo systemctl restart parallax-admin
```

## Scripts de automatización

### deploy.sh
```
#!/usr/bin/env bash
set -euo pipefail
cd /opt/parallax-admin
git pull
/opt/parallax-admin/.venv/bin/pip install -r requirements.txt
/opt/parallax-admin/.venv/bin/python manage.py migrate
/opt/parallax-admin/.venv/bin/python manage.py check
systemctl restart parallax-admin
```

### rollback.sh
```
#!/usr/bin/env bash
set -euo pipefail
cd /opt/parallax-admin
git fetch --all
git checkout <COMMIT_HASH>
/opt/parallax-admin/.venv/bin/pip install -r requirements.txt
/opt/parallax-admin/.venv/bin/python manage.py migrate
systemctl restart parallax-admin
```

## Verificación y testing post-instalación
- Validar estado del servicio:
  - `systemctl status parallax-admin`
- Validar salud de Django:
  - `/opt/parallax-admin/.venv/bin/python manage.py check`
- Probar API:
  - `curl http://example.com/api/users/active/`
- Probar WebSocket:
  - `wscat -c ws://example.com/ws/admin/`

## Monitoreo y logs

### Logs del servicio
```
journalctl -u parallax-admin -f
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
  - `pg_dump -U parallax parallax_admin > backup.sql`
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
