# Solar Remote Monitoring Platform

A human‑centered, AI‑assisted remote monitoring and billing platform for solar PV systems — designed for **households, SMEs, and C&I customers**.  
The platform integrates **real‑time inverter telemetry**, **PAYGo payments**, and **PPA monthly billing**, similar in concept to Deye Cloud.

---

## 🚀 Features (MVP)

- ✅ Real‑time solar inverter telemetry
- ✅ Device online/offline monitoring
- ✅ Energy generation & consumption dashboards
- ✅ PAYGo billing for households & SMEs
- ✅ Monthly PPA billing & invoicing for C&I customers
- ✅ Role‑based authentication (Household, SME, C&I)
- ✅ Web + Mobile support

---

## 🏗️ Architecture Overview

Inverter → Data Logger → MQTT / HTTP ↓ Django Backend (Telemetry, Billing, Auth) ↓ REST / WebSockets / APIs ↓ React Web  +  Mobile App

---

## 🧰 Tech Stack

### Backend
- Django
- Django Rest Framework (DRF)
- PostgreSQL
- Redis + Celery (background jobs)
- MQTT (Mosquitto / EMQX)

### Frontend (Web)
- React (TypeScript)
- Charting (Recharts / Chart.js)

### Mobile
- React Native (recommended for shared logic)
- Expo (fast prototyping)

### DevOps
- Docker
- CI/CD (GitHub Actions)
- Cloud deployment (Render / Fly.io / Vercel)

---

## 📁 Repository Structure (Monorepo)


solar-platform/ ├── backend/          # Django backend ├── frontend-web/     # React web app ├── frontend-mobile/  # React Native mobile app ├── infra/            # Docker, CI/CD, IaC ├── README.md └── LICENSE

---

## 🔑 Core KPIs

1. **Live telemetry latency < 10 seconds**
2. Device uptime (% reporting time)
3. Payment success rate
4. Revenue collected vs billed
5. Customer downtime incidents

---

## 🧑‍🤝‍🧑 Collaboration Workflow

- Feature‑based branches
- Shared API contract (OpenAPI/Swagger)
- Weekly backend ↔ frontend sync
- Automated linting & tests via CI

Recommended setup:
- ✅ **GitHub Organization**
- ✅ Protected `main` branch
- ✅ Pull request reviews

---

## 🛠️ Getting Started (Local)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

Frontend (Web)
cd frontend-web
npm install
npm run dev
