# 🌐 GeoTracker

> A production-grade IP Geolocation web app — built with Python, Flask, and Folium. Track any IP on an interactive dark map. Deploy to the cloud in minutes, for free.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat&logo=flask)
![Tests](https://img.shields.io/badge/Tests-28%20passing-00f5c4?style=flat)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat)

---

## ✨ Features

- 🔍 **Lookup any IP address** — or auto-detect your own
- 🗺️ **Interactive dark map** via Folium + OpenStreetMap (CartoDB Dark Matter tiles)
- 📡 **REST API** — `/api/lookup?ip=8.8.8.8` returns JSON + embedded map HTML
- 🛡️ **Private IP protection** — rejects non-routable addresses with a helpful error
- ✅ **28 unit & integration tests** — 100% pass rate
- 🚀 **One-click free deployment** to Render

---

## 📁 Project Structure

```
geotracker/
├── app/
│   ├── __init__.py        # Package marker
│   ├── config.py          # All config via env vars
│   ├── geo_service.py     # Business logic: IP lookup, GeoResult dataclass
│   ├── map_builder.py     # Folium map → embeddable iframe HTML
│   └── routes.py          # Flask app factory + API + frontend
├── tests/
│   ├── __init__.py
│   ├── test_geo_service.py   # 21 unit tests for service layer
│   └── test_routes.py        # 7 integration tests for Flask routes
├── main.py                # Entry point
├── requirements.txt
├── Procfile               # For Render / Railway
├── render.yaml            # One-click Render deploy config
├── pytest.ini
└── .gitignore
```

---

## 🚀 Quick Start (Local)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/geotracker.git
cd geotracker
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run

```bash
python main.py
```

Open **http://localhost:5000** in your browser.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Expected output:
```
28 passed in 2.88s
```

Tests cover:
- Private/public IP detection
- Successful API lookups (mocked)
- Network error handling (ConnectionError, Timeout, HTTPError)
- Invalid/missing data edge cases
- All Flask routes (200, 400, 500 responses)
- `GeoResult` dataclass methods

---

## 🌐 API Reference

### `GET /api/lookup`

| Parameter | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| `ip`      | string | No       | IPv4/IPv6 address. Blank = your IP.  |

**Success response:**
```json
{
  "ok": true,
  "data": {
    "ip": "8.8.8.8",
    "city": "Mountain View",
    "region": "California",
    "country": "United States",
    "country_code": "US",
    "postal": "94043",
    "latitude": 37.4056,
    "longitude": -122.0775,
    "timezone": "America/Los_Angeles",
    "org": "AS15169 Google LLC",
    "asn": "AS15169"
  },
  "map_html": "<iframe ...></iframe>"
}
```

**Error response (400):**
```json
{
  "ok": false,
  "error": "'192.168.1.1' is a private/local IP address — not routable on the internet."
}
```

### `GET /health`

```json
{ "status": "ok", "version": "1.0.0" }
```

---

## ☁️ Free Deployment on Render

**Render** gives you a free always-on web service. No credit card needed.

### Steps:

1. **Push to GitHub**
   ```bash
   git init && git add . && git commit -m "initial commit"
   gh repo create geotracker --public --push
   ```

2. **Go to [render.com](https://render.com)** → New → Web Service

3. **Connect your GitHub repo**

4. Render auto-detects `render.yaml` and fills everything in

5. Click **Deploy** — your app goes live at `https://geotracker.onrender.com`

> 💡 The `render.yaml` in this repo pre-configures runtime, build command, start command, and auto-generates a `SECRET_KEY`.

### Alternative: Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

---
<img width="1600" height="794" alt="image" src="https://github.com/user-attachments/assets/7fec8fcb-12fa-4567-b00d-2340086cc1c1" />


## ⚙️ Environment Variables

| Variable          | Default              | Description                          |
|-------------------|----------------------|--------------------------------------|
| `PORT`            | `5000`               | Port the server listens on           |
| `DEBUG`           | `false`              | Enable Flask debug mode              |
| `SECRET_KEY`      | `dev-secret-...`     | Flask secret key (change in prod!)   |
| `REQUEST_TIMEOUT` | `10`                 | Seconds before IP lookup times out   |

---

## 🛠️ Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.10+, Flask 3.0             |
| Geo API    | [ipapi.co](https://ipapi.co) (free) |
| Maps       | Folium + OpenStreetMap (CartoDB)    |
| Server     | Gunicorn                            |
| Testing    | pytest + unittest.mock              |
| Deployment | Render / Railway                    |

---

## 📜 License

MIT — do whatever you want with it.
