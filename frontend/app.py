import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Web Security Scanner", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.email = None

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# ---------- LOGIN / REGISTER ----------
if not st.session_state.token:
    st.title("🔒 AI Web Security Scanner")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    st.session_state.email = email
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Login failed"))

    with tab2:
        with st.form("register_form"):
            full_name = st.text_input("Full name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_submitted = st.form_submit_button("Register")
            if reg_submitted:
                r = requests.post(
                    f"{API_URL}/auth/register",
                    json={"email": reg_email, "password": reg_password, "full_name": full_name},
                )
                if r.status_code == 201:
                    st.success("Registered! Now log in from the Login tab.")
                else:
                    st.error(r.json().get("detail", "Registration failed"))

    st.stop()

# ---------- MAIN APP (logged in) ----------
st.sidebar.write(f"Logged in as **{st.session_state.email}**")
if st.sidebar.button("Log out"):
    st.session_state.token = None
    st.session_state.email = None
    st.rerun()

st.title("🔒 AI Web Security Scanner")

col1, col2 = st.columns([1, 2])

# --- Targets ---
with col1:
    st.subheader("Targets")

    with st.form("add_target_form"):
        name = st.text_input("Target name")
        url = st.text_input("URL / host (e.g. scanme.nmap.org)")
        add_submitted = st.form_submit_button("Add target")
        if add_submitted and name and url:
            r = requests.post(f"{API_URL}/targets", json={"name": name, "url": url}, headers=auth_headers())
            if r.status_code == 201:
                st.success("Target added")
                st.rerun()
            else:
                st.error(r.text)

    targets_resp = requests.get(f"{API_URL}/targets", headers=auth_headers())
    targets = targets_resp.json() if targets_resp.status_code == 200 else []

    if not targets:
        st.info("No targets yet — add one above.")
    else:
        for t in targets:
            with st.container(border=True):
                st.write(f"**{t['name']}**")
                st.caption(t["url"])
                c1, c2 = st.columns(2)
                if c1.button("Launch scan", key=f"scan_{t['id']}"):
                    r = requests.post(f"{API_URL}/targets/{t['id']}/scans", headers=auth_headers())
                    if r.status_code == 201:
                        st.success(f"Scan queued: {r.json()['id']}")
                    else:
                        st.error(r.text)
                if c2.button("Delete", key=f"del_{t['id']}"):
                    requests.delete(f"{API_URL}/targets/{t['id']}", headers=auth_headers())
                    st.rerun()

# --- Scans & vulnerabilities ---
with col2:
    st.subheader("Scans")

    if st.button("🔄 Refresh scans"):
        st.rerun()

    scans_resp = requests.get(f"{API_URL}/scans", headers=auth_headers())
    scans = scans_resp.json() if scans_resp.status_code == 200 else []

    if not scans:
        st.info("No scans yet — launch one from a target on the left.")
    else:
        for s in scans:
            status_emoji = {"queued": "⏳", "running": "🔄", "completed": "✅", "failed": "❌"}.get(s["status"], "❔")
            with st.expander(f"{status_emoji} Scan {s['id'][:8]} — {s['status']}"):
                detail_resp = requests.get(f"{API_URL}/scans/{s['id']}", headers=auth_headers())
                if detail_resp.status_code != 200:
                    st.error("Could not load scan detail")
                    continue
                detail = detail_resp.json()

                vulns = detail.get("vulnerabilities", [])
                if not vulns:
                    st.write("No vulnerabilities found (or scan still running).")
                for v in vulns:
                    st.markdown(f"**{v['title']}** — severity: `{v['severity']}`")
                    st.caption(v.get("description", ""))

                    analyze_key = f"analyze_{v['id']}"
                    if st.button("🤖 AI Analyze", key=analyze_key):
                        with st.spinner("Asking AI..."):
                            ar = requests.post(f"{API_URL}/vulnerabilities/{v['id']}/analyze", headers=auth_headers())
                        if ar.status_code == 200:
                            result = ar.json()
                            st.success("Analysis complete")
                            st.write("**Explanation:**", result["plain_english_explanation"])
                            st.write("**Remediation:**", result["remediation_steps"])
                            st.write("**Risk:**", result["risk_context"])
                        else:
                            st.error(ar.text)
                    st.divider()
