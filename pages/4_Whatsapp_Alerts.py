import streamlit as st
import time

st.set_page_config(page_title="WhatsApp Alerts — Vanya Raksha AI", page_icon="📲", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
[data-testid="stAppViewContainer"] {
    background: #050a06;
    background-image: radial-gradient(ellipse at 15% 10%, rgba(22,101,52,0.1) 0%, transparent 55%);
}
[data-testid="stSidebar"] { background: #060d07; border-right: 1px solid rgba(22,101,52,0.15); }
#MainMenu, footer, header { visibility: hidden; }
h1,h2,h3,h4,h5,h6,p,span,div,li,td,th,label,a { font-family: 'DM Sans', sans-serif !important; }
.stMarkdown p { color: #94a3b0 !important; }
label[data-testid="stWidgetLabel"] p { color: #94a3b0 !important; }
.vr-page-header { font-family:'Instrument Serif',serif!important; font-size:36px; color:#f0fdf4; margin:0 0 4px; }
.vr-page-sub { font-size:14px; color:#6b7b8a; margin-bottom:24px; }
.msg-bubble { border-radius:12px; padding:14px 18px; margin:8px 0; font-size:13px; line-height:1.6; max-width:520px; }
.msg-system { background:rgba(34,197,94,0.06); border:1px solid rgba(34,197,94,0.15); color:#bbf7d0; }
.msg-alert-red { background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.25); color:#fca5a5; }
.msg-alert-yellow { background:rgba(250,204,21,0.08); border:1px solid rgba(250,204,21,0.25); color:#fde68a; }
.msg-alert-green { background:rgba(34,197,94,0.06); border:1px solid rgba(34,197,94,0.15); color:#bbf7d0; }
.phone-card { background:rgba(10,20,12,0.5); border:1px solid rgba(34,197,94,0.12); border-radius:16px; padding:28px; max-width:480px; }
.status-badge { display:inline-block; padding:4px 12px; border-radius:20px; font-size:11px; font-weight:600; letter-spacing:0.5px; }
</style>
""", unsafe_allow_html=True)

from utils_data import load_dashboard_data, TRANSECT_ORDER, route_segments
df, _, _, _ = load_dashboard_data()

ZONE_MESSAGES = {
    'high': {
        'icon': '🔴', 'title': 'DANGER ZONE — 1 KM AHEAD',
        'body': '🚨 *ALERT: {segment} — 1 km ahead*\n\n🔴 HIGH RISK wildlife zone\n🦌 Animal crossing probability: *{risk}%*\n🐾 Chances of animal crossing are HIGH\n🚗 *Reduce speed to 20 km/h NOW*',
        'css': 'msg-alert-red',
        'send_whatsapp': True,
    },
    'moderate': {
        'icon': '🟡', 'title': 'CAUTION — 1 KM AHEAD',
        'body': '⚠️ *CAUTION: {segment} — 1 km ahead*\n\n🟡 MODERATE wildlife crossing risk\n🦌 Animal crossing probability: *{risk}%*\n🐾 Be alert — animal crossings possible\n🚗 *Reduce speed to 30 km/h*',
        'css': 'msg-alert-yellow',
        'send_whatsapp': True,
    },
    'low': {
        'icon': '🟢', 'title': 'SAFE ZONE',
        'body': '✅ *{segment}* — Lower risk. Normal speed is fine.',
        'css': 'msg-alert-green',
        'send_whatsapp': False,
    },
}

def get_zone(risk):
    if risk >= 0.75: return 'high'
    elif risk >= 0.40: return 'moderate'
    return 'low'

def send_whatsapp(to_number, message_body, account_sid, auth_token):
    """Send WhatsApp message via Twilio sandbox. Returns (success, detail)."""
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message_body,
            from_='whatsapp:+14155238886',
            to=f'whatsapp:+{to_number}'
        )
        return True, msg.sid
    except ImportError:
        return False, "twilio not installed — run: pip install twilio"
    except Exception as e:
        return False, str(e)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="vr-page-header">📲 WhatsApp Driver Alert System</div>', unsafe_allow_html=True)
st.markdown('<div class="vr-page-sub">Register on entry → receive zone-based alerts as you travel → number auto-deleted on exit.</div>', unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
for key, default in [
    ('wa_registered', False), ('wa_phone', ''), ('wa_journey_started', False),
    ('wa_messages', []), ('wa_exited', False), ('wa_twilio_sid', ''),
    ('wa_twilio_token', ''), ('wa_twilio_connected', False),
    ('wa_start', ''), ('wa_end', ''), ('wa_season', ''),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Twilio credentials (sidebar) — stored in session state ────────────────────
with st.sidebar:
    st.markdown("### 🔑 Twilio Configuration")
    st.markdown("---")
    sid_input = st.text_input("Account SID", value=st.session_state.wa_twilio_sid, type="password", key="sid_field")
    token_input = st.text_input("Auth Token", value=st.session_state.wa_twilio_token, type="password", key="token_field")

    if sid_input and token_input:
        st.session_state.wa_twilio_sid = sid_input
        st.session_state.wa_twilio_token = token_input
        st.session_state.wa_twilio_connected = True
        st.success("✅ Twilio connected — real WhatsApp messages will be sent.")
    else:
        st.session_state.wa_twilio_connected = False
        st.info("Demo mode — paste SID & Token above to send real WhatsApp messages.")

    st.markdown("---")
    st.markdown("**Setup steps:**")
    st.markdown("1. Go to [twilio.com](https://twilio.com) → create free account")
    st.markdown("2. Go to Messaging → Try WhatsApp")
    st.markdown("3. Send `join <word>` to +14155238886 from your phone")
    st.markdown("4. Paste Account SID and Auth Token above")

twilio_ok = st.session_state.wa_twilio_connected
twilio_sid = st.session_state.wa_twilio_sid
twilio_token = st.session_state.wa_twilio_token


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — REGISTRATION
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.wa_registered:
    st.markdown("### 🚗 Step 1 — Driver Registration at Checkpoint")

    reg1, reg2 = st.columns([1, 1])
    with reg1:
        st.markdown('<div class="phone-card">', unsafe_allow_html=True)
        phone = st.text_input("Mobile number (with country code, no +)", placeholder="919444258684",
                              help="India: 91XXXXXXXXXX")
        start_seg = st.selectbox("Entry checkpoint", TRANSECT_ORDER, index=0)
        end_seg = st.selectbox("Exit checkpoint", TRANSECT_ORDER, index=len(TRANSECT_ORDER)-1)
        season = st.selectbox("Current season", ["monsoon", "summer"], index=0)

        if st.button("✅ Register & Enter Corridor", type="primary", use_container_width=True):
            if phone and len(phone) >= 10:
                st.session_state.wa_registered = True
                st.session_state.wa_phone = phone
                st.session_state.wa_start = start_seg
                st.session_state.wa_end = end_seg
                st.session_state.wa_season = season
                st.session_state.wa_messages = []
                st.session_state.wa_exited = False

                welcome = (
                    f"🛡️ *Vanya Raksha AI*\n\n"
                    f"Welcome to the Anamalai Wildlife Corridor.\n"
                    f"Your number *+{phone}* is now registered.\n\n"
                    f"📍 Entry: {start_seg}\n📍 Exit: {end_seg}\n"
                    f"🌿 Season: {season.capitalize()}\n\n"
                    f"You will receive zone-based wildlife alerts as you drive.\n"
                    f"Your number will be automatically deleted when you exit.\n\n"
                    f"🚗 Drive safe. Protect wildlife."
                )
                st.session_state.wa_messages.append(('system', welcome))

                # Send welcome WhatsApp
                if twilio_ok:
                    ok, detail = send_whatsapp(phone, welcome.replace('*',''), twilio_sid, twilio_token)
                    if ok:
                        st.session_state.wa_messages.append(('info', f'✅ Welcome message sent to WhatsApp'))
                    else:
                        st.session_state.wa_messages.append(('info', f'❌ WhatsApp failed: {detail}'))

                st.rerun()
            else:
                st.error("Enter a valid phone number with country code.")
        st.markdown('</div>', unsafe_allow_html=True)

    with reg2:
        st.markdown("""
        <div style="background:rgba(10,20,12,0.5);border:1px solid rgba(34,197,94,0.1);border-radius:16px;padding:24px;">
            <div style="font-size:15px;font-weight:600;color:#e2e8f0;margin-bottom:12px;">🔒 Privacy-First Design</div>
            <div style="font-size:13px;color:#6b7b8a;line-height:1.8;">
                <b style="color:#4ade80;">Entry:</b> Number stored in session memory only.<br>
                <b style="color:#fbbf24;">During journey:</b> WhatsApp alerts at each zone boundary.<br>
                <b style="color:#f87171;">Exit:</b> Number permanently deleted.<br><br>
                No data stored on disk. No tracking after exit.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — JOURNEY SIMULATION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.wa_registered and not st.session_state.wa_exited:
    phone = st.session_state.wa_phone

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
        <span class="status-badge" style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);color:#4ade80;">● ACTIVE</span>
        <span style="color:#94a3b0;font-size:14px;">
            Driver: <b style="color:#e2e8f0;">+{phone[:4]}****{phone[-4:]}</b> &nbsp;|&nbsp;
            {st.session_state.wa_start} → {st.session_state.wa_end}
            &nbsp;|&nbsp; Twilio: <b style="color:{'#4ade80' if twilio_ok else '#f87171'};">{'ON' if twilio_ok else 'OFF'}</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚗 Step 2 — Simulate Journey")

    segments = route_segments(st.session_state.wa_start, st.session_state.wa_end)
    route_df = df[(df['transect'].isin(segments)) & (df['season'] == st.session_state.wa_season)].copy()
    route_df['route_order'] = route_df['transect'].apply(lambda x: segments.index(x) if x in segments else 99)
    route_df = route_df.sort_values('route_order').reset_index(drop=True)

    if st.button("🚀 Start Journey Simulation", type="primary", use_container_width=True):
        progress = st.progress(0)
        status_box = st.empty()
        alert_container = st.container()

        for i, (_, seg_row) in enumerate(route_df.iterrows()):
            risk = seg_row['risk_probability']
            zone = get_zone(risk)
            zone_data = ZONE_MESSAGES[zone]
            risk_pct = round(risk * 100, 1)

            msg_text = zone_data['body'].format(segment=seg_row['transect'], risk=risk_pct)

            # Show in UI
            with alert_container:
                st.markdown(
                    f'<div class="msg-bubble {zone_data["css"]}">'
                    f'{zone_data["icon"]} <b>{zone_data["title"]}</b><br><br>'
                    f'{msg_text.replace(chr(10), "<br>")}</div>',
                    unsafe_allow_html=True
                )

            # Send real WhatsApp ONLY for high and moderate risk zones
            if twilio_ok and zone_data.get('send_whatsapp', False):
                status_box.info(f"📤 Sending WhatsApp alert for {seg_row['transect']} ({zone_data['title']})...")
                plain_msg = f"🛡️ Vanya Raksha AI\n\n{msg_text.replace('*', '')}"
                ok, detail = send_whatsapp(phone, plain_msg, twilio_sid, twilio_token)
                if ok:
                    status_box.success(f"✅ WhatsApp sent for {seg_row['transect']}")
                else:
                    status_box.error(f"❌ Failed for {seg_row['transect']}: {detail}")
                time.sleep(2.5)
            elif twilio_ok and not zone_data.get('send_whatsapp', False):
                status_box.info(f"🟢 {seg_row['transect']} — safe zone, no WhatsApp needed")
                time.sleep(1.0)
            else:
                time.sleep(1.5)

            progress.progress((i + 1) / len(route_df))

        # Journey complete — delete number
        exit_msg = (
            f"🏁 Journey Complete\n\n"
            f"You have exited the wildlife corridor at {st.session_state.wa_end}.\n\n"
            f"Your phone number +{phone[:4]}****{phone[-4:]} has been permanently deleted from our system.\n\n"
            f"Thank you for driving safely. 🌿"
        )

        if twilio_ok:
            send_whatsapp(phone, exit_msg, twilio_sid, twilio_token)

        with alert_container:
            st.markdown(f'<div class="msg-bubble msg-system">🏁 <b>JOURNEY COMPLETE</b><br><br>{exit_msg.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

        st.session_state.wa_exited = True
        st.session_state.wa_phone = ''
        status_box.empty()
        st.balloons()

    # Show past messages
    if st.session_state.wa_messages:
        st.markdown("---")
        st.markdown("### 📋 Alert Log")
        for msg_type, msg_text in st.session_state.wa_messages:
            if msg_type == 'info':
                st.caption(msg_text)
            elif msg_type == 'system':
                st.markdown(f'<div class="msg-bubble msg-system">{msg_text.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — POST-EXIT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.wa_exited:
    st.markdown("""
    <div style="text-align:center;padding:40px 20px;">
        <div style="font-size:48px;margin-bottom:16px;">✅</div>
        <div style="font-family:'Instrument Serif',serif;font-size:28px;color:#f0fdf4;margin-bottom:8px;">Journey Complete — Number Deleted</div>
        <div style="font-size:14px;color:#6b7b8a;max-width:400px;margin:0 auto;">The driver's phone number has been permanently removed. No data retained.</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Register New Driver", use_container_width=True):
        st.session_state.wa_registered = False
        st.session_state.wa_phone = ''
        st.session_state.wa_journey_started = False
        st.session_state.wa_messages = []
        st.session_state.wa_exited = False
        st.rerun()
        #final