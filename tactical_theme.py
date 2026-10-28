"""
MNU Tactical Command Center - Military Cyber Theme
Drop-in module for the Streamlit app.

Usage in your main file:
    from tactical_theme import inject_theme, render_hero, render_kpis, render_qr_card, render_footer
    inject_theme()
    render_hero("logo.png", lang="العربية")
"""
import base64
import mimetypes
from io import BytesIO

import qrcode
import streamlit as st
import streamlit.components.v1 as components

# ---------- Palette (matched to the logo: gold + navy + neon) ----------
CYAN = "#00F0FF"
GOLD = "#FFC400"
GREEN = "#39FF14"
RED = "#FF2E63"
VIOLET = "#B388FF"

# ---------- Names (edit here) ----------
NAMES = {
    "English": {
        "uni": "MANSOURA NATIONAL UNIVERSITY",
        "fac": "FACULTY OF ENGINEERING",
        "sub": "CYBER-TACTICAL OPERATIONS & GOVERNANCE COMMAND CENTER",
        "pres_role": "UNIVERSITY PRESIDENT",
        "pres": "Prof. Dr. Mohamed Abdel Azim",
        "dean_role": "DEAN OF THE FACULTY",
        "dean": "Prof. Dr. Mohamed El-Helwagy",
        "dev_role": "SYSTEM ARCHITECTURE & ENGINEERING",
        "dev": "Eng. Amr Dayaa",
        "dir": "ltr",
    },
    "العربية": {
        "uni": "جامعة المنصورة الأهلية",
        "fac": "كلية الهندسة",
        "sub": "مركز عمليات القيادة السيبرانية والتكتيكية",
        "pres_role": "رئيس الجامعة",
        "pres": "أ.د. محمد عبد العظيم",
        "dean_role": "عميد الكلية",
        "dean": "أ.د. محمد الحلواني",
        "dev_role": "هندسة وتطوير النظم",
        "dev": "م. عمرو دعيه",
        "dir": "rtl",
    },
}
PHONE = "01027442086"


def inject_theme():
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Cairo:wght@600;800;900&family=Share+Tech+Mono&display=swap');

:root {{
  --cyan:{CYAN}; --gold:{GOLD}; --green:{GREEN}; --red:{RED}; --violet:{VIOLET};
  --bg:#03050A; --panel:#070B14;
}}
.stApp {{
  background:
    linear-gradient(rgba(0,240,255,.035) 1px, transparent 1px) 0 0/44px 44px,
    linear-gradient(90deg, rgba(0,240,255,.035) 1px, transparent 1px) 0 0/44px 44px,
    radial-gradient(ellipse at 50% -10%, #0c1a33 0%, var(--bg) 60%);
  color:#E6F1FF; font-family:'Cairo','Orbitron',sans-serif;
}}
/* scanlines */
.stApp::after {{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:9999;
  background:repeating-linear-gradient(0deg, rgba(0,0,0,0) 0, rgba(0,0,0,0) 2px, rgba(0,240,255,.035) 3px);
}}
header[data-testid="stHeader"] {{ background:transparent; }}
h1,h2,h3 {{ font-family:'Orbitron','Cairo',sans-serif !important; color:var(--cyan) !important;
  text-shadow:0 0 14px rgba(0,240,255,.6); letter-spacing:1.5px; }}

/* ---- cut-corner frames ---- */
.cut {{ padding:2px; background:linear-gradient(135deg,var(--gold),var(--cyan) 55%,var(--gold));
  clip-path:polygon(22px 0,100% 0,100% calc(100% - 22px),calc(100% - 22px) 100%,0 100%,0 22px);
  filter:drop-shadow(0 0 18px rgba(0,240,255,.35)); }}
.cut-in {{ background:var(--panel);
  clip-path:polygon(21px 0,100% 0,100% calc(100% - 21px),calc(100% - 21px) 100%,0 100%,0 21px); }}

/* ---- hero / logo ---- */
.hero-wrap {{ margin:6px 0 22px; }}
.logo-stage {{ background:#000; padding:clamp(18px,4vw,46px); text-align:center; position:relative; }}
.logo-stage img {{ width:100%; max-height:560px; object-fit:contain;
  filter:drop-shadow(0 0 22px rgba(255,196,0,.45)) drop-shadow(0 0 40px rgba(0,240,255,.25));
  animation:breath 5s ease-in-out infinite; }}
@keyframes breath {{ 50% {{ transform:scale(1.012);
  filter:drop-shadow(0 0 30px rgba(255,196,0,.65)) drop-shadow(0 0 55px rgba(0,240,255,.4)); }} }}
.logo-stage::before, .logo-stage::after {{ content:""; position:absolute; width:46px; height:46px; border:3px solid var(--cyan);
  box-shadow:0 0 12px var(--cyan); }}
.logo-stage::before {{ top:10px; left:10px; border-right:none; border-bottom:none; }}
.logo-stage::after  {{ bottom:10px; right:10px; border-left:none; border-top:none; }}
.sweep {{ position:absolute; left:0; right:0; height:3px; top:0; background:linear-gradient(90deg,transparent,var(--cyan),transparent);
  animation:sweep 4.5s linear infinite; opacity:.7; }}
@keyframes sweep {{ to {{ top:100%; }} }}

.uni-title {{ font-family:'Orbitron','Cairo'; font-weight:900; text-align:center; color:#fff;
  font-size:clamp(22px,3.6vw,44px); letter-spacing:3px; text-shadow:0 0 18px rgba(0,240,255,.8); margin:18px 0 0; }}
.uni-sub {{ text-align:center; color:var(--cyan); font-family:'Share Tech Mono','Cairo'; letter-spacing:3px;
  font-size:clamp(11px,1.5vw,16px); margin:4px 0 20px; }}

/* ---- leadership ---- */
.lead-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-bottom:18px; }}
@media(max-width:800px){{ .lead-grid{{ grid-template-columns:1fr; }} }}
.lead {{ padding:22px 18px; text-align:center; }}
.lead .role {{ font-family:'Share Tech Mono','Cairo'; letter-spacing:4px; font-size:13px; opacity:.85; }}
.lead .nm {{ font-family:'Cairo','Orbitron'; font-weight:900; font-size:clamp(26px,4.2vw,50px); line-height:1.35; margin-top:6px; }}
.lead.pres .nm {{ color:var(--gold); text-shadow:0 0 12px rgba(255,196,0,.9),0 0 34px rgba(255,150,0,.6); }}
.lead.pres .role {{ color:var(--gold); }}
.lead.dean .nm {{ color:var(--cyan); text-shadow:0 0 12px rgba(0,240,255,.95),0 0 34px rgba(0,160,255,.6); }}
.lead.dean .role {{ color:var(--cyan); }}
.lead.dev .nm {{ color:var(--green); font-size:clamp(20px,2.6vw,32px); text-shadow:0 0 12px rgba(57,255,20,.9); }}
.lead.dev .role {{ color:var(--green); }}
.phone {{ font-family:'Share Tech Mono'; color:var(--cyan); letter-spacing:3px; font-size:16px; margin-top:4px; }}

/* ---- status + KPI ---- */
.ticker {{ font-family:'Share Tech Mono'; color:var(--green); font-size:13px; letter-spacing:2px;
  border:1px solid rgba(57,255,20,.35); background:rgba(57,255,20,.05); padding:8px 14px; margin-bottom:18px; overflow:hidden; white-space:nowrap; }}
.ticker span {{ display:inline-block; padding-left:100%; animation:tick 28s linear infinite; }}
@keyframes tick {{ to {{ transform:translateX(-100%); }} }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin:8px 0 22px; }}
@media(max-width:1000px){{ .kpi-grid{{ grid-template-columns:repeat(2,1fr); }} }}
.kpi {{ padding:16px 12px; text-align:center; }}
.kpi .ic {{ font-size:28px; }}
.kpi .v {{ font-family:'Orbitron'; font-weight:900; font-size:34px; margin:2px 0; }}
.kpi .l {{ font-size:13px; letter-spacing:1px; opacity:.9; }}
.dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--green); box-shadow:0 0 8px var(--green);
  margin-inline-end:6px; animation:blink 1.4s infinite; }}
@keyframes blink {{ 50% {{ opacity:.25; }} }}

/* ---- QR card ---- */
.qr-card {{ padding:16px; text-align:center; }}
.qr-card img {{ width:100%; max-width:230px; border-radius:6px; background:#fff; padding:8px; }}
.qr-card .t {{ font-weight:800; margin-top:10px; font-size:16px; }}

/* ---- sidebar / widgets ---- */
[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#050912,#02040A); border-right:1px solid rgba(0,240,255,.35);
  box-shadow:0 0 25px rgba(0,240,255,.15); }}
[data-testid="stSidebar"] * {{ font-family:'Cairo',sans-serif; }}
.stTextInput input, .stTextArea textarea, .stNumberInput input, [data-baseweb="select"] > div {{
  background:#050A14 !important; border:1px solid rgba(0,240,255,.4) !important; color:#E6F1FF !important; border-radius:2px !important; }}
.stTextInput input:focus, .stTextArea textarea:focus {{ border-color:var(--gold) !important; box-shadow:0 0 12px rgba(255,196,0,.5) !important; }}
label, .stMarkdown p {{ color:#CFE9FF; }}
.stButton > button {{ background:linear-gradient(135deg,rgba(255,196,0,.15),rgba(0,240,255,.15)); color:var(--gold);
  border:1px solid var(--gold); border-radius:0; font-family:'Orbitron','Cairo'; font-weight:700; letter-spacing:2px;
  clip-path:polygon(12px 0,100% 0,100% calc(100% - 12px),calc(100% - 12px) 100%,0 100%,0 12px); transition:.2s; }}
.stButton > button:hover {{ background:var(--gold); color:#000; box-shadow:0 0 22px var(--gold); }}
hr {{ border-color:rgba(0,240,255,.25); }}
.footer-t {{ display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px; margin-top:50px; padding-top:16px;
  border-top:1px solid rgba(0,240,255,.3); color:#6B86A8; font-family:'Share Tech Mono'; font-size:12px; letter-spacing:2px; }}
</style>
""",
        unsafe_allow_html=True,
    )


def _img_b64(path_or_bytes):
    if isinstance(path_or_bytes, (bytes, bytearray)):
        return "image/png", base64.b64encode(path_or_bytes).decode()
    mime = mimetypes.guess_type(path_or_bytes)[0] or "image/png"
    with open(path_or_bytes, "rb") as f:
        return mime, base64.b64encode(f.read()).decode()


def render_clock(height=64):
    """Live tactical clock (needs an iframe so JS can run)."""
    components.html(
        f"""
<div id="c" style="font-family:'Share Tech Mono',monospace;color:{CYAN};text-align:center;letter-spacing:4px;
 font-size:22px;border:1px solid {CYAN}66;background:#030712;padding:10px;text-shadow:0 0 10px {CYAN};
 box-shadow:inset 0 0 14px {CYAN}33;">--</div>
<script>
function t(){{const d=new Date();const p=n=>String(n).padStart(2,'0');
document.getElementById('c').innerText='TACTICAL CLOCK  '+p(d.getDate())+'-'+p(d.getMonth()+1)+'-'+d.getFullYear()+'  |  '+p(d.getHours())+':'+p(d.getMinutes())+':'+p(d.getSeconds());}}
t();setInterval(t,1000);
</script>""",
        height=height,
    )


def render_hero(logo_path, lang="English"):
    n = NAMES[lang]
    mime, b64 = _img_b64(logo_path)
    st.markdown(
        f"""
<div class="hero-wrap" dir="{n['dir']}">
  <div class="cut"><div class="cut-in">
    <div class="logo-stage"><div class="sweep"></div>
      <img src="data:{mime};base64,{b64}" alt="MNU logo"/>
    </div>
  </div></div>
  <div class="uni-title">{n['uni']} &mdash; {n['fac']}</div>
  <div class="uni-sub">{n['sub']}</div>
  <div class="lead-grid">
    <div class="cut"><div class="cut-in lead pres"><div class="role">&#9670; {n['pres_role']} &#9670;</div><div class="nm">{n['pres']}</div></div></div>
    <div class="cut"><div class="cut-in lead dean"><div class="role">&#9670; {n['dean_role']} &#9670;</div><div class="nm">{n['dean']}</div></div></div>
  </div>
  <div class="cut"><div class="cut-in lead dev">
    <div class="role">&#9670; {n['dev_role']} &#9670;</div><div class="nm">{n['dev']}</div><div class="phone">&#9742; {PHONE}</div>
  </div></div>
</div>
""",
        unsafe_allow_html=True,
    )
    render_clock()
    st.markdown(
        '<div class="ticker"><span>&#9608; SYSTEM STATUS: ONLINE &nbsp;&bull;&nbsp; GPS GEOFENCE: ACTIVE '
        '&nbsp;&bull;&nbsp; ENCRYPTION: ENABLED &nbsp;&bull;&nbsp; 5 PORTALS: OPERATIONAL '
        '&nbsp;&bull;&nbsp; THREAT LEVEL: LOW &nbsp;&bull;&nbsp; MNU TACTICAL COMMAND V10.4</span></div>',
        unsafe_allow_html=True,
    )


def render_kpis(stats=None, lang="English"):
    """stats: dict of counts, e.g. {'staff':12,'student':340,'ta':25,'tech':18,'gov':7}"""
    s = {"staff": 0, "student": 0, "ta": 0, "tech": 0, "gov": 0}
    s.update(stats or {})
    ar = lang == "العربية"
    items = [
        ("💼", "تذاكر الصيانة" if ar else "MAINTENANCE", s["staff"], CYAN),
        ("🎓", "حضور الطلاب" if ar else "STUDENTS", s["student"], GOLD),
        ("👨‍🏫", "متابعة المعيدين" if ar else "TEACHING ASST.", s["ta"], GREEN),
        ("🛠️", "فحص القاعات" if ar else "HALL INSPECTION", s["tech"], VIOLET),
        ("💡", "الحوكمة والمقترحات" if ar else "GOVERNANCE", s["gov"], RED),
    ]
    cards = "".join(
        f'<div class="cut" style="background:linear-gradient(135deg,{c},transparent 70%)"><div class="cut-in kpi">'
        f'<div class="ic">{ic}</div><div class="v" style="color:{c};text-shadow:0 0 14px {c}">{v}</div>'
        f'<div class="l"><span class="dot"></span>{lb}</div></div></div>'
        for ic, lb, v, c in items
    )
    st.markdown(f'<div class="kpi-grid">{cards}</div>', unsafe_allow_html=True)


def make_qr(url: str) -> bytes:
    """High-contrast QR (dark on white) so it scans reliably from print or screen."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#02040A", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def render_qr_card(title: str, url: str, color: str = CYAN):
    _, b64 = _img_b64(make_qr(url))
    st.markdown(
        f'<div class="cut" style="background:linear-gradient(135deg,{color},transparent 75%)"><div class="cut-in qr-card">'
        f'<img src="data:image/png;base64,{b64}"/><div class="t" style="color:{color};text-shadow:0 0 10px {color}">{title}</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )


def render_footer(lang="English"):
    n = NAMES[lang]
    st.markdown(
        f'<div class="footer-t"><span>&#9889; MNU FACULTY OF ENGINEERING &mdash; TACTICAL COMMAND SYSTEM V10.4</span>'
        f'<span style="color:{GREEN}">{n["dev_role"]}: {n["dev"]} &nbsp;|&nbsp; {PHONE}</span></div>',
        unsafe_allow_html=True,
    )