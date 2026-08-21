"""
🎯 Financial OSINT Tool — Panel SUPER POTENCIADO
"""
import os
import sys
import json
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engines.extraction_engine import ExtractionEngine, EXTRACTION_PORTALS
from engines.institution_matcher import INSTITUTIONS
from engines.credit_score_engine import CreditScoreEngine
from engines.export_engine import ExportEngine
from engines.route_account_engine import RouteAccountEngine, SearchField
from engines.account_validator import AccountValidator, BatchValidation
from engines.plaid_engine import PlaidEngine
from engines.card_analyzer import CardAnalyzer, BatchCardAnalysis

# Import user tracker
try:
    from user_tracker import (
        log_activity, get_user_stats, get_global_stats,
        create_tracked_user, authenticate_user, get_all_tracked_users
    )
    HAS_TRACKER = True
except ImportError:
    HAS_TRACKER = False

st.set_page_config(page_title="Financial OSINT Tool PRO", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0a0a0f; }
    section[data-testid="stSidebar"] { background-color: #0d1117; }
    section[data-testid="stSidebar"] .stMarkdown { color: #c9d1d9; }
    section[data-testid="stSidebar"] .stTextInput label { color: #8b949e; }
    section[data-testid="stSidebar"] .stSelectbox label { color: #8b949e; }
    section[data-testid="stSidebar"] .stSlider label { color: #8b949e; }
    section[data-testid="stSidebar"] .stRadio label { color: #8b949e; }
    section[data-testid="stSidebar"] .stToggle label { color: #8b949e; }
    section[data-testid="stSidebar"] .stMetric label { color: #8b949e; }
    section[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] { color: #e94560; }
    section[data-testid="stSidebar"] hr { border-color: #21262d; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: #e94560 !important; }
    h1, h2, h3, h4 { color: #fff !important; }
    .stMetric { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; }
    .stMetric [data-testid="stMetricValue"] { color: #e94560 !important; }
    .score-badge { display: inline-block; padding: 8px 20px; border-radius: 12px; font-size: 2rem; font-weight: 800; }
    .score-excellent { background: rgba(0,200,83,0.15); color: #00c853; border: 1px solid rgba(0,200,83,0.3); }
    .score-good { background: rgba(100,221,23,0.15); color: #64dd17; border: 1px solid rgba(100,221,23,0.3); }
    .score-fair { background: rgba(255,214,0,0.15); color: #ffd600; border: 1px solid rgba(255,214,0,0.3); }
    .score-poor { background: rgba(233,69,96,0.15); color: #e94560; border: 1px solid rgba(233,69,96,0.3); }
    .data-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; margin-bottom: 8px; }
    .email-card { background: rgba(0,212,255,0.05); border-left: 3px solid #00d4ff; padding: 12px; margin-bottom: 6px; border-radius: 0 8px 8px 0; }
    .phone-card { background: rgba(0,200,83,0.05); border-left: 3px solid #00c853; padding: 12px; margin-bottom: 6px; border-radius: 0 8px 8px 0; }
    .breach-card { background: rgba(233,69,96,0.05); border-left: 3px solid #e94560; padding: 12px; margin-bottom: 6px; border-radius: 0 8px 8px 0; }
    .inst-card { background: rgba(255,215,0,0.05); border-left: 3px solid #ffd700; padding: 12px; margin-bottom: 6px; border-radius: 0 8px 8px 0; }
    .password-card { background: rgba(233,69,96,0.1); border: 1px solid rgba(233,69,96,0.3); padding: 8px 12px; border-radius: 8px; font-family: monospace; }
    .risk-high { color: #e94560; font-weight: 700; }
    .risk-medium { color: #ffd700; font-weight: 700; }
    .risk-low { color: #00d4ff; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

def get_engine():
    return ExtractionEngine(
        leakcheck_key=st.session_state.get("lc_key", os.environ.get("LEAKCHECK_API_KEY", "")),
    )

engine = get_engine()
exporter = ExportEngine()
credit_engine = CreditScoreEngine()

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    # === USER LOGIN ===
    if HAS_TRACKER:
        if "tracker_user" not in st.session_state:
            st.session_state.tracker_user = None
        
        if st.session_state.tracker_user:
            user = st.session_state.tracker_user
            st.markdown(f"""
            <div style="background:#0d4429; border:1px solid #3fb950; border-radius:10px; padding:12px; margin-bottom:16px;">
                👤 <b>{user['username']}</b><br>
                <span style="color:#8b949e; font-size:12px;">{user['email']}</span><br>
                <span style="color:#e94560; font-size:12px;">💰 {user.get('credits', 0)} créditos</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.tracker_user = None
                st.rerun()
        else:
            with st.expander("👤 Iniciar Sesión", expanded=False):
                login_tab1, login_tab2 = st.tabs(["Login", "Registro"])
                with login_tab1:
                    l_user = st.text_input("Usuario o email", key="login_user")
                    l_pass = st.text_input("Contraseña", type="password", key="login_pass")
                    if st.button("Entrar", use_container_width=True, key="btn_login"):
                        user, session_id = authenticate_user(l_user, l_pass)
                        if user:
                            st.session_state.tracker_user = user
                            st.success(f"Bienvenido {user['username']}!")
                            st.rerun()
                        else:
                            st.error("Credenciales incorrectas")
                with login_tab2:
                    r_user = st.text_input("Usuario", key="reg_user")
                    r_email = st.text_input("Email", key="reg_email")
                    r_pass = st.text_input("Contraseña", type="password", key="reg_pass")
                    if st.button("Crear Cuenta", use_container_width=True, key="btn_register"):
                        if r_user and r_email and r_pass:
                            user = create_tracked_user(r_user, r_email, r_pass)
                            if user:
                                st.session_state.tracker_user = user
                                st.success("Cuenta creada!")
                                st.rerun()
                            else:
                                st.error("Usuario o email ya existe")
    
    st.markdown("---")
    st.markdown("## ⚡ Financial OSINT PRO")
    st.markdown("Motor de inteligencia financiera")

    st.markdown("---")
    st.markdown("### 🔑 APIs Configuradas")

    # LeakCheck
    lc_key = st.text_input("LeakCheck Pro Key", type="password", help="$10/mes - leakcheck.io")
    if lc_key:
        st.success("✅ LeakCheck Pro")
        st.session_state["lc_key"] = lc_key
    else:
        st.warning("⚠️ LeakCheck no configurado")

    # DeHashed
    dh_key = st.text_input("DeHashed Key", type="password", help="$20/mes - dehashed.com")
    if dh_key:
        st.success("✅ DeHashed")
        st.session_state["dh_key"] = dh_key

    # IntelligenceX
    ix_key = st.text_input("IntelligenceX Key", type="password", help="$50/mes - intelx.io")
    if ix_key:
        st.success("✅ IntelligenceX")
        st.session_state["ix_key"] = ix_key

    # Snusbase
    sb_key = st.text_input("Snusbase Key", type="password", help="$30/mes - snusbase.com")
    if sb_key:
        st.success("✅ Snusbase")
        st.session_state["sb_key"] = sb_key

    st.markdown("---")
    st.markdown("### 🏦 Instituciones")
    inst_list = list(INSTITUTIONS.keys())
    selected_inst = st.multiselect(
        "Filtrar", inst_list,
        format_func=lambda x: INSTITUTIONS[x]["name"],
    )

    st.markdown("---")
    st.markdown("### 🔧 Motores")
    for key_p, portal in EXTRACTION_PORTALS.items():
        if portal["status"] == "active":
            st.markdown(f"✅ {portal['name']}")
        else:
            st.markdown(f"🔒 {portal['name']} — *requiere API key*")

    st.markdown("---")
    st.markdown("### 📖 Ayuda")
    st.markdown("[📄 Setup Completo](https://github.com)")
    st.markdown("[🔑 Obtener LeakCheck Pro](https://leakcheck.io)")
    st.markdown("[🔑 Obtener DeHashed](https://dehashed.com)")
    st.markdown("[🔑 Obtener IntelligenceX](https://intelx.io)")
    st.markdown("[🔑 Obtener Snusbase](https://snusbase.com)")

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🔍 Búsqueda Universal",
    "🔐 SSN Lookup",
    "🗺️ Route & Account Finder",
    "🏦 Validador de Cuentas",
    "💳 Credit Card Analyzer",
    "📊 Credit Score",
    "📥 Exportar",
    "📖 Setup & Ayuda",
])

# ─── TAB 1: Búsqueda ────────────────────────────────────────

with tab1:
    st.markdown("## 🔍 Búsqueda Universal")
    st.markdown("Busca por **dirección**, **email**, **teléfono**, o **nombre** — el motor encuentra todo lo asociado")

    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Dato a buscar",
            placeholder="1206 Laurel Ln Richardson, TX 75080  •  email@domain.com  •  +1-212-555-1234  •  John Smith",
        )
    with col2:
        query_type = st.selectbox("Tipo", ["auto", "address", "email", "phone", "name"])

    # Indicador de motor
    is_address = query and ('TX' in query or '75' in query or 'St' in query or 'Ln' in query or 'Ave' in query)
    if is_address:
        st.info("🏠 **Motor de Dirección Activo** — Buscando en múltiples fuentes...")

    if st.button("⚡ BUSCAR", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Ingresa un dato")
        else:
            with st.spinner("⚡ Motor multi-fuente procesando..."):
                result = engine.full_search(query, query_type, institutions=selected_inst)
                st.session_state["last_result"] = result
                st.session_state["last_query"] = query
                
                # Track search
                if HAS_TRACKER and st.session_state.get("tracker_user"):
                    log_activity(st.session_state.tracker_user["id"], "osint_search", {
                        "query": query[:100],
                        "type": query_type,
                        "profiles": len(result.profiles)
                    })

    # ── Resultados ──
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]

        st.markdown("---")
        st.markdown("## 📊 Resumen de Inteligencia")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("👤 Perfiles", len(result.profiles))
        c2.metric("📋 Brechas", result.total_breaches)
        c3.metric("⚡ Exposiciones", result.total_exposures)
        score = result.exposure_score
        color = "🔴" if score > 60 else "🟡" if score > 30 else "🟢"
        c4.metric("🎯 Riesgo", f"{color} {score}")

        # Credit Score total
        total_cs = sum(
            p.raw_data.get("credit_score", 0)
            for p in result.profiles
            if p.raw_data and p.raw_data.get("credit_score")
        )
        avg_cs = total_cs // len(result.profiles) if result.profiles and total_cs else 0
        c5.metric("📊 Credit Score", f"~{avg_cs}" if avg_cs else "N/A")

        # ── Perfiles ──
        for i, profile in enumerate(result.profiles):
            st.markdown("---")
            st.markdown(f"### 👤 Perfil {i+1}: {profile.name or 'Sin nombre identificado'}")

            # Risk + Credit Score en una fila
            col_risk, col_cs = st.columns(2)
            with col_risk:
                if profile.risk_score > 60:
                    st.markdown(f'<div class="data-card"><span class="risk-high">🔴 RIESGO ALTO: {profile.risk_score}/100</span></div>', unsafe_allow_html=True)
                elif profile.risk_score > 30:
                    st.markdown(f'<div class="data-card"><span class="risk-medium">🟡 RIESGO MEDIO: {profile.risk_score}/100</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="data-card"><span class="risk-low">🟢 RIESGO BAJO: {profile.risk_score}/100</span></div>', unsafe_allow_html=True)

            with col_cs:
                cs = profile.raw_data.get("credit_score") if profile.raw_data else None
                grade = profile.raw_data.get("credit_grade") if profile.raw_data else None
                if cs:
                    grade_class = "score-excellent" if cs >= 740 else "score-good" if cs >= 670 else "score-fair" if cs >= 580 else "score-poor"
                    st.markdown(f'<div class="data-card"><span class="score-badge {grade_class}">📊 {cs} — {grade}</span></div>', unsafe_allow_html=True)

            # SSN y DOB
            if profile.ssn or profile.dob:
                col_a, col_b = st.columns(2)
                with col_a:
                    if profile.ssn:
                        masked = f"***-**-{profile.ssn[-4:]}" if len(profile.ssn) >= 4 else "***-**-****"
                        st.markdown(f"**🔑 SSN:** `{masked}`")
                with col_b:
                    if profile.dob:
                        st.markdown(f"**📅 DOB:** `{profile.dob}`")

            # ── Emails ──
            if profile.emails:
                st.markdown(f"#### 📧 Emails ({len(profile.emails)})")
                for email in profile.emails:
                    inst_match = engine.matcher.match_email(email)
                    badges = " ".join([f"`{i.institution}`" for i in inst_match])
                    st.markdown(
                        f'<div class="email-card">📧 <code>{email}</code>'
                        f'{" → " + badges if badges else ""}</div>',
                        unsafe_allow_html=True,
                    )

            # ── Teléfonos ──
            if profile.phones:
                st.markdown(f"#### 📱 Teléfonos ({len(profile.phones)})")
                for phone in profile.phones:
                    inst_match = engine.matcher.match_phone(phone)
                    badges = " ".join([f"`{i.institution}`" for i in inst_match])
                    st.markdown(
                        f'<div class="phone-card">📱 <code>{phone}</code>'
                        f'{" → " + badges if badges else ""}</div>',
                        unsafe_allow_html=True,
                    )

            # ── Passwords ──
            if profile.passwords:
                st.markdown(f"#### 🔑 Passwords Expuestos ({len(profile.passwords)})")
                for pw in profile.passwords:
                    st.markdown(f'<div class="password-card">🔑 <code>{pw}</code></div>', unsafe_allow_html=True)

            # ── Tarjetas ──
            if profile.credit_cards:
                st.markdown(f"#### 💳 Tarjetas ({len(profile.credit_cards)})")
                for cc in profile.credit_cards:
                    st.markdown(f"💳 `{cc}`")

            # ── Instituciones ──
            if profile.institutions:
                st.markdown(f"#### 🏦 Instituciones Detectadas ({len(profile.institutions)})")
                for inst in profile.institutions:
                    st.markdown(
                        f'<div class="inst-card">🏦 <strong>{inst.institution}</strong> '
                        f'({inst.institution_type}) — {inst.evidence}</div>',
                        unsafe_allow_html=True,
                    )

            # ── Brechas ──
            if profile.breach_sources:
                st.markdown(f"#### 📋 Fuentes de Brechas ({len(profile.breach_sources)})")
                with st.expander(f"Ver {len(profile.breach_sources)} fuentes"):
                    for b in profile.breach_sources:
                        st.markdown(f'<div class="breach-card">📋 {b}</div>', unsafe_allow_html=True)

            # Exportar individual
            if st.button(f"📥 Exportar Perfil {i+1}", key=f"exp_{i}"):
                from core.models import SearchResult as SR
                r = SR(request=result.request, profiles=[profile])
                files = exporter.export_all(r)
                st.success(f"✅ {files['csv']}")

# ─── TAB 2: SSN Lookup ─────────────────────────────────────

with tab2:
    st.markdown("## 🔐 SSN Lookup — Búsqueda de Identidad")
    st.markdown("Busca el nombre, dirección y datos asociados a un SSN, o encuentra el SSN desde un nombre/dirección")

    ssn_tab1, ssn_tab2 = st.tabs(["SSN → Identidad", "Nombre/Dirección → SSN"])

    with ssn_tab1:
        st.markdown("### 🔍 SSN → Identidad Completa")
        ssn_input = st.text_input(
            "Ingresa el SSN",
            placeholder="123-45-6789",
            key="ssn_direct",
        )

        if st.button("⚡ Buscar por SSN", type="primary", key="btn_ssn"):
            if ssn_input:
                with st.spinner("🔍 Buscando identidad en múltiples fuentes..."):
                    result = engine.full_search(ssn_input, "ssn")
                    if result.profiles:
                        for p in result.profiles:
                            st.markdown("---")
                            st.markdown(f"### 👤 Identidad Encontrada: {p.name or 'Sin nombre'}")

                            # SSN
                            if p.ssn:
                                st.markdown(f"**🔑 SSN:** `{p.ssn}`")
                            if p.dob:
                                st.markdown(f"**📅 DOB:** `{p.dob}`")

                            # Emails
                            if p.emails:
                                st.markdown(f"**📧 Emails:** {', '.join(p.emails)}")

                            # Phones
                            if p.phones:
                                st.markdown(f"**📱 Teléfonos:** {', '.join(p.phones)}")

                            # Addresses
                            if p.addresses:
                                st.markdown(f"**📍 Direcciones:** {', '.join(p.addresses)}")

                            # Credit Score
                            cs = p.raw_data.get("credit_score") if p.raw_data else None
                            if cs:
                                grade = p.raw_data.get("credit_grade", "")
                                st.markdown(f"**📊 Credit Score:** ~{cs} ({grade})")

                            # Breaches
                            if p.breach_sources:
                                st.markdown(f"**📋 Brechas:** {len(p.breach_sources)} fuentes")
                                with st.expander("Ver fuentes"):
                                    for b in p.breach_sources:
                                        st.markdown(f"• {b}")

                            # Confidence
                            conf = p.raw_data.get("ssn_confidence", 0) if p.raw_data else 0
                            if conf:
                                st.markdown(f"**🎯 Confianza:** {int(conf * 100)}%")
                    else:
                        st.warning("No se encontraron datos para este SSN")

    with ssn_tab2:
        st.markdown("### 🔍 Nombre/Dirección → SSN")
        st.info("💡 Busca el SSN asociado a un nombre o dirección (si existe en brechas)")

        reverse_input = st.text_input(
            "Nombre o Dirección",
            placeholder="John Smith  •  123 Main St, New York, NY 10001",
            key="reverse_input",
        )
        reverse_type = st.selectbox("Tipo", ["name", "address"], key="reverse_type")

        if st.button("⚡ Buscar SSN", type="primary", key="btn_reverse"):
            if reverse_input:
                with st.spinner("🔍 Buscando SSN en brechas..."):
                    identity = engine.ssn_lookup.reverse_lookup(**{reverse_type: reverse_input})
                    if identity.ssn:
                        st.success(f"✅ SSN encontrado: `{identity.ssn}`")
                        if identity.name:
                            st.markdown(f"**Nombre:** {identity.name}")
                        if identity.dob:
                            st.markdown(f"**DOB:** {identity.dob}")
                        if identity.phones:
                            st.markdown(f"**Teléfonos:** {', '.join(identity.phones)}")
                        if identity.emails:
                            st.markdown(f"**Emails:** {', '.join(identity.emails)}")
                        if identity.breach_sources:
                            st.markdown(f"**Fuentes:** {len(identity.breach_sources)} brechas")
                        st.markdown(f"**Confianza:** {int(identity.confidence * 100)}%")
                    else:
                        st.warning("No se encontró SSN para esta búsqueda")
                        st.info("💡 Intenta con LeakCheck Pro o DeHashed para mejores resultados")

# ─── TAB 3: Route & Account Finder ──────────────────────────

with tab3:
    st.markdown("## 🗺️ Route & Account Finder")
    st.markdown(
        "Motor unificado de extracción. Ingresa **un campo** o sube un **lote/CSV** y el motor cruza "
        "múltiples fuentes para encontrar emails, teléfonos, SSN, rutas, cuentas bancarias, passwords, "
        "credit cards y credit score asociados."
    )

    # --- Init engine ---
    route_engine = RouteAccountEngine(
        leakcheck_key=st.session_state.get("lc_key", os.environ.get("LEAKCHECK_API_KEY", "")),
        dehashed_key=st.session_state.get("dh_key"),
        intelx_key=st.session_state.get("ix_key"),
    )

    route_mode = st.radio(
        "Modo de búsqueda",
        ["🔍 Búsqueda Individual", "📁 Lote (textarea)", "📄 Subir CSV/Excel"],
        horizontal=True,
        key="route_mode",
    )

    # ════════════════════════════════════════════════════════════
    # MODO 1: Búsqueda Individual
    # ════════════════════════════════════════════════════════════
    if route_mode.startswith("🔍"):
        st.markdown("### 🔍 Búsqueda Individual")
        st.caption("El motor detecta automáticamente el tipo de campo")

        rc1, rc2 = st.columns([5, 1])
        with rc1:
            route_input = st.text_input(
                "Campo de búsqueda",
                placeholder="email@domain.com  •  +1-212-555-1234  •  123-45-6789  •  1206 Laurel Ln, TX 75080  •  John Smith  •  01/15/1990",
                key="route_single",
            )
        with rc2:
            route_type = st.selectbox(
                "Tipo (auto=detecta)",
                ["auto", "email", "phone", "ssn", "address", "name", "dob", "username", "domain"],
                key="route_single_type",
            )

        if st.button("⚡ EXTRAER DATOS", type="primary", use_container_width=True, key="btn_route_single"):
            if route_input.strip():
                field = SearchField(
                    field_type=route_type if route_type != "auto" else RouteAccountEngine._detect_field_type(route_input),
                    value=route_input.strip(),
                )
                with st.spinner(f"⚡ Extrayendo datos de múltiples fuentes para: {field.field_type}..."):
                    result = route_engine.search_single(field)
                    st.session_state["route_last_result"] = result

                    # Track
                    if HAS_TRACKER and st.session_state.get("tracker_user"):
                        log_activity(st.session_state.tracker_user["id"], "route_search", {
                            "input": route_input[:100],
                            "type": field.field_type,
                            "total_data": result.total_data(),
                        })

        # --- Mostrar resultado individual ---
        if "route_last_result" in st.session_state:
            r = st.session_state["route_last_result"]
            st.markdown("---")

            # Metrics row
            mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
            mc1.metric("📧 Emails", len(r.emails))
            mc2.metric("📱 Teléfonos", len(r.phones))
            mc3.metric("👤 Nombres", len(r.names))
            mc4.metric("🔑 SSN", len(r.ssns))
            mc5.metric("🏦 Bancos", len(r.banks))
            mc6.metric("🎯 Riesgo", f"{r.risk_score}/100")

            # Credit Score
            if r.credit_score:
                gc = "score-excellent" if r.credit_score >= 740 else "score-good" if r.credit_score >= 670 else "score-fair" if r.credit_score >= 580 else "score-poor"
                st.markdown(f'<div class="score-badge {gc}" style="font-size:2rem;">📊 Credit Score: {r.credit_score} — {r.credit_grade}</div>', unsafe_allow_html=True)

            # Emails
            if r.emails:
                st.markdown(f"#### 📧 Emails ({len(r.emails)})")
                for e in r.emails:
                    inst_badges = ""
                    for m in route_engine._get_matcher().match_email(e):
                        inst_badges += f" <code>{m.institution}</code>"
                    st.markdown(f'<div class="email-card">📧 <code>{e}</code>{inst_badges}</div>', unsafe_allow_html=True)

            # Phones
            if r.phones:
                st.markdown(f"#### 📱 Teléfonos ({len(r.phones)})")
                for p in r.phones:
                    inst_badges = ""
                    for m in route_engine._get_matcher().match_phone(p):
                        inst_badges += f" <code>{m.institution}</code>"
                    st.markdown(f'<div class="phone-card">📱 <code>{p}</code>{inst_badges}</div>', unsafe_allow_html=True)

            # Names
            if r.names:
                st.markdown(f"#### 👤 Nombres ({len(r.names)})")
                for n in r.names:
                    st.markdown(f"- 👤 **{n}**")

            # Addresses
            if r.addresses:
                st.markdown(f"#### 🏠 Direcciones ({len(r.addresses)})")
                for a in r.addresses:
                    st.markdown(f"- 📍 **{a}**")

            # SSN
            if r.ssns:
                st.markdown(f"#### 🔑 SSN ({len(r.ssns)})")
                for s in r.ssns:
                    masked = f"***-**-{s[-4:]}" if len(s) >= 4 else "***-**-****"
                    st.markdown(f"- 🔑 `{masked}`")

            # DOB
            if r.dobs:
                st.markdown(f"#### 📅 Fecha de Nacimiento ({len(r.dobs)})")
                for d in r.dobs:
                    st.markdown(f"- 📅 `{d}`")

            # Banks
            if r.banks:
                st.markdown(f"#### 🏦 Bancos / Instituciones ({len(r.banks)})")
                for b in r.banks:
                    st.markdown(f'<div class="inst-card">🏦 <strong>{b}</strong></div>', unsafe_allow_html=True)

            # Accounts
            if r.accounts:
                st.markdown(f"#### 💼 Cuentas ({len(r.accounts)})")
                for a in r.accounts:
                    st.markdown(f"- 💼 `{a}`")

            # Credit Cards
            if r.credit_cards:
                st.markdown(f"#### 💳 Tarjetas de Crédito ({len(r.credit_cards)})")
                for cc in r.credit_cards:
                    st.markdown(f'<div class="password-card">💳 <code>{cc}</code></div>', unsafe_allow_html=True)

            # Passwords
            if r.passwords:
                st.markdown(f"#### 🔐 Passwords ({len(r.passwords)})")
                for pw in r.passwords:
                    st.markdown(f'<div class="password-card">🔑 <code>{pw}</code></div>', unsafe_allow_html=True)

            # Breach sources
            if r.breach_sources:
                with st.expander(f"📋 Fuentes de Brechas ({len(r.breach_sources)})"):
                    for b in r.breach_sources:
                        st.markdown(f"- {b}")

            # Institutions
            if r.institutions:
                with st.expander(f"🏛️ Instituciones detectadas ({len(r.institutions)})"):
                    for inst in r.institutions:
                        st.markdown(f"- 🏛️ **{inst['name']}** ({inst['type']}) — {inst['evidence']}")

            # Sources & time
            st.caption(f"Fuentes consultadas: {', '.join(r.sources_checked)}  |  Tiempo: {r.search_time_ms}ms")

    # ════════════════════════════════════════════════════════════
    # MODO 2: Lote (textarea)
    # ════════════════════════════════════════════════════════════
    elif route_mode.startswith("📁"):
        st.markdown("### 📁 Búsqueda Masiva")
        st.caption("Un campo por línea. El motor detecta el tipo automáticamente.")

        route_batch_text = st.text_area(
            "Campos de búsqueda",
            height=250,
            placeholder="email@domain.com\n+1-212-555-1234\n123-45-6789\n1206 Laurel Ln Richardson, TX 75080\nJohn Smith\n01/15/1990",
            key="route_batch_text",
        )

        route_workers = st.slider("Hilos paralelos", 1, 10, 5, key="route_workers")

        if st.button("⚡ EJECutar LOTE", type="primary", use_container_width=True, key="btn_route_batch"):
            if route_batch_text.strip():
                fields = RouteAccountEngine.parse_batch_input(route_batch_text)
                st.info(f"📋 {len(fields)} campos detectados")

                progress = st.progress(0)
                status_text = st.empty()

                def route_progress(done, total):
                    progress.progress(done / total)
                    status_text.text(f"⚡ Procesando {done}/{total}...")

                with st.spinner(f"⚡ Ejecutando {len(fields)} búsquedas en paralelo..."):
                    batch = route_engine.search_batch(fields, max_workers=route_workers, on_progress=route_progress)
                    st.session_state["route_batch_result"] = batch
                    status_text.text(f"✅ Completado: {batch.total_queries} consultas, {batch.total_results} datos en {batch.total_time_ms}ms")

                    # Track
                    if HAS_TRACKER and st.session_state.get("tracker_user"):
                        log_activity(st.session_state.tracker_user["id"], "route_batch", {
                            "queries": batch.total_queries,
                            "results": batch.total_results,
                        })

        # --- Mostrar resultados del lote ---
        if "route_batch_result" in st.session_state:
            batch = st.session_state["route_batch_result"]
            st.markdown("---")
            st.markdown(f"### 📊 Resultados: {batch.total_queries} consultas → {batch.total_results} datos ({batch.total_time_ms}ms)")

            # Table
            rows = []
            for r in batch.results:
                rows.append({
                    "Tipo": r.input_field,
                    "Input": r.input_value[:50],
                    "📧 Emails": len(r.emails),
                    "📱 Phones": len(r.phones),
                    "👤 Names": len(r.names),
                    "🔑 SSN": len(r.ssns),
                    "🏦 Banks": len(r.banks),
                    "💳 Cards": len(r.credit_cards),
                    "🔐 PW": len(r.passwords),
                    "📊 Score": r.credit_score or "",
                    "🎯 Risk": r.risk_score,
                    "Fuentes": len(r.sources_checked),
                    "ms": r.search_time_ms,
                })
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)

            # Export buttons
            st.markdown("### 📥 Exportar Resultados")
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                csv_data = RouteAccountEngine.export_csv(batch)
                st.download_button("📄 CSV", csv_data, "route_results.csv", "text/csv", use_container_width=True)
            with ec2:
                json_data = RouteAccountEngine.export_json(batch)
                st.download_button("📋 JSON", json_data, "route_results.json", "application/json", use_container_width=True)
            with ec3:
                txt_data = RouteAccountEngine.export_txt(batch)
                st.download_button("📝 TXT", txt_data, "route_results.txt", "text/plain", use_container_width=True)

    # ════════════════════════════════════════════════════════════
    # MODO 3: Subir CSV/Excel
    # ════════════════════════════════════════════════════════════
    elif route_mode.startswith("📄"):
        st.markdown("### 📄 Subir Archivo CSV o Excel")
        st.caption("El motor detecta columnas: email, phone, ssn, address, name, dob, username, domain")

        uploaded_file = st.file_uploader(
            "Sube tu archivo",
            type=["csv", "xlsx", "xls"],
            key="route_upload",
        )

        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    content = uploaded_file.read().decode("utf-8", errors="ignore")
                    fields = RouteAccountEngine.parse_csv(content)
                    df_preview = pd.read_csv(uploaded_file)
                    uploaded_file.seek(0)
                else:
                    df_preview = pd.read_excel(uploaded_file)
                    # For Excel, convert to CSV for parsing
                    import io as _io
                    buf = _io.StringIO()
                    df_preview.to_csv(buf, index=False)
                    fields = RouteAccountEngine.parse_csv(buf.getvalue())

                st.markdown(f"📋 **{len(df_preview)} filas** → **{len(fields)} campos detectados para búsqueda**")
                st.dataframe(df_preview.head(10), use_container_width=True)

                if fields:
                    field_counts = {}
                    for f in fields:
                        field_counts[f.field_type] = field_counts.get(f.field_type, 0) + 1
                    st.markdown("**Distribución de campos:**")
                    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
                    for i, (ft, cnt) in enumerate(field_counts.items()):
                        if i < 5:
                            [fc1, fc2, fc3, fc4, fc5][i].metric(ft, cnt)

                    route_workers_csv = st.slider("Hilos paralelos", 1, 10, 5, key="route_workers_csv")

                    if st.button("⚡ EJECutar BATCH desde CSV", type="primary", use_container_width=True, key="btn_route_csv"):
                        progress = st.progress(0)
                        status_text = st.empty()

                        def csv_progress(done, total):
                            progress.progress(done / total)
                            status_text.text(f"⚡ Procesando {done}/{total}...")

                        with st.spinner(f"⚡ Ejecutando {len(fields)} búsquedas desde CSV..."):
                            batch = route_engine.search_batch(fields, max_workers=route_workers_csv, on_progress=csv_progress)
                            st.session_state["route_batch_result"] = batch
                            status_text.text(f"✅ Completado: {batch.total_queries} consultas, {batch.total_results} datos")

                            if HAS_TRACKER and st.session_state.get("tracker_user"):
                                log_activity(st.session_state.tracker_user["id"], "route_csv_batch", {
                                    "file": uploaded_file.name,
                                    "queries": batch.total_queries,
                                    "results": batch.total_results,
                                })
            except Exception as e:
                st.error(f"Error leyendo archivo: {e}")

        else:
            st.info("📄 Arrastra un archivo CSV o Excel con tus datos")

            # Template download
            template = """email,phone,ssn,address,name,dob
user@example.com,+1-212-555-1234,123-45-6789,1206 Laurel Ln Richardson TX 75080,John Smith,01/15/1990
other@example.com,,987-65-4321,456 Oak Ave Dallas TX 75201,Jane Doe,03/22/1985"""
            st.download_button("📥 Descargar template CSV", template, "template.csv", "text/csv")

    # --- Resultados compartidos entre modos ---
    if "route_batch_result" in st.session_state and not route_mode.startswith("🔍"):
        batch = st.session_state["route_batch_result"]
        st.markdown("---")
        st.markdown(f"### 📊 Resumen del Lote: {batch.total_queries} consultas → {batch.total_results} datos")

        # Table
        rows = []
        for r in batch.results:
            rows.append({
                "Tipo": r.input_field,
                "Input": r.input_value[:50],
                "📧 Emails": len(r.emails),
                "📱 Phones": len(r.phones),
                "👤 Names": len(r.names),
                "🔑 SSN": len(r.ssns),
                "🏦 Banks": len(r.banks),
                "💳 Cards": len(r.credit_cards),
                "🔐 PW": len(r.passwords),
                "📊 Score": r.credit_score or "",
                "🎯 Risk": r.risk_score,
            })
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

        # Export
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            csv_data = RouteAccountEngine.export_csv(batch)
            st.download_button("📄 CSV", csv_data, "route_results.csv", "text/csv", use_container_width=True, key="dl_csv_batch")
        with ec2:
            json_data = RouteAccountEngine.export_json(batch)
            st.download_button("📋 JSON", json_data, "route_results.json", "application/json", use_container_width=True, key="dl_json_batch")
        with ec3:
            txt_data = RouteAccountEngine.export_txt(batch)
            st.download_button("📝 TXT", txt_data, "route_results.txt", "text/plain", use_container_width=True, key="dl_txt_batch")

# ─── TAB 6: Credit Score ────────────────────────────────────

with tab6:
    st.markdown("## 📊 Motor de Credit Score")
    st.markdown("Estima el credit score de un perfil basado en sus instituciones financieras y datos de brechas")

    cs_input = st.text_input(
        "Email o nombre para buscar score",
        placeholder="email@domain.com o John Smith",
    )

    if st.button("📊 Calcular Score", type="primary"):
        if cs_input:
            with st.spinner("Buscando datos financieros..."):
                result = engine.full_search(cs_input, "auto")
                if result.profiles:
                    for p in result.profiles:
                        cs = p.raw_data.get("credit_score") if p.raw_data else None
                        grade = p.raw_data.get("credit_grade") if p.raw_data else None
                        if cs:
                            grade_class = "score-excellent" if cs >= 740 else "score-good" if cs >= 670 else "score-fair" if cs >= 580 else "score-poor"
                            st.markdown(f'<div class="score-badge {grade_class}" style="font-size:3rem;">📊 {cs} — {grade}</div>', unsafe_allow_html=True)
                            st.markdown(f"**Instituciones:** {', '.join(i.institution for i in p.institutions)}")
                            st.markdown(f"**Basado en:** {len(p.institutions)} instituciones, {len(p.breach_sources)} brechas")
                        else:
                            st.warning("No se pudo determinar el score con los datos disponibles")
                else:
                    st.warning("No se encontraron datos financieros")

# ─── TAB 4B: Validador de Cuentas ───────────────────────────

with tab4:
    st.markdown("## 🏦 Validador de Cuentas Bancarias")
    st.markdown(
        "Valida **routing numbers**, **números de tarjeta** y **cuentas bancarias**. "
        "Verifica checksum ABA, algoritmo de Luhn, BIN lookup y reglas de formato."
    )

    validator = AccountValidator()

    val_mode = st.radio(
        "Modo",
        ["🔍 Validar Individual", "📁 Lote (textarea)", "📄 Subir CSV"],
        horizontal=True,
        key="val_mode",
    )

    if val_mode.startswith("🔍"):
        val_input = st.text_input(
            "Dato a validar",
            placeholder="021000021 (routing)  •  4532015112030367 (card)  •  123-45-6789 (SSN)",
            key="val_single",
        )
        val_type = st.selectbox("Tipo", ["auto", "routing", "card", "account", "ssn"], key="val_single_type")

        if st.button("⚡ VALIDAR", type="primary", use_container_width=True, key="btn_val_single"):
            if val_input.strip():
                with st.spinner("Validando..."):
                    v = validator.validate(val_input, val_type)
                    st.session_state["val_last"] = v

                    if HAS_TRACKER and st.session_state.get("tracker_user"):
                        log_activity(st.session_state.tracker_user["id"], "validate", {
                            "input": val_input[:50],
                            "type": v.input_type,
                            "status": v.status,
                        })

        if "val_last" in st.session_state:
            v = st.session_state["val_last"]
            st.markdown("---")

            # Status badge
            status_colors = {"valid": "#00c853", "invalid": "#e94560", "suspicious": "#ffd700", "unknown": "#888"}
            status_emojis = {"valid": "✅", "invalid": "❌", "suspicious": "⚠️", "unknown": "❓"}
            sc = status_colors.get(v.status, "#888")
            se = status_emojis.get(v.status, "?")
            st.markdown(f'<div style="background:{sc}22;border:2px solid {sc};border-radius:12px;padding:20px;text-align:center;">'
                        f'<span style="font-size:2rem;">{se}</span><br>'
                        f'<span style="font-size:1.5rem;font-weight:800;color:{sc};">{v.status.upper()}</span><br>'
                        f'<span style="color:#888;">{v.status_detail}</span></div>',
                        unsafe_allow_html=True)

            # Metrics
            vc1, vc2, vc3, vc4 = st.columns(4)
            vc1.metric("Tipo", v.input_type.upper())
            vc2.metric("Confianza", f"{v.confidence:.0%}")
            vc3.metric("Checks OK", len(v.checks_passed))
            vc4.metric("Fallas", len(v.checks_failed))

            # Routing info
            if v.routing_number:
                st.markdown(f"**🔢 Routing:** `{v.routing_number}`")
                if v.routing_bank:
                    st.markdown(f"**🏦 Banco:** {v.routing_bank}")
                st.markdown(f"**📊 Estado:** {'🟢 Activo' if v.routing_active else '🔴 Inactivo/desconocido'}")

            # Card info
            if v.card_network:
                st.markdown(f"**💳 Red:** {v.card_network}")
            if v.card_bank:
                st.markdown(f"**🏦 Banco:** {v.card_bank}")
            if v.card_type:
                st.markdown(f"**📋 Tipo:** {v.card_type}")
            if v.card_last4:
                st.markdown(f"**🔢 Últimos 4:** `{v.card_last4}`")

            # SSN info
            if v.ssn_area:
                st.markdown(f"**🔑 SSN:** `{v.ssn_area}-{v.ssn_group}-{v.ssn_serial}`")

            # Account info
            if v.account_masked:
                st.markdown(f"**💼 Cuenta:** `{v.account_masked}` ({v.account_length} dígitos)")

            # Checks
            if v.checks_passed:
                with st.expander(f"✅ Checks pasados ({len(v.checks_passed)})"):
                    for c in v.checks_passed:
                        st.markdown(f"- ✅ {c}")
            if v.checks_failed:
                with st.expander(f"❌ Checks fallidos ({len(v.checks_failed)})"):
                    for c in v.checks_failed:
                        st.markdown(f"- ❌ {c}")
            if v.warnings:
                with st.expander(f"⚠️ Advertencias ({len(v.warnings)})"):
                    for w in v.warnings:
                        st.markdown(f"- ⚠️ {w}")

    elif val_mode.startswith("📁"):
        st.markdown("### 📁 Validación Masiva")
        st.caption("Un routing, tarjeta o cuenta por línea. El motor detecta el tipo.")

        val_batch_text = st.text_area(
            "Datos a validar",
            height=250,
            placeholder="021000021\n4532015112030367\n123-45-6789\n9876543210",
            key="val_batch_text",
        )

        if st.button("⚡ VALIDAR LOTE", type="primary", use_container_width=True, key="btn_val_batch"):
            if val_batch_text.strip():
                items = AccountValidator.parse_batch_input(val_batch_text)
                with st.spinner(f"Validando {len(items)} items..."):
                    batch = validator.validate_batch(items)
                    st.session_state["val_batch"] = batch

        if "val_batch" in st.session_state:
            batch = st.session_state["val_batch"]
            st.markdown(f"### 📊 Resultados: {batch.total} items — ✅ {batch.valid} válidos | ❌ {batch.invalid} inválidos | ⚠️ {batch.suspicious} sospechosos")

            rows = []
            for r in batch.results:
                rows.append({
                    "Input": r.input_value[:30],
                    "Tipo": r.input_type,
                    "Estado": r.status.upper(),
                    "Confianza": f"{r.confidence:.0%}",
                    "Banco": r.card_bank or r.routing_bank or "",
                    "Red": r.card_network or "",
                    "Detalle": r.status_detail[:60],
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)

            # Export
            st.markdown("### 📥 Exportar")
            vec1, vec2 = st.columns(2)
            with vec1:
                csv_d = AccountValidator.export_csv(batch)
                st.download_button("📄 CSV", csv_d, "validation_results.csv", "text/csv", use_container_width=True)
            with vec2:
                json_d = AccountValidator.export_json(batch)
                st.download_button("📋 JSON", json_d, "validation_results.json", "application/json", use_container_width=True)

    elif val_mode.startswith("📄"):
        st.markdown("### 📄 Subir CSV")
        st.caption("Columnas esperadas: any column with routing/card/account/ssn data")
        val_file = st.file_uploader("Sube CSV", type=["csv"], key="val_file")
        if val_file:
            try:
                df = pd.read_csv(val_file)
                st.dataframe(df.head(5), use_container_width=True)

                # Try to find valid columns
                all_vals = []
                for col in df.columns:
                    for val in df[col].dropna().astype(str):
                        clean = re.sub(r'[^0-9-]', '', val)
                        if 4 <= len(clean) <= 19:
                            all_vals.append((clean, "auto"))

                if all_vals:
                    st.info(f"📋 {len(all_vals)} valores detectados para validación")
                    if st.button("⚡ VALIDAR CSV", type="primary", key="btn_val_csv"):
                        with st.spinner(f"Validando {len(all_vals)} items..."):
                            batch = validator.validate_batch(all_vals[:500])  # Limit
                            st.session_state["val_batch"] = batch
                            st.rerun()
                else:
                    st.warning("No se detectaron datos válidos en el CSV")
            except Exception as e:
                st.error(f"Error: {e}")

# ─── TAB 5: Credit Card Analyzer ───────────────────────────

with tab5:
    st.markdown("## 💳 Credit Card Analyzer")
    st.markdown(
        "Análisis completo de tarjetas de crédito/débito: BIN lookup, red de pago, "
        "banco emisor, tipo, nivel, país y validación Luhn."
    )

    card_analyzer = CardAnalyzer()
    card_plaid = PlaidEngine()

    card_mode = st.radio(
        "Modo",
        ["🔍 Analizar Individual", "📁 Lote (textarea)", "📄 Subir CSV"],
        horizontal=True,
        key="card_mode",
    )

    if card_mode.startswith("🔍"):
        st.markdown("### 🔍 Análisis Individual")
        card_input = st.text_input(
            "Número de tarjeta",
            placeholder="4532015112030367  •  5424003511111111  •  374245455400126",
            key="card_single",
        )

        if st.button("⚡ ANALIZAR TARJETA", type="primary", use_container_width=True, key="btn_card_single"):
            if card_input.strip():
                with st.spinner("Analizando tarjeta..."):
                    card_result = card_analyzer.analyze(card_input)
                    st.session_state["card_last"] = card_result

                    if HAS_TRACKER and st.session_state.get("tracker_user"):
                        log_activity(st.session_state.tracker_user["id"], "card_analyze", {
                            "card": card_result.card_masked,
                            "network": card_result.network,
                            "status": card_result.status,
                        })

        if "card_last" in st.session_state:
            c = st.session_state["card_last"]
            st.markdown("---")

            # Network banner
            network_colors = {
                "Visa": "#1A1F71", "Mastercard": "#EB001B", "Amex": "#006FCF",
                "Discover": "#FF6000", "Diners": "#004080", "JCB": "#0066B2",
                "UnionPay": "#E21836",
            }
            nc = network_colors.get(c.network, '#333')
            net_name = c.network or 'Desconocida'
            st.markdown(
                '<div style="background:' + nc + ';border-radius:12px;padding:20px;margin-bottom:16px;">'
                '<span style="font-size:2.5rem;">' + c.network_icon + '</span>'
                '<span style="font-size:1.5rem;font-weight:800;color:#fff;margin-left:12px;">' + net_name + '</span>'
                '<span style="color:rgba(255,255,255,0.8);margin-left:12px;">' + c.card_masked + '</span>'
                '</div>',
                unsafe_allow_html=True,
            )

            # Status badge
            status_colors = {"valid": "#00c853", "invalid": "#e94560", "suspicious": "#ffd700"}
            sc = status_colors.get(c.status, '#888')
            status_emojis = {'valid': '✅', 'invalid': '❌', 'suspicious': '⚠️'}
            status_icon = status_emojis.get(c.status, '?')
            status_upper = c.status.upper()
            st.markdown(
                '<div style="background:' + sc + '22;border:2px solid ' + sc + ';border-radius:12px;padding:16px;text-align:center;margin-bottom:16px;">'
                '<span style="font-size:1.5rem;">' + status_icon + '</span>'
                '<span style="font-size:1.3rem;font-weight:800;color:' + sc + ';margin-left:8px;">' + status_upper + '</span>'
                '<span style="color:#888;margin-left:12px;">' + c.status_detail + '</span>'
                '</div>',
                unsafe_allow_html=True,
            )

            # Info grid
            ig1, ig2, ig3, ig4 = st.columns(4)
            ig1.metric("🏦 Banco Emisor", c.issuing_bank or "No identificado")
            ig2.metric("📋 Tipo", f"{c.card_type} {c.card_level}".strip())
            ig3.metric("🌍 País", c.bank_country_name or c.bank_country or "")
            ig4.metric("🎯 Confianza", f"{c.confidence:.0%}")

            # Validation checks
            st.markdown("### 📋 Checks de Validación")
            cv1, cv2, cv3 = st.columns(3)
            cv1.metric("✅ Luhn", "Válido" if c.is_valid_luhn else "Inválido")
            cv2.metric("📏 Longitud", "OK" if c.is_valid_length else "Inválida")
            cv3.metric("🔢 BIN", "Identificado" if c.is_valid_bin else "No encontrado")

            if c.checks_passed:
                with st.expander(f"✅ Checks pasados ({len(c.checks_passed)})"):
                    for ch in c.checks_passed:
                        st.markdown(f"- ✅ {ch}")
            if c.checks_failed:
                with st.expander(f"❌ Checks fallidos ({len(c.checks_failed)})"):
                    for ch in c.checks_failed:
                        st.markdown(f"- ❌ {ch}")
            if c.warnings:
                with st.expander(f"⚠️ Advertencias ({len(c.warnings)})"):
                    for w in c.warnings:
                        st.markdown(f"- ⚠️ {w}")

    elif card_mode.startswith("📁"):
        st.markdown("### 📁 Análisis Masivo")
        st.caption("Un número de tarjeta por línea")

        card_batch_text = st.text_area(
            "Números de tarjeta",
            height=200,
            placeholder="4532015112030367\n5424003511111111\n374245455400126\n6011000990139424",
            key="card_batch_text",
        )

        if st.button("⚡ ANALIZAR LOTE", type="primary", use_container_width=True, key="btn_card_batch"):
            if card_batch_text.strip():
                cards = CardAnalyzer.parse_batch_input(card_batch_text)
                with st.spinner(f"Analizando {len(cards)} tarjetas..."):
                    batch = card_analyzer.analyze_batch(cards)
                    st.session_state["card_batch"] = batch

        if "card_batch" in st.session_state:
            batch = st.session_state["card_batch"]

            # Summary
            st.markdown(f"### 📊 Resumen: {batch.total} tarjetas")
            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric("✅ Válidas", batch.valid)
            sm2.metric("❌ Inválidas", batch.invalid)
            sm3.metric("📡 Redes", len(batch.networks))
            sm4.metric("🏦 Bancos", len(batch.banks))

            # Network distribution
            if batch.networks:
                st.markdown("**Distribución por Red:**")
                for net, cnt in sorted(batch.networks.items(), key=lambda x: -x[1]):
                    bar_len = int(cnt / max(batch.networks.values()) * 30) if batch.networks else 0
                    st.markdown(f"`{net}` {'█' * bar_len} {cnt}")

            # Table
            rows = []
            for r in batch.results:
                rows.append({
                    "Tarjeta": r.card_masked,
                    "Red": f"{r.network_icon} {r.network}",
                    "Banco": r.issuing_bank or "",
                    "Tipo": r.card_type,
                    "Nivel": r.card_level,
                    "País": r.bank_country,
                    "Estado": r.status.upper(),
                    "Luhn": "✅" if r.is_valid_luhn else "❌",
                    "BIN": "✅" if r.is_valid_bin else "❌",
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)

            # Export
            st.markdown("### 📥 Exportar")
            cec1, cec2 = st.columns(2)
            with cec1:
                csv_d = CardAnalyzer.export_csv(batch)
                st.download_button("📄 CSV", csv_d, "card_analysis.csv", "text/csv", use_container_width=True)
            with cec2:
                json_d = CardAnalyzer.export_json(batch)
                st.download_button("📋 JSON", json_d, "card_analysis.json", "application/json", use_container_width=True)

    elif card_mode.startswith("📄"):
        st.markdown("### 📄 Subir CSV")
        st.caption("Columna con números de tarjeta (auto-detecta)")
        card_file = st.file_uploader("Sube CSV", type=["csv"], key="card_file")
        if card_file:
            try:
                df = pd.read_csv(card_file)
                st.dataframe(df.head(5), use_container_width=True)

                all_cards = []
                for col in df.columns:
                    for val in df[col].dropna().astype(str):
                        clean = re.sub(r'[^0-9]', '', val)
                        if 13 <= len(clean) <= 19 and clean.isdigit():
                            all_cards.append(clean)

                if all_cards:
                    st.info(f"📋 {len(all_cards)} números de tarjeta detectados")
                    if st.button("⚡ ANALIZAR CSV", type="primary", key="btn_card_csv"):
                        with st.spinner(f"Analizando {len(all_cards)} tarjetas..."):
                            batch = card_analyzer.analyze_batch(all_cards[:200])
                            st.session_state["card_batch"] = batch
                            st.rerun()
                else:
                    st.warning("No se detectaron números de tarjeta en el CSV")
            except Exception as e:
                st.error(f"Error: {e}")

# ─── TAB 6: Exportar ────────────────────────────────────────

with tab6:
    st.markdown("## 📥 Exportar Resultados")
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 CSV", use_container_width=True):
                path = exporter.export_csv(result)
                st.success(f"✅ {path}")
        with col2:
            if st.button("📋 JSON", use_container_width=True):
                path = exporter.export_json(result)
                st.success(f"✅ {path}")
        with col3:
            if st.button("📝 TXT", use_container_width=True):
                path = exporter.export_txt(result)
                st.success(f"✅ {path}")
    else:
        st.info("Realiza una búsqueda primero")

    # Reportes
    st.markdown("---")
    st.markdown("### 📂 Reportes")
    if os.path.exists("output/reports"):
        for f in sorted(os.listdir("output/reports"), reverse=True)[:10]:
            st.markdown(f"📄 {f}")

# ─── TAB 8: Setup & Ayuda ──────────────────────────────────

with tab8:
    st.markdown("## 📖 Setup & Ayuda Completa")
    st.markdown("Configura todas las APIs y aprende a usar la herramienta")

    # ── Estado de APIs ──
    st.markdown("### 🔑 Estado de las APIs")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        lc_ok = bool(st.session_state.get("lc_key"))
        st.markdown(f"{'✅' if lc_ok else '❌'} **LeakCheck Pro**")
        st.caption("$10/mes — leakcheck.io")
    with col2:
        dh_ok = bool(st.session_state.get("dh_key"))
        st.markdown(f"{'✅' if dh_ok else '❌'} **DeHashed**")
        st.caption("$20/mes — dehashed.com")
    with col3:
        ix_ok = bool(st.session_state.get("ix_key"))
        st.markdown(f"{'✅' if ix_ok else '❌'} **IntelligenceX**")
        st.caption("$50/mes — intelx.io")
    with col4:
        sb_ok = bool(st.session_state.get("sb_key"))
        st.markdown(f"{'✅' if sb_ok else '❌'} **Snusbase**")
        st.caption("$30/mes — snusbase.com")

    st.markdown("---")

    # ── Guías por Plataforma ──
    st.markdown("### 📋 Guías de Setup por Plataforma")

    with st.expander("🔑 LeakCheck Pro — $10/mes (MÍNIMO RECOMENDADO)", expanded=True):
        st.markdown("""
**Qué hace:** Busca en 15B+ registros de brechas. Soporta SSN, email, phone, address.

**Cómo obtener:**
1. Ve a [leakcheck.io](https://leakcheck.io)
2. Click **Sign Up** → Crea cuenta
3. Ve a **Dashboard** → **Subscription**
4. Selecciona plan **Pro** ($10)
5. Paga con tarjeta o crypto
6. Ve a **Dashboard** → **API Keys** → **Create Key**
7. Copia la key y pégala en el Sidebar

**Capacidades:**
- SSN → Nombre, DOB, Dirección, Teléfono, Email
- Nombre → SSN (si está en brechas)
- Dirección → SSN + residentes
- Email → passwords, instituciones
""")
        st.link_button("🔗 Obtener LeakCheck Pro", "https://leakcheck.io")

    with st.expander("🔑 DeHashed — $20/mes (EL MÁS COMPLETO)"):
        st.markdown("""
**Qué hace:** Motor de búsqueda en 10B+ registros. El más completo para SSN lookup.

**Cómo obtener:**
1. Ve a [dehashed.com](https://www.dehashed.com)
2. Click **Sign Up** → Crea cuenta
3. Ve a **Dashboard** → **Subscription**
4. Selecciona plan **Basic** ($20)
5. Paga con tarjeta
6. Ve a **Settings** → **API Access**
7. Copia tu API Key (formato: dhash_xxx)
8. Pégala en el Sidebar

**Capacidades:**
- SSN → Todos los campos asociados
- Nombre + Estado → SSN
- Dirección → SSN + residentes
- Phone → SSN + email
- VIN → vehicle info + owner
""")
        st.link_button("🔗 Obtener DeHashed", "https://www.dehashed.com")

    with st.expander("🔑 IntelligenceX — $50/mes (DARK WEB)"):
        st.markdown("""
**Qué hace:** Búsqueda en dark web, breaches, paste sites. Los más profundo.

**Cómo obtener:**
1. Ve a [intelx.io](https://intelx.io)
2. Click **Sign Up** → Crea cuenta
3. Ve a **Dashboard** → **Subscription**
4. Selecciona plan **Explorer** ($50)
5. Paga con tarjeta o crypto
6. Ve a **Settings** → **API Keys** → **Generate Key**
7. Copia tu API Key (formato: UUID)
8. Pégala en el Sidebar

**Capacidades:**
- Término libre → cualquier texto en breaches
- SSN → archivos filtrados en dark web
- Nombre → documentos filtrados
- Búsqueda más lenta pero más profunda
""")
        st.link_button("🔗 Obtener IntelligenceX", "https://intelx.io")

    with st.expander("🔑 Snusbase — $30/mes (STEALER LOGS)"):
        st.markdown("""
**Qué hace:** Base de datos de stealer logs (malware que roba credenciales).

**Cómo obtener:**
1. Ve a [snusbase.com](https://snusbase.com)
2. Click **Sign Up** → Crea cuenta
3. Ve a **Dashboard** → **Subscription**
4. Selecciona plan **Basic** ($30)
5. Paga con tarjeta o crypto
6. Ve a **Settings** → **API**
7. Copia tu API Key (formato: snus_xxx)
8. Pégala en el Sidebar

**Capacidades:**
- Email → passwords, cookies, tokens
- Password → otros emails
- Token → sesión activa robada
""")
        st.link_button("🔗 Obtener Snusbase", "https://snusbase.com")

    st.markdown("---")

    # ── Guías de Uso por Pestaña ──
    st.markdown("### 🎯 Guías de Uso Completas")

    with st.expander("🗺️ Route & Account Finder — Motor Unificado", expanded=True):
        st.markdown("""
**El motor más potente de la herramienta.** Acepta CUALQUIER campo y cruza múltiples fuentes.

### Modos de Uso
- **🔍 Individual:** Un campo → motor extrae todo lo asociado
- **📁 Lote:** Múltiples campos en textarea → procesamiento paralelo (hasta 10 hilos)
- **📄 CSV/Excel:** Subes archivo → auto-detecta columnas y procesa

### Tipos de Campo (detectados automáticamente)
| Campo | Ejemplo | Qué extrae |
|-------|---------|------------|
| 📧 email | user@domain.com | passwords, instituciones, breach data |
| 📱 phone | +1-212-555-1234 | email, nombre, SSN, bancos |
| 🔑 ssn | 123-45-6789 | identidad completa, brechas, credit score |
| 🏠 address | 1206 Laurel Ln TX | residentes, SSN, cuentas, bancos |
| 👤 name | John Smith | SSN, emails, teléfonos, dirección |
| 📅 dob | 01/15/1990 | perfils cruzados con todos los campos |
| 👤 username | @john | emails, breach data |
| 🌐 domain | bankofamerica.com | emails del dominio, breach data |

### Qué Entrega por Cada Búsqueda
- ✅ Emails, teléfonos, nombres, direcciones
- ✅ SSN, fecha de nacimiento
- ✅ Bancos/instituciones detectadas (15+)
- ✅ Cuentas, tarjetas de crédito
- ✅ Passwords expuestos
- ✅ Credit Score estimado
- ✅ Fuentes de brechas
- ✅ Risk Score (0-100)
- ✅ Exportación CSV/JSON/TXT

### Ejemplo Rápido
1. Pestaña **🗺️ Route & Account Finder**
2. Selecciona **🔍 Individual**
3. Ingresa: `1206 Laurel Ln Richardson, TX 75080`
4. Tipo: `auto` (auto-detecta)
5. Click **⚡ EXTRAER DATOS**
6. Ve: emails, passwords, SSN, bancos, tarjetas, credit score
""")

    with st.expander("🏦 Validador de Cuentas Bancarias"):
        st.markdown("""
**Valida routing numbers, tarjetas y cuentas bancarias** con algoritmos de verificación.

### Qué Valida
| Tipo | Algoritmo | Qué verifica |
|------|-----------|-------------|
| 🔢 Routing Number | Checksum ABA | Formato 9 dígitos + banco conocido |
| 💳 Tarjeta de Crédito | Luhn + BIN | Número válido + banco emisor |
| 💼 Cuenta Bancaria | Formato | Longitud, dígitos, patrones |
| 🔑 SSN | Reglas oficiales | Área (001-899), Grupo, Serial |

### Modos de Uso
- **🔍 Individual:** Un dato a la vez
- **📁 Lote:** Múltiples datos en textarea
- **📄 CSV:** Subir archivo con auto-detección

### Base de Datos
- 50+ routing numbers de bancos US
- 60+ BINs de bancos y fintechs
- Reglas SSN oficiales de la SSA

### Ejemplo Rápido
1. Pestaña **🏦 Validador de Cuentas**
2. Selecciona **🔍 Individual**
3. Ingresa: `021000021` (routing de Chase)
4. Click **⚡ VALIDAR**
5. Ve: ✅ Válido, banco: JPMorgan Chase, checksum OK
""")

    with st.expander("💳 Credit Card Analyzer — Análisis de Tarjetas"):
        st.markdown("""
**Motor completo de análisis de tarjetas de crédito/débito.**

### Qué Analiza
| Campo | Qué Entrega |
|-------|------------|
| 🔢 BIN/IIN | Banco emisor (100+ bancos) |
| 🌐 Red | Visa, Mastercard, Amex, Discover, Diners, JCB, UnionPay |
| 🏦 Banco | Nombre del banco emisor |
| 🌍 País | País de emisión (US, MX, ES, JP, CN, etc.) |
| 📋 Tipo | Crédito, Débito, Prepago |
| 🏆 Nivel | Classic, Gold, Platinum, Signature, Infinite |
| ✅ Luhn | Validación numérica |
| 📏 Longitud | Correcta para la red |

### Modos de Uso
- **🔍 Individual:** Analizar una tarjeta
- **📁 Lote:** Analizar múltiples tarjetas
- **📄 CSV:** Subir archivo con columnas de tarjetas

### Base de Datos
- 200+ BINs de bancos internacionales
- 7 redes de pago: Visa, MC, Amex, Discover, Diners, JCB, UnionPay
- 15+ países de emisión

### Ejemplo Rápido
1. Pestaña **💳 Credit Card Analyzer**
2. Selecciona **🔍 Individual**
3. Ingresa: `4532015112030367`
4. Click **⚡ ANALIZAR TARJETA**
5. Ve: 🟦 Visa — Chase — Gold — US — ✅ Válida
""")

    with st.expander("🔐 Búsqueda por SSN"):
        st.markdown("""
1. Pestaña **🔐 SSN Lookup**
2. Sub-pestaña **SSN → Identidad**
3. Ingresa: `123-45-6789`
4. Click **⚡ Buscar por SSN**
5. Ve: nombre, DOB, dirección, teléfono, email, brechas

**Para Reverse Lookup (Nombre → SSN):**
1. Sub-pestaña **Nombre/Dirección → SSN**
2. Ingresa nombre o dirección
3. Click **⚡ Buscar SSN**
""")

    with st.expander("📊 Credit Score"):
        st.markdown("""
1. Pestaña **📊 Credit Score**
2. Ingresa email o nombre
3. Click **📊 Calcular Score**
4. Ve: score estimado (300-850) + grade

**Nota:** El score es una estimación basada en las instituciones detectadas.
""")

    with st.expander("📁 Búsqueda por Lote"):
        st.markdown("""
**Procesamiento masivo de consultas:**

1. Ingresa múltiples campos (uno por línea)
2. Selecciona hilos paralelos (1-10)
3. Click **⚡ Ejecutar Lote**
4. Ve: tabla resumen + exportación CSV/JSON

**Soporta:** addresses, emails, phones, SSNs, nombres mixtos
""")

    st.markdown("---")

    # ── Plaid Setup ──
    st.markdown("### 🏦 Integración Plaid (Balance y Estado de Cuentas)")
    st.markdown("""
**Plaid** permite verificar si una cuenta bancaria está activa y tiene fondos.

### Setup (5 minutos)
1. Ve a **https://dashboard.plaid.com/signup**
2. Crea cuenta gratuita (sandbox = 100 requests/mes gratis)
3. Ve a **Team Settings → Keys**
4. Copia **Client ID** y **Secret**
5. En Streamlit Cloud: Settings → Secrets → Agrega:
```
PLAID_CLIENT_ID = "tu_client_id"
PLAID_SECRET = "tu_secret"
PLAID_ENV = "sandbox"
```

### Modos
- **sandbox** (gratis): Datos simulados para testing
- **development** ($0.30/request): Datos reales limitados
- **production** ($0.30/request): Datos reales completos

### Qué Verifica
- ✅ Balance disponible y actual
- ✅ Estado de la cuenta (activa/inactiva)
- ✅ Tipo de cuenta (checking/savings/credit)
- ✅ Routing y account number reales (vía Plaid Auth)
- ✅ Datos del titular (vía Plaid Identity)
""")

    st.markdown("---")

    # ── Costos ──
    st.markdown("### 💰 Planes y Costos")
    st.markdown("""
| Plataforma | Plan Mínimo | Plan Recomendado |
|------------|-------------|------------------|
| LeakCheck Pro | $10/mes | $25/mes |
| DeHashed | $20/mes | $50/mes |
| IntelligenceX | $50/mes | $100/mes |
| Snusbase | $30/mes | $60/mes |
| Plaid | Gratis (sandbox) | $0.30/request |

**Para empezar:** Solo necesitas LeakCheck Pro ($10/mes)
**Máximo poder:** Todas las APIs + Plaid ($110-235/mes)
""")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#555;'>⚡ Financial OSINT PRO v3.0 — Motor de inteligencia financiera multi-fuente con Route Finder, Validator y Card Analyzer</div>", unsafe_allow_html=True)
