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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Búsqueda Universal",
    "🔐 SSN Lookup",
    "📁 Lote Masivo",
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

# ─── TAB 3: Lote (Lote Masivo) ─────────────────────────────

with tab2:
    st.markdown("## 📁 Búsqueda Masiva por Lote")
    lote = st.text_area(
        "Una entrada por línea (direcciones, emails, teléfonos)",
        height=200,
        placeholder="1206 Laurel Ln Richardson, TX 75080\nuser@email.com\n+1-212-555-1234",
    )

    if st.button("⚡ Ejecutar Lote", type="primary", use_container_width=True):
        if lote.strip():
            queries = [q.strip() for q in lote.strip().split("\n") if q.strip()]
            progress = st.progress(0)
            results_list = []
            for i, q in enumerate(queries):
                r = engine.full_search(q, "auto", institutions=selected_inst)
                results_list.append(r)
                progress.progress((i + 1) / len(queries))
            st.session_state["lote_results"] = results_list
            st.success(f"✅ {len(results_list)} consultas procesadas")

    if "lote_results" in st.session_state:
        rows = []
        for r in st.session_state["lote_results"]:
            for p in r.profiles:
                cs = p.raw_data.get("credit_score", "") if p.raw_data else ""
                rows.append({
                    "Query": r.request.query,
                    "Nombre": p.name,
                    "Emails": len(p.emails),
                    "Teléfonos": len(p.phones),
                    "SSN": "✅" if p.ssn else "❌",
                    "Passwords": len(p.passwords),
                    "Tarjetas": len(p.credit_cards),
                    "Credit Score": cs,
                    "Instituciones": ", ".join(i.institution for i in p.institutions),
                    "Risk": p.risk_score,
                })
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

# ─── TAB 4: Credit Score ────────────────────────────────────

with tab4:
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

# ─── TAB 5: Exportar ────────────────────────────────────────

with tab5:
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

# ─── TAB 6: Setup & Ayuda ──────────────────────────────────

with tab6:
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

    # ── Cómo Usar ──
    st.markdown("### 🎯 Cómo Usar la Herramienta")

    with st.expander("🔍 Búsqueda por Dirección"):
        st.markdown("""
1. Pestaña **🔍 Búsqueda Universal**
2. Ingresa: `1206 Laurel Ln Richardson, TX 75080`
3. Tipo: `auto` o `address`
4. Click **⚡ BUSCAR**
5. Ve: emails, passwords, SSN, tarjetas, credit score, instituciones
""")

    with st.expander("🔐 Búsqueda por SSN"):
        st.markdown("""
1. Pestaña **🔐 SSN Lookup**
2. Sub-pestaña **SSN → Identidad**
3. Ingresa: `123-45-6789`
4. Click **⚡ Buscar por SSN**
5. Ve: nombre, DOB, dirección, teléfono, email, brechas
""")

    with st.expander("🔄 Reverse Lookup (Nombre → SSN)"):
        st.markdown("""
1. Pestaña **🔐 SSN Lookup**
2. Sub-pestaña **Nombre/Dirección → SSN**
3. Ingresa: `John Smith` o dirección
4. Tipo: `name` o `address`
5. Click **⚡ Buscar SSN**
6. Ve: SSN asociado (si existe en brechas)
""")

    with st.expander("📊 Credit Score"):
        st.markdown("""
1. Pestaña **📊 Credit Score**
2. Ingresa email o nombre
3. Click **📊 Calcular Score**
4. Ve: score estimado (300-850) + grade

**Nota:** El score es una estimación basada en las instituciones detectadas.
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

**Para empezar:** Solo necesitas LeakCheck Pro ($10/mes)
**Máximo poder:** Todas las APIs ($110-235/mes)
""")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#555;'>⚡ Financial OSINT PRO v2.0 — Motor de inteligencia financiera multi-fuente</div>", unsafe_allow_html=True)
