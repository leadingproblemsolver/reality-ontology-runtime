from __future__ import annotations

import json
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .nextmove import NextMoveEngine
from .store import RealityStore


def _json(handler: BaseHTTPRequestHandler, status: int, payload: Any) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0 or length > 1_000_000:
        raise ValueError("request body must be 1..1,000,000 bytes")
    raw = handler.rfile.read(length)
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON body must be an object")
    return value


def render_next_page(view: dict[str, Any] | None) -> bytes:
    if not view:
        content = """
        <section class='empty'>
          <p class='eyebrow'>NO ACTIVE TRANSITION</p>
          <h1>Load one mission, then execute only what changes reality.</h1>
          <p>Use <code>ro next-start --spec examples/next_market.json</code> or POST a mission to <code>/api/mission</code>.</p>
        </section>
        """
        data = "null"
    else:
        def h(key: str) -> str:
            return escape(str(view[key]))
        timer = view["timer"]
        content = f"""
        <section class='hero'>
          <div class='topline'><span class='status'>{escape(view['status'])}</span><span id='clock'>{timer['remaining_seconds'] // 60:02d}:{timer['remaining_seconds'] % 60:02d}</span></div>
          <p class='eyebrow'>TARGET</p><h1>{h('target')}</h1>
          <div class='grid'>
            <div><p class='eyebrow'>NOW</p><p>{h('now')}</p></div>
            <div><p class='eyebrow'>DELTA</p><p>{h('delta')}</p></div>
          </div>
          <div class='next'><p class='eyebrow'>NEXT MOVE</p><h2>{h('next_move')}</h2></div>
          <div class='grid'>
            <div><p class='eyebrow'>EXPECT</p><p>{h('expected_postcondition')}</p></div>
            <div><p class='eyebrow'>RECEIPT</p><p>{h('expected_receipt')}</p></div>
          </div>
          <div class='meter'><span>Urgency</span><strong>{view['urgency']}</strong></div>
          <p class='nudge' id='nudge'>{escape(view['nudge'])}</p>
        </section>
        <section class='settle'>
          <h3>Settle this transition</h3>
          <textarea id='observation' placeholder='What actually happened?'></textarea>
          <input id='receipt' placeholder='Receipt URL/path (required for receipt, capability gain, or falsification)'>
          <input id='nextAction' placeholder='Next action, only if already known'>
          <div class='actions'>
            <button data-outcome='RECEIPT'>Receipt</button>
            <button data-outcome='CAPABILITY_GAIN'>Capability gain</button>
            <button data-outcome='FALSIFIED_HYPOTHESIS'>Assumption died</button>
            <button data-outcome='BLOCKED'>Blocked</button>
            <button data-outcome='EXPLICIT_KILL'>Kill</button>
          </div>
          <pre id='result' aria-live='polite'></pre>
        </section>
        """
        data = json.dumps(view).replace("</", "<\\/")

    html = f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Logistinfra /next</title>
<style>
:root{{--bg:#0b0d10;--panel:#12161b;--text:#f4f7fa;--muted:#9ea8b3;--line:#2a323b;--accent:#f2c94c;--danger:#ff6b6b}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.45 ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:780px;margin:0 auto;padding:24px}} section{{border:1px solid var(--line);border-radius:18px;padding:22px;background:var(--panel);margin-bottom:16px}}
.topline{{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:24px}} .status{{font-weight:700;letter-spacing:.08em;font-size:12px;color:var(--accent)}} #clock{{font:700 28px ui-monospace,SFMono-Regular,Menlo,monospace}}
.eyebrow{{margin:0 0 6px;color:var(--muted);font-size:11px;font-weight:800;letter-spacing:.12em}} h1{{font-size:clamp(28px,5vw,44px);line-height:1.05;margin:0 0 24px}} h2{{font-size:clamp(22px,4vw,32px);margin:0}} h3{{margin-top:0}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:16px 0}} .grid>div,.next{{border-top:1px solid var(--line);padding-top:14px}} .next{{margin:26px 0;padding:20px 0;border-bottom:1px solid var(--line)}}
.meter{{display:flex;justify-content:space-between;border-top:1px solid var(--line);padding-top:14px}} .meter strong{{font-size:26px}} .nudge{{margin:14px 0 0;color:var(--accent);font-weight:700}}
textarea,input{{width:100%;background:#0e1216;color:var(--text);border:1px solid var(--line);border-radius:12px;padding:13px;margin:0 0 10px;font:inherit}} textarea{{min-height:92px;resize:vertical}}
.actions{{display:flex;flex-wrap:wrap;gap:8px}} button{{background:var(--text);color:#111;border:0;border-radius:10px;padding:11px 14px;font-weight:800;cursor:pointer}} button:last-child{{background:var(--danger)}} pre{{white-space:pre-wrap;overflow-wrap:anywhere;color:var(--muted)}} code{{color:var(--accent)}}
@media(max-width:560px){{main{{padding:12px}}section{{padding:16px}}.grid{{grid-template-columns:1fr}}button{{flex:1 1 45%}}}}
</style>
</head>
<body><main>{content}</main>
<script>
const view={data};
if(view){{
  let remaining=view.timer.remaining_seconds;
  const clock=document.getElementById('clock');
  const nudge=document.getElementById('nudge');
  const render=()=>{{const m=Math.floor(remaining/60),s=remaining%60; clock.textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0'); if(remaining===0) nudge.textContent='SETTLE REQUIRED — capture reality before doing more work.';}};
  render(); const timer=setInterval(()=>{{if(remaining>0) remaining-=1; render(); if(remaining===0) clearInterval(timer);}},1000);
  document.querySelectorAll('button[data-outcome]').forEach(btn=>btn.addEventListener('click',async()=>{{
    const body={{outcome:btn.dataset.outcome,observation:document.getElementById('observation').value,receipt_locator:document.getElementById('receipt').value,next_action:document.getElementById('nextAction').value}};
    const res=await fetch('/api/settle/{{}}'.replace('{{}}',view.mission_id),{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});
    const payload=await res.json(); document.getElementById('result').textContent=JSON.stringify(payload,null,2); if(res.ok) setTimeout(()=>location.reload(),600);
  }}));
}}
</script></body></html>"""
    return html.encode("utf-8")


def make_handler(db_path: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "LogistinfraNext/0.1"

        def _engine(self):
            store = RealityStore(db_path)
            return store, NextMoveEngine(store)

        def log_message(self, fmt, *args):
            return

        def do_GET(self):
            path = urlparse(self.path).path
            store, engine = self._engine()
            try:
                if path in ("/", "/next"):
                    try:
                        view = engine.current()
                    except KeyError:
                        view = None
                    body = render_next_page(view)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers(); self.wfile.write(body); return
                if path == "/api/next":
                    try:
                        return _json(self, 200, engine.current())
                    except KeyError:
                        return _json(self, 404, {"error": "no mission"})
                if path.startswith("/api/events/"):
                    mission_id = path.rsplit("/", 1)[-1]
                    return _json(self, 200, engine.events(mission_id))
                return _json(self, 404, {"error": "not found"})
            finally:
                store.close()

        def do_POST(self):
            path = urlparse(self.path).path
            store, engine = self._engine()
            try:
                try:
                    payload = _read_json(self)
                    if path == "/api/mission":
                        view = engine.start_mission(
                            target=str(payload.get("target", "")),
                            observed_state=str(payload.get("observed_state", "")),
                            delta=str(payload.get("delta", "")),
                            candidates=payload.get("candidates", []),
                            timebox_seconds=int(payload.get("timebox_seconds", 900)),
                            base_urgency=int(payload.get("base_urgency", 50)),
                            owner=payload.get("owner"),
                        )
                        return _json(self, 201, view)
                    if path.startswith("/api/settle/"):
                        mission_id = path.rsplit("/", 1)[-1]
                        view = engine.settle(
                            mission_id,
                            outcome=str(payload.get("outcome", "")),
                            observation=str(payload.get("observation", "")),
                            receipt_locator=payload.get("receipt_locator") or None,
                            next_action=payload.get("next_action") or None,
                        )
                        return _json(self, 200, view)
                    return _json(self, 404, {"error": "not found"})
                except (ValueError, KeyError, json.JSONDecodeError) as exc:
                    return _json(self, 400, {"error": str(exc)})
            finally:
                store.close()

    return Handler


def serve(db_path: str = ".runtime/reality.db", host: str = "127.0.0.1", port: int = 8787) -> None:
    if port < 1 or port > 65535:
        raise ValueError("port must be 1..65535")
    server = ThreadingHTTPServer((host, port), make_handler(db_path))
    print(f"Logistinfra /next → http://{host}:{port}/next")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
