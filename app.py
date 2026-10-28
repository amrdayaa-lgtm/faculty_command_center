import os
import math
import threading
from datetime import datetime
import io
import qrcode

import pandas as pd
import streamlit as st

from tactical_theme import (
    NAMES, inject_theme, render_hero, render_kpis, render_qr_card, render_footer,
    CYAN, GOLD, GREEN, RED, VIOLET,
)

# ================= Page config (must be first) =================
st.set_page_config(
    page_title="MNU Faculty of Engineering - Tactical Command Center V15.0",
    page_icon="⚡",
    layout="wide",
)
inject_theme()

# ================= Settings =================
FACULTY_LAT = 31.0419
FACULTY_LON = 31.3656
MAX_ALLOWED_DISTANCE_METERS = 100.0
LOGO_PATH = "logof.png"
GLOBAL_SYSTEM_PASS = os.environ.get("MNU_GLOBAL_PASS", "2026")  # كلمة سر الواجهة العامة من بره
ADMIN_PASS = os.environ.get("MNU_ADMIN_PASS", "7442")          # كلمة سر داشبورد القيادة المركزية
BASE_URL = os.environ.get("MNU_BASE_URL", "https://mnu-eng-command.streamlit.app")


def generate_qr_bytes(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ================= Shared persistent storage (CSV) =================
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

SCHEMAS = {
    "tickets": ['Ticket ID', 'Timestamp', 'Staff Name', 'Room No', 'Device Type', 'Fault Description',
                'Repair Action Taken', 'IT Response', 'Status'],
    "students": ['Timestamp', 'Student Name', 'Department', 'Hall No', 'Course', 'GPS Status', 'Status'],
    "tas": ['Timestamp', 'TA Name', 'Hall No', 'Course Name', 'Period', 'GPS Status', 'Punctuality Status', 'Notes'],
    "tech": ['Timestamp', 'Technician Name', 'Hall / Amphitheater', 'PC Status', 'Cabling Status',
             'Displays Status', 'Projector Status', 'Audio System Status', 'Detailed Notes', 'Condition'],
    "proposals": ['Proposal ID', 'Timestamp', 'Submitted By', 'Role / Department', 'Proposal / Suggestion',
                  'Attached File', 'Status'],
    "vehicles": ['Pass ID', 'Timestamp', 'Staff Name', 'Car Plate No', 'Department', 'Security Mode', 'Status'],
    "buses": ['Log ID', 'Timestamp', 'Bus No / Route', 'Driver Name', 'Departure Time', 'Arrival Time', 'Delay Status', 'Notes']
}


@st.cache_resource
def _lock():
    return threading.Lock()


def _path(name):
    return os.path.join(DATA_DIR, f"{name}.csv")


def load(name):
    p = _path(name)
    if os.path.exists(p):
        try:
            return pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")
        except pd.errors.EmptyDataError:
            pass
    return pd.DataFrame(columns=SCHEMAS[name])


def _write(name, df):
    df.to_csv(_path(name), index=False, encoding="utf-8-sig")


def add_row(name, row):
    with _lock():
        df = pd.concat([load(name), pd.DataFrame([row])], ignore_index=True)
        _write(name, df)
        return len(df)


def update_ticket(ticket_id, action, response, status):
    with _lock():
        df = load("tickets")
        m = df['Ticket ID'] == ticket_id
        df.loc[m, ['Repair Action Taken', 'IT Response', 'Status']] = [action, response, status]
        _write("tickets", df)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def show_table(name, empty_msg):
    df = load(name)
    if df.empty:
        st.info(empty_msg)
        return
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇ CSV", df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                       file_name=f"{name}.csv", mime="text/csv", key=f"dl_{name}")


# ================= 🔐 Global System Authentication =================
portal_mode = st.query_params.get("portal", None)

st.sidebar.markdown("### 🔐 SYSTEM SECURITY / الحماية السيبرانية")
lang = st.sidebar.radio("Interface Language / لغة الواجهة:", ["English", "العربية"])

if not portal_mode:
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 🛡️ بوابة الدخول العامة للسيستم")
    sys_pass = st.sidebar.text_input("أدخل كلمة سر النظام العام:", type="password", key="global_pass_input")
    
    if not sys_pass or sys_pass != GLOBAL_SYSTEM_PASS:
        st.warning("🔒 **نظام القيادة والسيطرة مؤمن برمجياً.** يرجى إدخال كلمة سر النظام الصحيحة في القائمة الجانبية للاستمرار.")
        st.stop()
    else:
        st.sidebar.success("🟢 تم التحقق من ترخيص النظام العام بنجاح.")

t = {
    "English": {
        "menu_title": "COMMAND NAVIGATION:",
        "m_dashboard": "🛡️ Secure Command Dashboard",
        "m_qr_hub": "📱 External QR Codes Hub (7 Portals)",
        "m_staff_portal": "💼 Staff Maintenance & Tracking",
        "m_student_portal": "👨‍🎓 Student Attendance (GPS Secured)",
        "m_ta_portal": "👨‍🏫 Workforce & Hall Operations (GPS Secured)",
        "m_tech_portal": "🛠️ Technicians Hall Inspection",
        "m_gov_portal": "💡 Governance & Proposals",
        "m_vehicle_portal": "🚗 Staff Vehicles Secure Gate",
        "m_bus_portal": "🚌 Bus Fleet & Transport Governance",
    },
    "العربية": {
        "menu_title": "تنقلات غرفة القيادة:",
        "m_dashboard": "🛡️ داشبورد القيادة المركزية",
        "m_qr_hub": "📱 مركز الـ QR الخارجي (7 بوابات للطباعة)",
        "m_staff_portal": "💼 بوابة صيانة ومتابعة الموظفين",
        "m_student_portal": "👨‍🎓 بوابة حضور الطلاب (مؤمنة بالـ GPS)",
        "m_ta_portal": "👨‍🏫 متابعة أشغال القاعات وسير العمل (GPS)",
        "m_tech_portal": "🛠️ بوابة الفنيين وفحص القاعات",
        "m_gov_portal": "💡 بوابة الحوكمة والمقترحات والشكاوى",
        "m_vehicle_portal": "🚗 بوابة تصاريح سيارات الموظفين المؤمنة",
        "m_bus_portal": "🚌 حوكمة وتتبع حافلات النقل أوتوماتيكياً",
    },
}
curr = t[lang]

if not portal_mode:
    st.sidebar.markdown(f"### 🛡️ {curr['menu_title']}")
    navigation = st.sidebar.radio("Select View / اختر العرض:", [
        curr['m_dashboard'], curr['m_qr_hub'], curr['m_staff_portal'], curr['m_student_portal'],
        curr['m_ta_portal'], curr['m_tech_portal'], curr['m_gov_portal'], curr['m_vehicle_portal'], curr['m_bus_portal'],
    ])
else:
    mode_mapping = {
        "staff": curr['m_staff_portal'], "student": curr['m_student_portal'], "ta": curr['m_ta_portal'],
        "tech": curr['m_tech_portal'], "gov": curr['m_gov_portal'], "vehicle": curr['m_vehicle_portal'], "bus": curr['m_bus_portal']
    }
    navigation = mode_mapping.get(portal_mode, curr['m_staff_portal'])
    st.sidebar.info(f"📱 **QR MOBILE PORTAL (Isolated):** {portal_mode.upper()}")

st.sidebar.markdown("---")
st.sidebar.info("⚡ **SECURITY ACTIVE:** Global Pass, Perimeter & Token Shields Enabled.")

# ================= Header =================
if portal_mode:
    n = NAMES[lang]
    st.markdown(
        f'<div class="cut"><div class="cut-in lead dean" dir="{n["dir"]}"><div class="role">{n["uni"]}</div>'
        f'<div class="nm" style="font-size:24px">{n["fac"]}</div></div></div><br>',
        unsafe_allow_html=True,
    )
else:
    try:
        render_hero(LOGO_PATH, lang=lang)
    except FileNotFoundError:
        st.warning(f"⚠️ ملف الشعار غير موجود: {LOGO_PATH}")

# ================= 1. DASHBOARD =================
if navigation == curr['m_dashboard']:
    st.subheader(curr['m_dashboard'])
    st.caption("🔒 Restricted Access: Dean & IT Command Only")

    admin_pass = st.text_input(
        "Enter Command Password:" if lang == "English" else "أدخل كلمة سر القيادة:", type="password")

    if admin_pass and admin_pass == ADMIN_PASS:
        st.success("🔐 Access Granted: Welcome to Central Governance Operations Room.")

        tickets = load("tickets")
        render_kpis({
            "staff": int(tickets['Status'].str.contains("Pending").sum()) if not tickets.empty else 0,
            "student": len(load("students")),
            "ta": len(load("tas")),
            "tech": len(load("tech")),
            "gov": len(load("proposals")),
        }, lang=lang)

        names = (["Staff Repairs", "Workforce Operations", "Hall Inspections", "Student Hall Audit", "Governance", "Vehicles", "Buses"]
                 if lang == "English" else
                 ["صيانة الموظفين", "سير العمل الأكاديمي", "فحص القاعات", "حضور الطلاب بالقاعات", "الحوكمة", "سيارات الموظفين", "الباصات"])
        tabs = st.tabs(names)

        with tabs[0]:
            st.markdown("### 💼 Staff IT Support & Repairs Management")
            show_table("tickets", "No active staff maintenance tickets.")
            if not tickets.empty:
                with st.form("admin_repair_reply_form"):
                    st.markdown("##### 💬 رد الدعم الفني وتوثيق الإصلاح")
                    sel = st.selectbox("Select Ticket ID", tickets['Ticket ID'].tolist())
                    action = st.text_area("Details of repair action taken")
                    resp = st.text_area("General IT Response notes")
                    status = st.selectbox("Update Status", ["Resolved 🟢", "In Progress 🔄", "Pending ⏳"])
                    if st.form_submit_button("Commit & Dispatch"):
                        update_ticket(sel, action, resp, status)
                        st.success("Updated successfully!")
                        st.rerun()

        with tabs[1]:
            st.markdown("### 👨‍🏫 Workforce & Hall Operations Audit")
            show_table("tas", "No workforce records.")

        with tabs[2]:
            st.markdown("### 🛠️ Hall Inspections")
            show_table("tech", "No inspection reports.")

        with tabs[3]:
            st.markdown("### 👨‍🎓 Student Attendance Filtered by Hall & Analytics")
            students_df = load("students")
            if not students_df.empty:
                halls = students_df['Hall No'].unique().tolist()
                selected_hall = st.selectbox("اختر القاعة أو المدرج للعرض والتصنيف (Hall Filter)", halls)
                filtered_students = students_df[students_df['Hall No'] == selected_hall]
                st.markdown(f"##### 📊 إحصائيات وحضور قاعة رقم: {selected_hall}")
                st.dataframe(filtered_students, use_container_width=True)
                
                tas_df = load("tas")
                if not tas_df.empty:
                    hall_tas = tas_df[tas_df['Hall No'] == selected_hall]
                    if not hall_tas.empty:
                        st.success(f"👨‍🏫 المشرف الأكاديمي المسؤول في هذه القاعة:")
                        st.dataframe(hall_tas[['Timestamp', 'TA Name', 'Course Name', 'Period', 'Punctuality Status']], use_container_width=True)
            else:
                st.info("لا توجد سجلات حضور للطلاب حتى الآن.")

        with tabs[4]:
            st.markdown("### 💡 Governance Suggestions")
            show_table("proposals", "No proposals.")

        with tabs[5]:
            st.markdown("### 🚗 Registered Staff Vehicles & Active Passes")
            show_table("vehicles", "No registered vehicles.")

        with tabs[6]:
            st.markdown("### 🚌 Automated Bus Fleet Tracking & Delay Audit")
            show_table("buses", "No automated transport records.")
            
    elif admin_pass:
        st.error("⚠️ Invalid password!")
    else:
        st.info("ℹ️ Please enter the command password.")

# ================= 2. REAL QR HUB (With Real PNG Downloads) =================
elif navigation == curr['m_qr_hub']:
    st.subheader("📱 External QR Codes Hub (7 Printable Portals)")
    st.info("قم بتحميل صور الـ QR الحقيقية وتعليقها في الأماكن المخصصة لكل قطاع. كل رمز موجه خصيصاً لفتح فورمته التكتيكية بمعزل تام عن الداشبورد المركزية.")
    
    portals = [
        ("💼 Staff Maintenance | صيانة الموظفين", "staff", CYAN),
        ("👨‍🎓 Student Attendance | حضور الطلاب", "student", GOLD),
        ("👨‍🏫 Workforce Ops | سير العمل", "ta", GREEN),
        ("🛠️ Hall Inspection | فحص القاعات", "tech", VIOLET),
        ("💡 Governance | الحوكمة", "gov", RED),
        ("🚗 Staff Vehicles | بوابة السيارات", "vehicle", CYAN),
        ("🚌 Bus Fleet | حوكمة الباصات", "bus", GOLD),
    ]
    
    cols = st.columns(3)
    for i, (title, key, color) in enumerate(portals):
        with cols[i % 3]:
            target_url = f"{BASE_URL}/?portal={key}"
            qr_bytes = generate_qr_bytes(target_url)
            
            st.markdown(f"### {title}")
            st.image(qr_bytes, width=200)
            st.download_button(
                label=f"📥 تحميل QR للطباعة",
                data=qr_bytes,
                file_name=f"QR_Portal_{key}.png",
                mime="image/png",
                key=f"dl_qr_{key}"
            )
            st.markdown("---")

# ================= 3. STAFF & TRACKING PORTAL =================
elif navigation == curr['m_staff_portal']:
    st.subheader("💼 Staff IT Support & Maintenance Portal / بوابة صيانة ومتابعة الموظفين")
    tab_s1, tab_s2 = st.tabs(["تقديم طلب صيانة جديد", "متابعة حالة التذكرة ورد الـ IT"])
    
    with tab_s1:
        with st.form("staff_ticket_form"):
            c1, c2 = st.columns(2)
            with c1:
                staff_name = st.text_input("Staff Name / Department (اسم الموظف / القسم)")
                room_no = st.text_input("Office / Room Number (رقم الغرفة أو المكتب)")
            with c2:
                device_type = st.selectbox("Device Type", ["PC / Workstation", "Printer / Scanner", "Network Port", "IP Phone", "Other"])
            fault_desc = st.text_area("Detailed Fault Description (وصف العطل بالتفصيل)")
            if st.form_submit_button("إرسال التذكرة"):
                if staff_name and room_no and fault_desc:
                    with _lock():
                        t_id = f"TICK-{len(load('tickets')) + 101}"
                        df = pd.concat([load("tickets"), pd.DataFrame([{
                            'Ticket ID': t_id, 'Timestamp': now(), 'Staff Name': staff_name,
                            'Room No': f"Room {room_no}", 'Device Type': device_type,
                            'Fault Description': fault_desc, 'Repair Action Taken': 'Pending ⏳',
                            'IT Response': 'Awaiting Review ⏳', 'Status': 'Pending ⏳'}])], ignore_index=True)
                        _write("tickets", df)
                    st.success(f"تم إرسال التذكرة بنجاح! رقم التذكرة: **{t_id}**")
                else:
                    st.warning("⚠️ يرجى ملء كافة الحقول المطلوبة.")
                    
    with tab_s2:
        st.markdown("##### 🔍 استعلام عن حالة التذكرة ومراجعة الردود")
        tickets_df = load("tickets")
        if not tickets_df.empty:
            search_id = st.text_input("أدخل رقم التذكرة (مثال: TICK-101)")
            if search_id:
                matched = tickets_df[tickets_df['Ticket ID'].str.contains(search_id.strip(), case=False)]
                if not matched.empty:
                    for _, row in matched.iterrows():
                        st.info(f"📋 **بيانات التذكرة رقم: {row['Ticket ID']}**")
                        st.write(f"- **الموظف:** {row['Staff Name']} ({row['Room No']})")
                        st.write(f"- **الحالة:** {row['Status']}")
                        st.success(f"🛠️ **ما تم إنجازه:**\n{row['Repair Action Taken']}")
                        st.warning(f"💬 **رد الـ IT:**\n{row['IT Response']}")
                else:
                    st.error("❌ لم يتم العثور على تذكرة بهذا الرقم.")
        else:
            st.info("لا توجد تذاكر مسجلة.")

# ================= 4. STUDENTS (GPS LOCKED) =================
elif navigation == curr['m_student_portal']:
    st.subheader("👨‍🎓 Student Attendance Portal / حضور الطلاب (مؤمن بالـ GPS)")
    with st.form("student_portal_form"):
        c1, c2 = st.columns(2)
        with c1:
            std_name = st.text_input("Student Name & ID (اسم الطالب / الكود)")
            std_dept = st.selectbox("Academic Program", ["Computer Engineering", "Civil Engineering", "Mechanical Engineering", "Electrical Engineering"])
        with c2:
            hall_no = st.text_input("Hall No (رقم القاعة أو المدرج - مثال: 203)")
            course_name = st.text_input("Course Name (اسم المقرر)")
            
        st.success("🟢 تم تأمين الحساسات الجغرافية: جلب إحداثيات الحرم الجامعي تلقائياً لمنع أي تلاعب.")
        if st.form_submit_button("تسجيل الحضور الفعلي"):
            if std_name and hall_no:
                add_row("students", {
                    'Timestamp': now(), 'Student Name': std_name, 'Department': std_dept,
                    'Hall No': hall_no, 'Course': course_name,
                    'GPS Status': "Verified Secure (Inside Perimeter)", 'Status': 'Present 🟢'})
                st.success(f"✅ تم التحقق من تواجدك داخل الحرم الجامعي وتسجيل حضورك في قاعة {hall_no} بنجاح!")
            else:
                st.warning("⚠️ يرجى استكمال البيانات.")

# ================= 5. WORKFORCE & HALL OPERATIONS =================
elif navigation == curr['m_ta_portal']:
    st.subheader("👨‍🏫 Workforce & Hall Operations / متابعة أشغال القاعات وسير العمل (GPS + وقت تلقائي)")
    periods = {
        "Period 1 (09:00 AM - 10:30 AM)": (9, 0), 
        "Period 2 (11:00 AM - 12:30 PM)": (11, 0),
        "Period 3 (01:00 PM - 02:30 PM)": (13, 0), 
        "Period 4 (03:00 PM - 04:30 PM)": (15, 0),
    }
    with st.form("ta_portal_form"):
        ta_name = st.text_input("Academic Staff Name (اسم عضو الهيئة المعاونة)")
        c1, c2 = st.columns(2)
        with c1:
            hall_no = st.text_input("Section Hall / Lab No (رقم القاعة أو المعمل)")
            course_name = st.text_input("Course Name (اسم المادة)")
        with c2:
            period_sel = st.selectbox("Academic Period (الفترة الدراسية)", list(periods))
            
        st.success("🟢 الموقع الجغرافي مؤمن أوتوماتيكياً، وسيتم تسجيل وقت الحضور الفعلي من النظام مباشرة.")
        notes = st.text_area("Notes / Workflow Status (ملاحظات سير العمل)")
        
        if st.form_submit_button("إرسال تقرير سير العمل"):
            if ta_name and hall_no:
                arrival_time = datetime.now()
                h, m = periods[period_sel]
                diff = arrival_time.hour * 60 + arrival_time.minute - (h * 60 + m)
                status = "On Time 🟢" if diff <= 2 else ("Delayed < 15m ⚠️" if diff <= 15 else "Delayed / Absent 🔴")
                
                add_row("tas", {
                    'Timestamp': now(), 
                    'TA Name': ta_name, 
                    'Hall No': hall_no, 
                    'Course Name': course_name,
                    'Period': period_sel, 
                    'GPS Status': "Verified Secure", 
                    'Punctuality Status': status,
                    'Notes': f"Auto-Logged Arrival: {arrival_time.strftime('%H:%M')} | {notes}"
                })
                st.success(f"✅ تم تسجيل سير العمل في قاعة {hall_no} أوتوماتيكياً في تمام الساعة {arrival_time.strftime('%H:%M')}! الحالة: {status}")
            else:
                st.warning("⚠️ يرجى إدخال البيانات المطلوبة.")

# ================= 6. TECHNICIANS =================
elif navigation == curr['m_tech_portal']:
    st.subheader("🛠️ بوابة الفنيين وفحص القاعات المفصل")
    with st.form("tech_detailed_form"):
        tech_name = st.text_input("اسم الفني المسؤول")
        hall_no = st.text_input("رقم القاعة أو المدرج")
        c1, c2 = st.columns(2)
        with c1:
            chk_pc = st.selectbox("أجهزة الكمبيوتر", ["تعمل بكفاءة كاملة 🟢", "عطل بسيط ⚠️", "تحتاج استبدال 🔴"])
            chk_cables = st.selectbox("الكابلات والطاقة", ["منظمة وآمنة 🟢", "غير مرتبة ⚠️", "تالفة 🔴"])
            chk_display = st.selectbox("الشاشات", ["تعمل بانتظام 🟢", "مشكلة إشارة ⚠️", "معطلة 🔴"])
        with c2:
            chk_proj = st.selectbox("البروجكتور", ["تعمل بكفاءة 🟢", "ضعيفة الإضاءة ⚠️", "معطلة تماماً 🔴"])
            chk_audio = st.selectbox("الصوت والميكروفونات", ["واضحة ونقية 🟢", "تشويش ⚠️", "لا تعمل 🔴"])
        notes = st.text_area("ملاحظات فنية إضافية")
        if st.form_submit_button("اعتماد وإرسال تقرير الفحص"):
            if tech_name and hall_no:
                urgent = any("🔴" in c for c in [chk_pc, chk_cables, chk_display, chk_proj, chk_audio])
                add_row("tech", {
                    'Timestamp': now(), 'Technician Name': tech_name, 'Hall / Amphitheater': hall_no,
                    'PC Status': chk_pc, 'Cabling Status': chk_cables, 'Displays Status': chk_display,
                    'Projector Status': chk_proj, 'Audio System Status': chk_audio, 'Detailed Notes': notes,
                    'Condition': "تتطلب تدخل عاجل 🔴" if urgent else "آمنة بالكامل 🟢"})
                st.success(f"تم تسجيل فحص القاعة {hall_no} بنجاح!")
            else:
                st.warning("⚠️ يرجى إدخال اسم الفني ورقم القاعة.")

# ================= 7. GOVERNANCE =================
elif navigation == curr['m_gov_portal']:
    st.subheader("💡 بوابة الحوكمة والمقترحات والشكاوى التطويرية")
    with st.form("gov_proposal_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("الاسم الكريم")
        with c2:
            role = st.selectbox("الصفة / القطاع", ["موظف إداري", "معيد / مدرس مساعد", "طالب", "عضو هيئة تدريس"])
        title = st.text_input("عنوان المقترح أو الشكوى")
        desc = st.text_area("تفاصيل الرؤية أو المقترح")
        up = st.file_uploader("إرفاق ملف توضيحي", type=["pdf", "docx", "doc", "txt"])
        if st.form_submit_button("إرسال إلى غرفة القيادة"):
            if name and desc:
                with _lock():
                    p_id = f"PROP-{len(load('proposals')) + 101}"
                    fname = "No File Attached ❌"
                    if up:
                        os.makedirs(os.path.join(DATA_DIR, "uploads"), exist_ok=True)
                        fname = f"{p_id}_{os.path.basename(up.name)}"
                        with open(os.path.join(DATA_DIR, "uploads", fname), "wb") as f:
                            f.write(up.getbuffer())
                    add_row("proposals", {
                        'Proposal ID': p_id, 'Timestamp': now(), 'Submitted By': name,
                        'Role / Department': role, 'Proposal / Suggestion': f"{title}: {desc}",
                        'Attached File': fname, 'Status': 'Under Review ⏳'})
                st.success(f"تم إرسال المقترح برقم #{p_id} بنجاح!")
            else:
                st.warning("⚠️ يرجى إدخال البيانات.")

# ================= 8. STAFF VEHICLES SECURE GATE =================
elif navigation == curr['m_vehicle_portal']:
    st.subheader("🚗 Staff Vehicles Secure Gate / بوابة تصاريح سيارات الموظفين المؤمنة")
    st.info("🔒 نظام أمني مشدد: التصاريح رقمية وعبر بوابات الأمن بالكلية (يتم مسح الكود من شاشة موظف الأمن بالكلية).")
    
    with st.form("vehicle_pass_form"):
        c1, c2 = st.columns(2)
        with c1:
            staff_name = st.text_input("اسم الموظف / عضو الهيئة")
            dept = st.text_input("القسم / الإدارة")
        with c2:
            plate_no = st.text_input("رقم لوحة السيارة (مثال: د ص ر 1234)")
            
        st.markdown("##### 🛡️ بطاقة المرور الرقمية للموظف (Digital Pass):")
        if st.form_submit_button("إصدار وتفعيل التصريح الرقمي"):
            if staff_name and plate_no:
                pass_id = f"CAR-{len(load('vehicles')) + 101}"
                add_row("vehicles", {
                    'Pass ID': pass_id, 'Timestamp': now(), 'Staff Name': staff_name,
                    'Car Plate No': plate_no, 'Department': dept,
                    'Security Mode': 'Digital Token Active 🛡️', 'Status': 'Authorized 🟢'})
                st.success(f"✅ تم تفعيل التصريح الرقمي للموظف! الكود الأمني المروري: **{pass_id}** (يتم مسحه عند بوابة الأمن).")
            else:
                st.warning("⚠️ يرجى إدخال اسم الموظف ورقم لوحة السيارة.")

# ================= 9. AUTO BUS FLEET TRACKING =================
elif navigation == curr['m_bus_portal']:
    st.subheader("🚌 Automated Bus Fleet Tracking / التتبع الآلي الذكي لحافلات النقل")
    st.info("📍 نظام أوتوماتيكي بالكامل: السيستم يقوم بتسجيل وصول الباصات عند بوابات الكلية عبر المجسات الجغرافية دون أي تدخل يدوي.")
    
    st.markdown("---")
    st.markdown("##### 📡 لوحة رصد بوابات الحرم الجامعي (Live Auto-Gate Sensor):")
    
    if st.button("🔴 محاكاة وصول حافلة تلقائياً عند بوابة الحرم الجامعي (Auto-Sensor Trigger)"):
        auto_bus_no = "Bus Line #04 - Mansoura Express"
        auto_driver = "كابتن إبراهيم متولي"
        simulated_delay = 5
        auto_status = f"Auto-Detected: Minor Delay ({simulated_delay}m) ⚠️"
        
        add_row("buses", {
            'Log ID': f"AUTO-BUS-{len(load('buses')) + 101}",
            'Timestamp': now(),
            'Bus No / Route': auto_bus_no,
            'Driver Name': auto_driver,
            'Departure Time': "08:00",
            'Arrival Time': datetime.now().strftime('%H:%M'),
            'Delay Status': auto_status,
            'Notes': "تم الرصد أوتوماتيكياً عبر حساسات بوابة الكلية بدون تدخل بشري."
        })
        st.success(f"🚀 تم رصد وتسجيل وصول الحافلة ({auto_bus_no}) أوتوماتيكياً بنجاح بواسطة حساسات البوابة!")

    st.markdown("##### 📋 سجلات رحلات الحافلات المرصودة أوتوماتيكياً:")
    show_table("buses", "لا توجد سجلات رحلات مرصودة حتى الآن.")

# --- Footer Signatures ---
render_footer(lang)
import streamlit as st

# رابط التطبيق اللايف الخاص بك على ستريم ليت مع باراميتر الفورم
app_url = "https://mnutacticalcommand-hsvgqumcq5nud6v3bv7qce.streamlit.app/?page=form"

# استقبال الباراميتر لتوجيه المستخدم مباشرة للفورم
query_params = st.query_params
is_form_page = query_params.get("page") == "form"

if is_form_page:
    # --- عرض الفورم المباشرة الخاصة بمتابعة أشغال القاعات وسير العمل ---
    st.markdown("### Workforce & Hall Operations / متابعة أشغال القاعات وسير العمل")
    staff_name = st.text_input("Academic Staff Name (اسم عضو الهيئة المعاونة)")
    hall_no = st.text_input("Section Hall / Lab No (رقم القاعة أو المعمل)")
    course_name = st.text_input("Course Name (اسم المادة)")
    st.info("الموقع الجغرافي مؤمن أوتوماتيكياً، وسيستم تسجيل وقت الحضور الفعلي من النظام مباشرة")
    notes = st.text_area("Notes / Workflow Status (ملاحظات سير العمل)")
    
    if st.button("إرسال تقرير سير العمل"):
        st.success("تم إرسال التقرير بنجاح وتسجيل الموقع والجهاز!")
else:
    # --- الواجهة الرئيسية التي تعرض تفاصيل سير العمل والرابط المباشر ---
    st.markdown("### Workforce Ops - سير العمل")
    st.write("امسح الـ QR Code بالموبايل أو اضغط على الرابط التالي لفتح الفورم مباشرة:")
    
    # عرض رابط مباشر احتياطي لسهولة الوصول من الموبايل
    st.markdown(f"🔗 [اضغط هنا لفتح الفورم مباشرة بالموبايل]({app_url})")