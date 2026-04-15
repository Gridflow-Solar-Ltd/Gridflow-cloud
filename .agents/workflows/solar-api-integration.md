---
description: Workflow for integrating Deye Cloud and Solarman APIs into the Django backend
---

# Solar API Integration Workflow

## Prerequisites
- Python 3.11+ and pip
- PostgreSQL 15+ installed and running
- Redis installed and running
- Deye Cloud developer account with AppID + AppSecret
- Solarman developer account with APP_ID + APP_SECRET
- Access token obtained from both platforms

## Phase 1: Infrastructure Setup

### 1. Install PostgreSQL and create database
```bash
createdb gridflow
```

### 2. Install Redis (if not already installed)
```bash
# Windows: use WSL or download from https://github.com/microsoftarchive/redis/releases
# Or use Docker:
docker run -d --name gridflow-redis -p 6379:6379 redis:7-alpine
```

### 3. Create `.env` file in backend/
```bash
cd backend
cp .env.example .env
# Fill in DATABASE_URL, REDIS_URL, DEYE_BASE_URL, SOLARMAN_BASE_URL, FIELD_ENCRYPTION_KEY
```

### 4. Install new Python dependencies
// turbo
```bash
cd backend && pip install psycopg2-binary django-environ celery[redis] django-celery-beat redis requests django-encrypted-model-fields
```

### 5. Update requirements.txt
// turbo
```bash
cd backend && pip freeze > requirements.txt
```

## Phase 2: Database Migration

### 6. Update settings.py
- Switch DATABASES from SQLite to PostgreSQL using django-environ
- Add 'integrations' and 'django_celery_beat' to INSTALLED_APPS
- Add Celery configuration
- Add Redis cache configuration
- Add provider default URLs

### 7. Create the integrations app
// turbo
```bash
cd backend && python manage.py startapp integrations
```

### 8. Implement models
- Create `ProviderCredential` in `integrations/models.py`
- Expand `Device` model with `data_source`, `provider_credential`, `provider_device_id`, `provider_station_id`, `last_synced_at`
- Expand `Telemetry` model with all new fields (see implementation plan)
- Create `DeviceAlert` model in `telemetry/models.py`

### 9. Run migrations
```bash
cd backend && python manage.py makemigrations && python manage.py migrate
```

## Phase 3: Provider Client Implementation

### 10. Create the provider abstraction layer
Create the following files:
- `integrations/clients/__init__.py` — ProviderManager factory
- `integrations/clients/base.py` — Abstract BaseProviderClient
- `integrations/normalizers.py` — NormalizedTelemetry dataclass

### 11. Implement Deye Cloud client
Create `integrations/clients/deye.py`:
- Auth: `POST /v1.0/account/token?appId=<appId>` — body: `{appSecret, email, password(SHA256)}`
- Station list: `POST /v1.0/station/list` — body: `{page, size}`
- Device list: `POST /v1.0/device/list` — body: `{page, size}`
- Device latest: `POST /v1.0/device/latest` — body: `{deviceList: [sn1, sn2, ...]}`
- Device history: `POST /v1.0/device/history` — body: `{deviceSn, granularity, startAt, endAt, measurePoints}`
- Headers: `Content-Type: application/json`, `Authorization: bearer <token>`
- Region-aware base URL (eu1/us1/india)

### 12. Refactor Solarman client
Move `telemetry/solarman_client.py` → `integrations/clients/solarman.py`:
- Implement BaseProviderClient interface
- Keep HMAC signature logic
- Add historical data and alerts methods
- Auth: `POST /account/v1.0/token`
- Realtime: `POST /device/v1.0/currentData`
- Historical: `POST /device/v1.0/historical`
- Alerts: `POST /station/v1.0/alert`

## Phase 4: Celery Background Tasks

### 13. Configure Celery
Create `gridflow_cloud_backend/celery.py`:
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gridflow_cloud_backend.settings')
app = Celery('gridflow_cloud_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 14. Implement tasks
Create `integrations/tasks.py`:
- `sync_all_devices` — periodic (every 5 min), iterates all active credentials
- `sync_single_device(device_id)` — on-demand
- `backfill_device_history(device_id, start_date, end_date)` — historical pull
- `sync_alerts(credential_id)` — alarm sync

### 15. Start Celery workers
```bash
cd backend && celery -A gridflow_cloud_backend worker --loglevel=info
```

```bash
cd backend && celery -A gridflow_cloud_backend beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Phase 5: API Endpoints

### 16. Create integration API endpoints
- `integrations/serializers.py` — ProviderCredential serializer (mask secrets on read)
- `integrations/views.py` — CRUD for credentials, manual sync trigger, device discovery
- `integrations/urls.py` — URL routing

### 17. Update telemetry endpoints
- Refactor `TelemetrySyncFromSolarmanView` → provider-agnostic `TelemetrySyncView`
- Add `TelemetryHistoryView` with date range filtering
- Add `DeviceAlertListView`
- Update `telemetry/urls.py`

### 18. Wire URLs
Add to `gridflow_cloud_backend/urls.py`:
```python
path('api/integrations/', include('integrations.urls')),
```

## Phase 6: Verification

### 19. Run tests
```bash
cd backend && python manage.py test integrations telemetry devices
```

### 20. Manual smoke test
```bash
# Create provider credential
curl -X POST http://localhost:8000/api/integrations/credentials/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"provider": "DEYE", "app_id": "...", "app_secret": "..."}'

# Trigger sync
curl -X POST http://localhost:8000/api/devices/1/telemetry/sync/ \
  -H "Authorization: Bearer <token>"

# Check telemetry
curl http://localhost:8000/api/devices/1/telemetry/ \
  -H "Authorization: Bearer <token>"
```

### 21. Verify background sync
```bash
# Check Celery logs for successful periodic syncs
# Verify TelemetryReading records are being created in DB
cd backend && python manage.py shell -c "from telemetry.models import TelemetryReading; print(TelemetryReading.objects.count())"
```
