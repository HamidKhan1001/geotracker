"""
Flask application factory + routes.
"""

import logging
from flask import Flask, jsonify, request, render_template_string
from app.config import Config
from app.geo_service import lookup, GeoServiceError
from app.map_builder import build_map_html

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__, static_folder="../static")
    app.secret_key = Config.SECRET_KEY

    # ── Health check ────────────────────────────────────────────────────────
    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "version": Config.VERSION})

    # ── REST API ─────────────────────────────────────────────────────────────
    @app.get("/api/lookup")
    def api_lookup():
        """
        GET /api/lookup?ip=8.8.8.8
        Returns JSON with all geo fields + inline map HTML.
        """
        ip = request.args.get("ip", "").strip() or None
        try:
            result = lookup(ip)
            map_html = build_map_html(result)
            return jsonify({"ok": True, "data": result.to_dict(), "map_html": map_html})
        except GeoServiceError as e:
            logger.warning("Lookup failed: %s", e)
            return jsonify({"ok": False, "error": str(e)}), 400
        except Exception as e:
            logger.exception("Unexpected error")
            return jsonify({"ok": False, "error": "Internal server error"}), 500

    # ── Frontend ─────────────────────────────────────────────────────────────
    @app.get("/")
    def index():
        return render_template_string(FRONTEND_HTML)

    return app


# ── Embedded Frontend ────────────────────────────────────────────────────────
FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>GeoTracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{--bg:#060a0f;--surface:#0d1420;--panel:#111827;--accent:#00f5c4;--accent2:#0ea5e9;--text:#e2e8f0;--muted:#64748b;--border:rgba(0,245,196,0.15);--glow:0 0 30px rgba(0,245,196,0.15);}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Syne',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;}
body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,245,196,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,245,196,0.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}
.wrap{position:relative;z-index:1;max-width:1100px;margin:0 auto;padding:28px 20px;}
header{display:flex;align-items:center;justify-content:space-between;margin-bottom:32px;padding-bottom:20px;border-bottom:1px solid var(--border);}
.logo{font-size:24px;font-weight:800;letter-spacing:-1px;}.logo span{color:var(--accent);}
.badge{background:rgba(0,245,196,0.08);border:1px solid var(--border);border-radius:100px;padding:7px 15px;font-family:'Space Mono',monospace;font-size:11px;color:var(--accent);display:flex;align-items:center;gap:8px;}
.dot{width:7px;height:7px;background:var(--accent);border-radius:50%;animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.search-box{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:28px;margin-bottom:22px;box-shadow:var(--glow);}
.label{font-size:11px;letter-spacing:2px;color:var(--muted);font-family:'Space Mono',monospace;margin-bottom:12px;}
.row{display:flex;gap:10px;flex-wrap:wrap;}
input{flex:1;min-width:180px;background:var(--panel);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:13px 16px;color:var(--text);font-family:'Space Mono',monospace;font-size:14px;outline:none;transition:border-color .2s;}
input:focus{border-color:var(--accent);}
input::placeholder{color:var(--muted);}
.btn{padding:13px 24px;border-radius:10px;font-family:'Syne',sans-serif;font-weight:700;font-size:13px;cursor:pointer;border:none;transition:all .2s;letter-spacing:.5px;}
.btn-g{background:var(--accent);color:#000;box-shadow:0 0 20px rgba(0,245,196,0.25);}
.btn-g:hover{transform:translateY(-1px);box-shadow:0 4px 25px rgba(0,245,196,0.4);}
.btn-b{background:transparent;color:var(--accent2);border:1px solid rgba(14,165,233,0.3);}
.btn-b:hover{background:rgba(14,165,233,0.07);}
.btn:disabled{opacity:.45;cursor:not-allowed;transform:none!important;}
.grid{display:grid;grid-template-columns:340px 1fr;gap:18px;}
@media(max-width:780px){.grid{grid-template-columns:1fr;}}
.panel{display:flex;flex-direction:column;gap:14px;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px;transition:border-color .3s;}
.card:hover{border-color:rgba(0,245,196,0.3);}
.ctitle{font-size:10px;letter-spacing:2px;color:var(--muted);font-family:'Space Mono',monospace;margin-bottom:14px;display:flex;align-items:center;gap:7px;}
.ctitle::before{content:'';display:block;width:3px;height:11px;background:var(--accent);border-radius:2px;}
.irow{display:flex;justify-content:space-between;align-items:flex-start;padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.04);}
.irow:last-child{border-bottom:none;padding-bottom:0;}
.ik{font-size:11px;color:var(--muted);font-family:'Space Mono',monospace;flex-shrink:0;margin-right:10px;}
.iv{font-size:13px;font-weight:600;text-align:right;word-break:break-all;}
.iv.g{color:var(--accent);}
.iv.b{color:var(--accent2);}
.coords{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px;}
.cbox{background:var(--panel);border-radius:10px;padding:14px;text-align:center;}
.clabel{font-size:10px;letter-spacing:1.5px;color:var(--muted);font-family:'Space Mono',monospace;text-transform:uppercase;margin-bottom:5px;}
.cval{font-family:'Space Mono',monospace;font-size:15px;color:var(--accent);font-weight:700;}
.map-wrap{border-radius:16px;overflow:hidden;border:1px solid var(--border);box-shadow:var(--glow);min-height:480px;display:flex;align-items:center;justify-content:center;background:var(--surface);}
.map-wrap iframe{width:100%;height:480px;border:none;display:block;}
.empty{text-align:center;color:var(--muted);font-family:'Space Mono',monospace;font-size:12px;line-height:2;padding:40px;}
.empty-icon{font-size:44px;display:block;margin-bottom:12px;opacity:.35;}
.err{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:10px;padding:11px 16px;color:#fca5a5;font-family:'Space Mono',monospace;font-size:12px;margin-top:10px;display:none;}
.spin{width:36px;height:36px;border:3px solid rgba(0,245,196,.1);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite;margin:0 auto 12px;}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-msg{color:var(--muted);font-family:'Space Mono',monospace;font-size:12px;text-align:center;}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">Geo<span>Tracker</span></div>
    <div class="badge"><div class="dot"></div>LIVE TRACKING</div>
  </header>

  <div class="search-box">
    <div class="label">// ENTER IP ADDRESS TO LOCATE</div>
    <div class="row">
      <input id="ipIn" type="text" placeholder="e.g. 8.8.8.8  —  leave blank for your own IP" maxlength="45"/>
      <button class="btn btn-g" id="trackBtn" onclick="track()">⚡ Track IP</button>
      <button class="btn btn-b" onclick="trackMine()">📍 My IP</button>
    </div>
    <div class="err" id="err"></div>
  </div>

  <div class="grid">
    <div class="panel">
      <div class="card">
        <div class="ctitle">IP INFORMATION</div>
        <div class="irow"><span class="ik">IP</span><span class="iv g" id="f-ip">—</span></div>
        <div class="irow"><span class="ik">ISP</span><span class="iv" id="f-org">—</span></div>
        <div class="irow"><span class="ik">ASN</span><span class="iv" id="f-asn">—</span></div>
      </div>
      <div class="card">
        <div class="ctitle">LOCATION</div>
        <div class="irow"><span class="ik">COUNTRY</span><span class="iv" id="f-country">—</span></div>
        <div class="irow"><span class="ik">REGION</span><span class="iv" id="f-region">—</span></div>
        <div class="irow"><span class="ik">CITY</span><span class="iv" id="f-city">—</span></div>
        <div class="irow"><span class="ik">POSTAL</span><span class="iv" id="f-postal">—</span></div>
        <div class="irow"><span class="ik">TIMEZONE</span><span class="iv b" id="f-tz">—</span></div>
      </div>
      <div class="card">
        <div class="ctitle">COORDINATES</div>
        <div class="coords">
          <div class="cbox"><div class="clabel">Latitude</div><div class="cval" id="f-lat">—</div></div>
          <div class="cbox"><div class="clabel">Longitude</div><div class="cval" id="f-lon">—</div></div>
        </div>
      </div>
    </div>

    <div class="map-wrap" id="mapWrap">
      <div class="empty">
        <span class="empty-icon">🌐</span>
        Enter an IP above and hit <strong style="color:var(--accent)">Track IP</strong><br/>to see it pinned on the map
      </div>
    </div>
  </div>
</div>

<script>
function set(id,v){const el=document.getElementById(id);if(el)el.textContent=v||'—';}
function showErr(msg){const e=document.getElementById('err');e.textContent='⚠ '+msg;e.style.display='block';setTimeout(()=>e.style.display='none',6000);}
function setLoading(on){
  document.getElementById('trackBtn').disabled=on;
  if(on){document.getElementById('mapWrap').innerHTML='<div style="text-align:center;padding:40px"><div class="spin"></div><div class="loading-msg">Locating IP address...</div></div>';}
}

async function track(ip){
  const val=ip||document.getElementById('ipIn').value.trim();
  setLoading(true);
  document.getElementById('err').style.display='none';
  try{
    const res=await fetch('/api/lookup?ip='+encodeURIComponent(val));
    const json=await res.json();
    if(!json.ok)throw new Error(json.error);
    const d=json.data;
    set('f-ip',d.ip); set('f-org',d.org); set('f-asn',d.asn);
    set('f-country',d.country+' ('+d.country_code+')');
    set('f-region',d.region); set('f-city',d.city);
    set('f-postal',d.postal); set('f-tz',d.timezone);
    set('f-lat',parseFloat(d.latitude).toFixed(6));
    set('f-lon',parseFloat(d.longitude).toFixed(6));
    document.getElementById('mapWrap').innerHTML=json.map_html;
  }catch(e){showErr(e.message);}
  finally{setLoading(false);}
}

function trackMine(){document.getElementById('ipIn').value='';track('');}
document.getElementById('ipIn').addEventListener('keydown',e=>{if(e.key==='Enter')track();});
</script>
</body>
</html>"""
