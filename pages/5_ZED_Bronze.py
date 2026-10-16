import streamlit as st
import json
import io
import os
import zipfile
from pathlib import Path
from datetime import date, datetime

import yaml

try:
    from jinja2 import Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# ── Paths ────────────────────────────────────────────────────────
BASE    = Path(__file__).parent.parent
CFG     = BASE / "zed_config" / "config.yaml"
UNITS   = BASE / "units"

# ── Config loader ────────────────────────────────────────────────
@st.cache_data
def load_config():
    with open(CFG) as f:
        return yaml.safe_load(f)

# ── Unit data helpers ─────────────────────────────────────────────
def unit_path(udyam: str) -> Path:
    safe = udyam.strip().replace("/", "-").replace(" ", "_")
    p = UNITS / safe
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_unit(udyam: str, data: dict):
    with open(unit_path(udyam) / "data.json", "w") as f:
        json.dump(data, f, indent=2, default=str)

def load_unit(udyam: str) -> dict:
    f = unit_path(udyam) / "data.json"
    return json.loads(f.read_text()) if f.exists() else {}

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(page_title="ZED Bronze Evidence Kit", page_icon="🏅", layout="wide")

# ── CSS: larger touch targets for phone use ───────────────────────
st.markdown("""
<style>
  div[data-testid="stButton"] > button { min-height: 2.6rem; font-size: 1rem; }
  div[data-testid="stTextInput"] input { font-size: 1rem; }
  .step-done  { color: #1a7f5a; font-weight: 600; }
  .step-now   { color: #d97706; font-weight: 600; }
  .step-later { color: #9ca3af; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
def main():
    cfg = load_config()
    UNITS.mkdir(exist_ok=True)

    # Initialise session state
    for k, v in [("zed_step", 0), ("zed_udyam", ""), ("zed_data", {}), ("org_roles", None)]:
        if k not in st.session_state:
            st.session_state[k] = v

    st.title("🏅 ZED Bronze Evidence Kit")
    st.caption("Total Impact · Nagpur MSME Programme")

    if st.session_state.zed_step == 0:
        screen_unit_selector(cfg)
        return

    render_progress(cfg)
    st.divider()

    step = st.session_state.zed_step
    if   step == 1: screen_step1(cfg)
    elif step == 2: screen_step2(cfg)
    elif step == 3: screen_step3(cfg)
    elif step == 4: screen_step4(cfg)
    elif step == 5: screen_step5(cfg)
    elif step == 6: screen_step6(cfg)
    elif step == 7: screen_step7(cfg)


# ════════════════════════════════════════════════════════════════
# PROGRESS BAR
# ════════════════════════════════════════════════════════════════
def render_progress(cfg):
    steps  = cfg["steps"]
    total  = len(steps)
    cur    = st.session_state.zed_step
    unit   = st.session_state.zed_data.get("unit_name") or st.session_state.zed_udyam

    st.progress(min(cur / total, 1.0))
    cols = st.columns(total)
    for i, s in enumerate(steps, 1):
        if   i < cur:  icon, cls = "✅", "step-done"
        elif i == cur: icon, cls = "▶", "step-now"
        else:          icon, cls = "○", "step-later"
        cols[i-1].markdown(f'<span class="{cls}">{icon} {s["short"]}</span>', unsafe_allow_html=True)

    st.caption(f"Unit: **{unit}**  ·  Udyam: {st.session_state.zed_udyam}")


# ════════════════════════════════════════════════════════════════
# UNIT SELECTOR (Step 0)
# ════════════════════════════════════════════════════════════════
def screen_unit_selector(cfg):
    st.subheader("Select or create a unit")
    tab_new, tab_resume = st.tabs(["New unit", "Resume existing unit"])

    with tab_new:
        udyam = st.text_input("Udyam Registration Number", placeholder="e.g. UDYAM-MH-00-0000001")
        if st.button("Start →", type="primary", use_container_width=True):
            if udyam.strip():
                st.session_state.zed_udyam = udyam.strip()
                st.session_state.zed_data  = load_unit(udyam.strip())
                st.session_state.zed_step  = 1
                st.rerun()
            else:
                st.error("Please enter a Udyam number to continue.")

        st.divider()
        st.caption("Or try the built-in demo:")
        if st.button("Load Demo — Demo Gears Pvt Ltd", use_container_width=True):
            st.session_state.zed_udyam = "DEMO-GEARS-001"
            st.session_state.zed_data  = cfg.get("demo_unit", {})
            st.session_state.zed_step  = 1
            st.rerun()

    with tab_resume:
        existing = sorted([d.name for d in UNITS.iterdir() if d.is_dir()]) if UNITS.exists() else []
        if existing:
            sel = st.selectbox("Select a saved unit", existing)
            if st.button("Resume →", type="primary", use_container_width=True):
                data = load_unit(sel)
                st.session_state.zed_udyam = sel
                st.session_state.zed_data  = data
                st.session_state.zed_step  = data.get("_last_step", 1)
                st.rerun()
        else:
            st.info("No saved units found. Create a new unit to get started.")


# ════════════════════════════════════════════════════════════════
# STEP 1 — BASIC UNIT DETAILS
# ════════════════════════════════════════════════════════════════
def screen_step1(cfg):
    d = st.session_state.zed_data
    st.subheader("Step 1 — Basic Unit Details")

    # ── Unit info ─────────────────────────────────────────────────
    st.markdown("#### Unit Information")
    c1, c2 = st.columns(2)
    with c1:
        unit_name    = st.text_input("Unit Name *",                    value=d.get("unit_name", ""))
        size_class   = st.selectbox("Size Class *", ["Micro", "Small", "Medium"],
                                    index=["Micro","Small","Medium"].index(d.get("size_class","Micro")))
        nic_code     = st.text_input("NIC Code", value=d.get("nic_code",""),
                                     help="National Industrial Classification code, e.g. 28991 for machinery")
    with c2:
        address      = st.text_area("Address *",       value=d.get("address",""),      height=120)

    c3, c4 = st.columns(2)
    with c3:
        main_products  = st.text_area("Main Products *",  value=d.get("main_products",""),
                                      height=80, placeholder="e.g. CNC machined components, castings")
    with c4:
        main_customers = st.text_area("Main Customers",  value=d.get("main_customers",""),
                                      height=80, placeholder="e.g. Bajaj Auto, Tier-1 auto suppliers")

    # ── Workforce ─────────────────────────────────────────────────
    st.markdown("#### Workforce")
    c5, c6, c7 = st.columns(3)
    with c5: men     = st.number_input("Male employees",   min_value=0, value=int(d.get("employees_men",0)))
    with c6: wom_emp = st.number_input("Female employees", min_value=0, value=int(d.get("employees_women",0)))
    with c7: shifts  = st.number_input("Number of shifts", min_value=1, max_value=3, value=int(d.get("shifts",1)))

    # ── Owner ─────────────────────────────────────────────────────
    st.markdown("#### Owner Details")
    c8, c9 = st.columns(2)
    with c8:
        owner_name = st.text_input("Owner / MD Name *", value=d.get("owner_name",""))
    with c9:
        st.markdown("**Enterprise category** *(affects ZED subsidy)*")
        women_owned = st.checkbox("Women-owned enterprise",    value=d.get("owned_by_women", False))
        sc_owned    = st.checkbox("SC-owned enterprise",       value=d.get("owned_by_sc",    False))
        st_owned    = st.checkbox("ST-owned enterprise",       value=d.get("owned_by_st",    False))

    # ── Licences ──────────────────────────────────────────────────
    st.markdown("#### Regulatory Compliance")
    st.caption("ZED Bronze scores Leadership partly on regulatory status. Flag any gaps now.")

    licences = d.get("licences", {})

    def licence_widget(key, label):
        saved = licences.get(key, {})
        with st.expander(label, expanded=(saved.get("has","No") == "No")):
            opts  = ["Yes", "No", "Not applicable"]
            has   = st.radio("Status", opts,
                             index=opts.index(saved.get("has","No")),
                             key=f"lic_{key}_has", horizontal=True)
            result = {"has": has}

            if has == "Yes":
                lc1, lc2 = st.columns(2)
                with lc1:
                    result["number"] = st.text_input("Licence / consent number",
                                                     value=saved.get("number",""), key=f"lic_{key}_num")
                with lc2:
                    try:
                        stored_exp = date.fromisoformat(saved.get("expiry", str(date.today())))
                    except (ValueError, TypeError):
                        stored_exp = date.today()
                    exp = st.date_input("Expiry date", value=stored_exp, key=f"lic_{key}_exp")
                    result["expiry"] = str(exp)
                    if exp < date.today():
                        st.error(f"⚠️ EXPIRED — renew before applying for ZED Bronze.")
                    elif (exp - date.today()).days < 90:
                        st.warning(f"⚠️ Expires in {(exp - date.today()).days} days — renew soon.")

                up = st.file_uploader("Upload document (PDF / image)",
                                      type=["pdf","jpg","jpeg","png"], key=f"lic_{key}_up")
                if up:
                    fp = unit_path(st.session_state.zed_udyam) / f"{key}_{up.name}"
                    fp.write_bytes(up.read())
                    result["file"] = str(fp)
                    st.success(f"Saved: {up.name}")
                elif saved.get("file"):
                    result["file"] = saved["file"]
                    st.caption(f"On file: {Path(saved['file']).name}")

            elif has == "No":
                st.warning(f"⚠️ Missing. Required for ZED Bronze leadership assessment.")
        return result

    licences["cte_cto"]  = licence_widget("cte_cto",  "Pollution Consent — CTE & CTO (MPCB)")
    licences["factory"]  = licence_widget("factory",  "Factory Licence")
    licences["fire_noc"] = licence_widget("fire_noc", "Fire NOC")
    licences["other"]    = licence_widget("other",    "Other licences (specify in notes below)")

    # ── Existing certifications ────────────────────────────────────
    st.markdown("#### Existing Certifications")
    cert_opts = ["ISO 9001", "ISO 14001", "ISO 45001", "IATF 16949", "Other"]
    existing_certs = st.multiselect("Certifications already held (if any)",
                                    cert_opts, default=d.get("existing_certs",[]))
    cert_files = d.get("cert_files", {})
    for cert in existing_certs:
        up = st.file_uploader(f"Upload {cert} certificate",
                              type=["pdf","jpg","jpeg","png"], key=f"cert_{cert}")
        if up:
            fp = unit_path(st.session_state.zed_udyam) / f"cert_{cert.replace(' ','_')}_{up.name}"
            fp.write_bytes(up.read())
            cert_files[cert] = str(fp)
            st.success(f"Saved: {up.name}")

    notes = st.text_area("Notes (other licences, observations)", value=d.get("notes",""), height=80)

    # ── Navigation ─────────────────────────────────────────────────
    st.divider()
    cs, cn = st.columns([1, 3])
    with cs:
        if st.button("Skip for now", use_container_width=True):
            st.session_state.zed_step = 2
            st.rerun()
    with cn:
        if st.button("Save and continue →", type="primary", use_container_width=True):
            errors = []
            if not unit_name.strip():  errors.append("Unit name is required.")
            if not owner_name.strip(): errors.append("Owner name is required.")
            if errors:
                for e in errors: st.error(e)
            else:
                updated = {
                    **d,
                    "unit_name": unit_name.strip(),
                    "udyam": st.session_state.zed_udyam,
                    "size_class": size_class,
                    "nic_code": nic_code,
                    "address": address,
                    "main_products": main_products,
                    "main_customers": main_customers,
                    "employees_men": men,
                    "employees_women": wom_emp,
                    "shifts": shifts,
                    "owner_name": owner_name.strip(),
                    "owned_by_women": women_owned,
                    "owned_by_sc": sc_owned,
                    "owned_by_st": st_owned,
                    "licences": licences,
                    "existing_certs": existing_certs,
                    "cert_files": cert_files,
                    "notes": notes,
                    "_last_step": 2,
                    "_updated": datetime.now().isoformat(),
                }
                st.session_state.zed_data = updated
                save_unit(st.session_state.zed_udyam, updated)
                st.success("Saved ✓")
                st.session_state.zed_step = 2
                st.rerun()


# ════════════════════════════════════════════════════════════════
# STEP 2 — ORG CHART
# ════════════════════════════════════════════════════════════════
def screen_step2(cfg):
    d         = st.session_state.zed_data
    unit_name = d.get("unit_name") or st.session_state.zed_udyam

    st.subheader("Step 2 — Organisation Chart")
    st.caption("ZED Bronze — Leadership parameter. Upload your existing chart or build one now.")

    tab_up, tab_build = st.tabs(["📎 Upload existing chart", "🔧 Build one now"])

    # ── Upload tab ────────────────────────────────────────────────
    with tab_up:
        up = st.file_uploader("Upload org chart (PDF, PNG or JPG)",
                              type=["pdf","png","jpg","jpeg"])
        if up:
            fp = unit_path(st.session_state.zed_udyam) / f"org_chart_upload_{up.name}"
            fp.write_bytes(up.read())
            d["org_chart_file"] = str(fp)
            st.session_state.zed_data = d
            save_unit(st.session_state.zed_udyam, d)
            st.success(f"Saved: {up.name}")
            if up.type.startswith("image"):
                st.image(up.getvalue())
        elif d.get("org_chart_file"):
            st.caption(f"On file: {Path(d['org_chart_file']).name}")

    # ── Build tab ─────────────────────────────────────────────────
    with tab_build:
        # Seed roles from config on first visit
        if st.session_state.org_roles is None:
            saved_roles = d.get("org_roles")
            st.session_state.org_roles = (
                saved_roles if saved_roles
                else [r.copy() for r in cfg.get("default_org_roles", [])]
            )

        roles = st.session_state.org_roles
        st.markdown("Pre-filled with common MSME roles. Edit, delete, or add as needed.")

        updated = []
        for i, role in enumerate(roles):
            desig_options = ["— (Top level)"] + [
                r.get("designation","") for j, r in enumerate(roles)
                if j != i and r.get("designation","").strip()
            ]
            cur_reports = role.get("reports_to", "— (Top level)")
            if cur_reports not in desig_options:
                cur_reports = "— (Top level)"

            with st.container(border=True):
                c1, c2, cdel = st.columns([2, 2, 0.3])
                with c1:
                    desig = st.text_input("Designation *", value=role.get("designation",""),
                                          key=f"desig_{i}")
                    name  = st.text_input("Name (optional)", value=role.get("name",""),
                                          key=f"name_{i}", placeholder="e.g. Rajesh Kumar")
                with c2:
                    reports = st.selectbox("Reports to", desig_options,
                                           index=desig_options.index(cur_reports),
                                           key=f"reports_{i}")
                    resp = st.text_area("Key responsibilities", value=role.get("responsibilities",""),
                                        key=f"resp_{i}", height=72)
                with cdel:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button("✕", key=f"del_{i}", help="Remove this role"):
                        roles.pop(i)
                        st.session_state.org_roles = roles
                        st.rerun()
                updated.append({"designation": desig, "name": name,
                                 "reports_to": reports, "responsibilities": resp})
        st.session_state.org_roles = updated

        if st.button("＋ Add role", use_container_width=False):
            st.session_state.org_roles.append(
                {"designation":"","name":"","reports_to":"— (Top level)","responsibilities":""})
            st.rerun()

        st.divider()

        # ── Generate org chart ─────────────────────────────────────
        st.markdown("**Generate outputs from the roles above**")
        gc1, gc2, gc3 = st.columns(3)

        with gc1:
            if not HAS_GRAPHVIZ:
                st.button("Generate Org Chart PNG", disabled=True,
                          help="Install graphviz: pip install graphviz + system Graphviz binary")
            else:
                if st.button("Generate Org Chart PNG", use_container_width=True):
                    png = make_org_chart_png(updated, unit_name)
                    if png:
                        st.image(png)
                        st.download_button("↓ Download PNG", data=png,
                                           file_name=f"Org_Chart_{unit_name.replace(' ','_')}.png",
                                           mime="image/png", use_container_width=True)
                        fp = unit_path(st.session_state.zed_udyam) / \
                             f"01_Leadership_Org_Chart_{unit_name.replace(' ','_')}.png"
                        fp.write_bytes(png)

        with gc2:
            if not HAS_DOCX:
                st.button("Roles & Responsibilities DOCX", disabled=True,
                          help="Install python-docx: pip install python-docx")
            else:
                if st.button("Roles & Responsibilities DOCX", use_container_width=True):
                    docx_bytes = make_roles_docx(updated, unit_name, d)
                    st.download_button("↓ Download DOCX", data=docx_bytes,
                                       file_name=f"Roles_Responsibilities_{unit_name.replace(' ','_')}.docx",
                                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                       use_container_width=True)

        with gc3:
            if not HAS_DOCX:
                st.button("Management Review Template", disabled=True,
                          help="Install python-docx: pip install python-docx")
            else:
                if st.button("Management Review Template", use_container_width=True):
                    docx_bytes = make_mmr_template(unit_name, d)
                    st.download_button("↓ Download DOCX", data=docx_bytes,
                                       file_name=f"Monthly_Mgmt_Review_{unit_name.replace(' ','_')}.docx",
                                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                       use_container_width=True)

    # ── Navigation ─────────────────────────────────────────────────
    st.divider()
    cb, cs, cn = st.columns([1, 1, 2])
    with cb:
        if st.button("← Back", use_container_width=True):
            st.session_state.zed_step = 1
            st.rerun()
    with cs:
        if st.button("Skip for now", use_container_width=True):
            st.session_state.zed_step = 3
            st.rerun()
    with cn:
        if st.button("Save and continue →", type="primary", use_container_width=True):
            d["org_roles"]   = st.session_state.org_roles
            d["_last_step"]  = 3
            d["_updated"]    = datetime.now().isoformat()
            st.session_state.zed_data = d
            save_unit(st.session_state.zed_udyam, d)
            st.success("Saved ✓")
            st.session_state.zed_step = 3
            st.rerun()


# ════════════════════════════════════════════════════════════════
# GENERATORS
# ════════════════════════════════════════════════════════════════
def make_org_chart_png(roles, unit_name: str) -> bytes | None:
    dot = graphviz.Digraph(
        graph_attr={
            "rankdir": "TB", "splines": "ortho", "bgcolor": "white",
            "label": f"Organisation Chart\n{unit_name}",
            "labelloc": "t", "fontsize": "13", "fontname": "Helvetica",
        },
        node_attr={
            "shape": "box", "style": "filled,rounded",
            "fillcolor": "#e8f5ef", "color": "#1a7f5a",
            "fontname": "Helvetica", "fontsize": "10",
        },
        edge_attr={"arrowhead": "open", "color": "#6b7280"},
    )
    for role in roles:
        desig = role.get("designation","").strip()
        name  = role.get("name","").strip()
        if not desig:
            continue
        label = desig + (f"\n({name})" if name else "")
        dot.node(desig, label)

    for role in roles:
        desig     = role.get("designation","").strip()
        reports   = role.get("reports_to","").strip()
        if desig and reports and reports != "— (Top level)":
            dot.edge(reports, desig)

    try:
        return dot.pipe(format="png")
    except Exception as e:
        st.error(f"Could not generate chart. Make sure the Graphviz system binary is installed. Error: {e}")
        return None


def make_roles_docx(roles, unit_name: str, unit_data: dict) -> bytes:
    doc = Document()
    _doc_header(doc, "Roles and Responsibilities", unit_name, unit_data)

    for role in roles:
        desig   = role.get("designation","").strip()
        name    = role.get("name","").strip()
        reports = role.get("reports_to","").strip()
        resp    = role.get("responsibilities","").strip()
        if not desig:
            continue

        h = doc.add_heading(desig + (f" — {name}" if name else ""), level=2)
        t = doc.add_table(rows=3, cols=2)
        t.style = "Table Grid"
        for row, label, val in [
            (0, "Reports to",          reports if reports != "— (Top level)" else "—"),
            (1, "Key responsibilities", resp),
            (2, "Incumbent",           name if name else "TBD"),
        ]:
            t.rows[row].cells[0].text = label
            t.rows[row].cells[1].text = val
            t.rows[row].cells[0].paragraphs[0].runs[0].bold = True
        doc.add_paragraph()

    doc.add_paragraph("Display this document on the notice board and explain to all workers.")
    return _docx_bytes(doc)


def make_mmr_template(unit_name: str, unit_data: dict) -> bytes:
    doc = Document()
    _doc_header(doc, "Monthly Management Review Record", unit_name, unit_data)
    doc.add_paragraph(
        "ZED Bronze — Leadership Parameter. Complete and sign each month. "
        "Retain for at least 3 years."
    )

    t = doc.add_table(rows=1, cols=2)
    t.style = "Table Grid"
    t.rows[0].cells[0].text = "Meeting Date"
    t.rows[0].cells[1].text = ""

    agenda_items = [
        "Attendees (name and designation)",
        "Compliance status (licences, certifications — any expired or due?)",
        "Quality issues / customer complaints since last review",
        "Safety incidents or near-misses since last review",
        "Delivery performance — on-time vs late, reasons",
        "Actions from previous review — status (open / closed)",
        "New issues identified",
        "Actions assigned (Person  |  Action  |  Due date)",
        "Next review date",
    ]
    for item in agenda_items:
        row = t.add_row()
        row.cells[0].text = item
        row.cells[0].paragraphs[0].runs[0].bold = True
        row.cells[1].text = ""

    doc.add_paragraph()
    doc.add_paragraph(
        "Chair (Owner / MD): ___________________________   "
        "Signature: ___________________________"
    )
    return _docx_bytes(doc)


# ── DOCX helpers ──────────────────────────────────────────────────
def _doc_header(doc, title: str, unit_name: str, unit_data: dict):
    p = doc.add_heading(title, 0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    sub = doc.add_paragraph(unit_name)
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(13)
    sub.runs[0].bold = True

    meta = doc.add_paragraph(
        f"Date: {date.today().strftime('%d %B %Y')}   ·   Version: 1.0   ·   "
        f"Prepared for ZED Bronze Certification"
    )
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.runs[0].font.size = Pt(10)

    sig = doc.add_paragraph(
        "Prepared by: _______________________   "
        "Approved by (Owner signature): _______________________"
    )
    sig.runs[0].font.size = Pt(10)
    doc.add_paragraph()


def _docx_bytes(doc) -> bytes:
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ════════════════════════════════════════════════════════════════
# STEP 3 — POLICIES
# ════════════════════════════════════════════════════════════════
POLICY_KEYS = [
    ("quality",  "Quality Policy",                    "04_Quality/Quality_Policy"),
    ("env",      "Environment Policy",                "02_CleanWorkplace/Environment_Policy"),
    ("ohs",      "Occupational Health & Safety Policy", "03_OHS/OHS_Policy"),
]

def _load_policy_template(key: str) -> str:
    tpl_file = BASE / "zed_config" / "policy_templates" / f"{key}_policy.j2"
    if tpl_file.exists():
        return tpl_file.read_text()
    return ""

def _render_policy(key: str, answers: dict) -> str:
    tpl_text = _load_policy_template(key)
    if not tpl_text:
        return "(Template not found. Please add zed_config/policy_templates/{key}_policy.j2)"
    if not HAS_JINJA2:
        return "(Jinja2 not installed — run: pip install jinja2)"
    return Template(tpl_text).render(**answers, today=date.today().strftime("%d %B %Y"))


def _policy_tab(key: str, label: str, folder_prefix: str, d: dict, cfg):
    udyam     = st.session_state.zed_udyam
    unit_name = d.get("unit_name") or udyam
    tab_up, tab_gen = st.tabs([f"📎 Upload existing {label}", f"✏️ Generate {label}"])

    pol_data = d.get(f"policy_{key}", {})

    with tab_up:
        up = st.file_uploader(f"Upload {label} (PDF / image)", type=["pdf","jpg","jpeg","png"],
                               key=f"pol_up_{key}")
        if up:
            fp = unit_path(udyam) / f"{folder_prefix.replace('/','_')}_{up.name}"
            fp.write_bytes(up.read())
            pol_data["uploaded_file"] = str(fp)
            st.success(f"Saved: {up.name}")
        elif pol_data.get("uploaded_file"):
            st.caption(f"On file: {Path(pol_data['uploaded_file']).name}")

    with tab_gen:
        st.caption("Answer these short questions — the policy will be generated in plain English.")
        products   = st.text_input(f"What does {unit_name} make?",
                                    value=pol_data.get("q_products", d.get("main_products","")),
                                    key=f"pol_{key}_prod")
        customers  = st.text_input("Who are the main customers?",
                                    value=pol_data.get("q_customers", d.get("main_customers","")),
                                    key=f"pol_{key}_cust")
        if key == "quality":
            issues = st.text_area("What are the 2-3 main quality issues or risks?",
                                   value=pol_data.get("q_issues","e.g. dimensional errors, surface finish rejections"),
                                   key=f"pol_{key}_iss", height=72)
            commit = st.text_area("One commitment the owner wants to make to customers:",
                                   value=pol_data.get("q_commit","e.g. zero defect delivery, 100% on-time dispatch"),
                                   key=f"pol_{key}_com", height=72)
            hazards = ""; waste = ""
        elif key == "env":
            waste   = st.text_area("Main waste streams (solid, liquid, air emissions):",
                                    value=pol_data.get("q_waste","e.g. metal scrap, coolant sludge, dust"),
                                    key=f"pol_{key}_waste", height=72)
            commit  = st.text_area("One environment commitment:",
                                    value=pol_data.get("q_commit","e.g. reduce coolant use, proper scrap disposal"),
                                    key=f"pol_{key}_com", height=72)
            issues = ""; hazards = ""
        else:  # ohs
            hazards = st.text_area("Main hazards (machines, chemicals, heat, dust, noise, lifting):",
                                    value=pol_data.get("q_hazards","e.g. rotating machinery, metal chips, noise above 85 dB"),
                                    key=f"pol_{key}_haz", height=72)
            commit  = st.text_area("One safety commitment:",
                                    value=pol_data.get("q_commit","e.g. zero accident target, PPE for all workers"),
                                    key=f"pol_{key}_com", height=72)
            issues = ""; waste = ""

        if st.button(f"Generate {label}", key=f"pol_gen_{key}", type="primary"):
            answers = dict(unit_name=unit_name, products=products, customers=customers,
                           issues=issues, hazards=hazards, waste=waste, commit=commit,
                           owner_name=d.get("owner_name","___________"))
            pol_data.update({f"q_{k}": v for k, v in answers.items()})
            text = _render_policy(key, answers)
            pol_data["generated_text"] = text
            st.session_state[f"pol_text_{key}"] = text

        saved_text = st.session_state.get(f"pol_text_{key}", pol_data.get("generated_text",""))
        if saved_text:
            st.text_area("Generated policy (edit before using):", value=saved_text,
                          height=300, key=f"pol_edit_{key}")
            if HAS_DOCX:
                if st.button(f"Download {label} DOCX", key=f"pol_dl_{key}"):
                    doc = Document()
                    _doc_header(doc, label, unit_name, d)
                    for line in saved_text.split("\n"):
                        doc.add_paragraph(line)
                    doc.add_paragraph()
                    doc.add_paragraph(
                        "Owner Signature: ______________________   Date: ____________"
                    )
                    doc.add_paragraph(
                        "Display on notice board and explain to all workers."
                    )
                    fp = unit_path(udyam) / f"{folder_prefix.replace('/','_')}_{unit_name.replace(' ','_')}.docx"
                    fp.write_bytes(_docx_bytes(doc))
                    pol_data["generated_file"] = str(fp)
                    st.download_button(
                        f"↓ Download {label}",
                        data=_docx_bytes(doc),
                        file_name=fp.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"pol_dl2_{key}",
                    )
            st.warning("The owner must read, edit, and sign this policy. "
                       "The unit must actually follow what it says.")
    return pol_data


def screen_step3(cfg):
    d = st.session_state.zed_data
    st.subheader("Step 3 — Policies")
    st.caption("ZED Bronze — Leadership, Safety, Quality parameters. Upload existing or generate new.")

    tabs = st.tabs([label for _, label, _ in POLICY_KEYS])
    for i, (key, label, folder) in enumerate(POLICY_KEYS):
        with tabs[i]:
            d[f"policy_{key}"] = _policy_tab(key, label, folder, d, cfg)

    st.divider()
    cb, cs, cn = st.columns([1, 1, 2])
    with cb:
        if st.button("← Back", key="s3back", use_container_width=True):
            st.session_state.zed_step = 2; st.rerun()
    with cs:
        if st.button("Skip for now", key="s3skip", use_container_width=True):
            st.session_state.zed_step = 4; st.rerun()
    with cn:
        if st.button("Save and continue →", key="s3next", type="primary", use_container_width=True):
            d["_last_step"] = 4; d["_updated"] = datetime.now().isoformat()
            st.session_state.zed_data = d
            save_unit(st.session_state.zed_udyam, d)
            st.success("Saved ✓"); st.session_state.zed_step = 4; st.rerun()


# ════════════════════════════════════════════════════════════════
# STEP 4 — PROCESS FLOW
# ════════════════════════════════════════════════════════════════
def screen_step4(cfg):
    d = st.session_state.zed_data
    unit_name = d.get("unit_name") or st.session_state.zed_udyam
    udyam     = st.session_state.zed_udyam

    st.subheader("Step 4 — Process Flow Chart")
    st.caption("ZED Bronze — Quality parameter. Upload your existing flow chart or build one.")

    tab_up, tab_build = st.tabs(["📎 Upload existing chart", "🔧 Build one now"])

    with tab_up:
        up = st.file_uploader("Upload process flow chart (PDF / image)", type=["pdf","png","jpg","jpeg"],
                               key="pf_up")
        if up:
            fp = unit_path(udyam) / f"04_Quality_ProcessFlow_{up.name}"
            fp.write_bytes(up.read())
            d["process_flow_file"] = str(fp)
            save_unit(udyam, d)
            st.success(f"Saved: {up.name}")
            if up.type.startswith("image"):
                st.image(up.getvalue())
        elif d.get("process_flow_file"):
            st.caption(f"On file: {Path(d['process_flow_file']).name}")

    with tab_build:
        # Seed default steps
        if "process_steps" not in st.session_state:
            saved = d.get("process_steps")
            st.session_state.process_steps = saved if saved else [
                {"step": "Raw material receipt",   "machine": "",                "inspection": True,  "check": "Material grade, dimensions", "hazard": "Manual handling"},
                {"step": "Incoming inspection",    "machine": "Vernier, micrometer", "inspection": True,  "check": "Dimensions, surface, hardness", "hazard": ""},
                {"step": "Cutting / Blanking",     "machine": "Shear / bandsaw",   "inspection": False, "check": "", "hazard": "Sharp edges, noise"},
                {"step": "Machining",              "machine": "CNC / lathe",       "inspection": False, "check": "", "hazard": "Rotating parts, chips"},
                {"step": "In-process inspection",  "machine": "Gauges",            "inspection": True,  "check": "Dimensions, finish",          "hazard": ""},
                {"step": "Final inspection",       "machine": "CMM / gauges",      "inspection": True,  "check": "All drawing requirements",    "hazard": ""},
                {"step": "Packing",                "machine": "",                  "inspection": False, "check": "",                            "hazard": ""},
                {"step": "Dispatch",               "machine": "",                  "inspection": False, "check": "Correct quantity & address",  "hazard": "Lifting"},
            ]

        steps_data = st.session_state.process_steps
        updated_steps = []
        for i, s in enumerate(steps_data):
            with st.container(border=True):
                c1, c2, c3, cdel = st.columns([2, 2, 2, 0.3])
                with c1:
                    step_name = st.text_input("Process step *", value=s.get("step",""), key=f"ps_name_{i}")
                    machine   = st.text_input("Machine / equipment", value=s.get("machine",""), key=f"ps_mach_{i}")
                with c2:
                    insp = st.checkbox("Inspection point?", value=s.get("inspection", False), key=f"ps_insp_{i}")
                    check = st.text_input("What is checked", value=s.get("check",""), key=f"ps_check_{i}",
                                          disabled=not insp)
                with c3:
                    hazard = st.text_input("Key hazard (if any)", value=s.get("hazard",""), key=f"ps_haz_{i}")
                with cdel:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if st.button("✕", key=f"ps_del_{i}", help="Remove step"):
                        steps_data.pop(i); st.session_state.process_steps = steps_data; st.rerun()
                updated_steps.append({"step": step_name, "machine": machine,
                                       "inspection": insp, "check": check, "hazard": hazard})
        st.session_state.process_steps = updated_steps

        if st.button("＋ Add process step"):
            st.session_state.process_steps.append(
                {"step":"","machine":"","inspection":False,"check":"","hazard":""})
            st.rerun()

        st.divider()
        st.markdown("**Generate outputs**")
        g1, g2, g3 = st.columns(3)

        with g1:
            if not HAS_GRAPHVIZ:
                st.button("Process Flow PNG", disabled=True, help="Install graphviz")
            elif st.button("Process Flow PNG", use_container_width=True):
                png = make_process_flow_png(updated_steps, unit_name)
                if png:
                    st.image(png)
                    fp = unit_path(udyam) / f"04_Quality_ProcessFlow_{unit_name.replace(' ','_')}.png"
                    fp.write_bytes(png)
                    d["process_flow_generated"] = str(fp)
                    st.download_button("↓ Download PNG", data=png,
                                       file_name=fp.name, mime="image/png")

        with g2:
            if not HAS_DOCX:
                st.button("Inspection Checklist DOCX", disabled=True)
            elif st.button("Inspection Checklist DOCX", use_container_width=True):
                b = make_inspection_checklist(updated_steps, unit_name, d)
                st.download_button("↓ Download", data=b,
                                   file_name=f"Inspection_Checklist_{unit_name.replace(' ','_')}.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        with g3:
            if not HAS_DOCX:
                st.button("Inspection Record Templates", disabled=True)
            elif st.button("Inspection Record Templates", use_container_width=True):
                b = make_inspection_records(unit_name, d)
                st.download_button("↓ Download", data=b,
                                   file_name=f"Inspection_Records_{unit_name.replace(' ','_')}.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    st.divider()
    cb, cs, cn = st.columns([1, 1, 2])
    with cb:
        if st.button("← Back", key="s4back", use_container_width=True):
            st.session_state.zed_step = 3; st.rerun()
    with cs:
        if st.button("Skip for now", key="s4skip", use_container_width=True):
            st.session_state.zed_step = 5; st.rerun()
    with cn:
        if st.button("Save and continue →", key="s4next", type="primary", use_container_width=True):
            d["process_steps"] = st.session_state.process_steps
            d["_last_step"] = 5; d["_updated"] = datetime.now().isoformat()
            st.session_state.zed_data = d
            save_unit(udyam, d); st.success("Saved ✓")
            st.session_state.zed_step = 5; st.rerun()


def make_process_flow_png(steps, unit_name: str):
    dot = graphviz.Digraph(
        graph_attr={"rankdir":"TB","splines":"ortho","bgcolor":"white",
                    "label":f"Process Flow Chart\n{unit_name}","labelloc":"t",
                    "fontsize":"13","fontname":"Helvetica"},
        node_attr={"fontname":"Helvetica","fontsize":"10"},
        edge_attr={"arrowhead":"open","color":"#6b7280"},
    )
    valid = [s for s in steps if s.get("step","").strip()]
    for i, s in enumerate(valid):
        nid   = f"n{i}"
        label = s["step"]
        if s.get("machine"): label += f"\n({s['machine']})"
        if s.get("inspection"):
            dot.node(nid, label=label, shape="diamond", style="filled",
                     fillcolor="#fef9c3", color="#d97706")
        else:
            dot.node(nid, label=label, shape="box", style="filled,rounded",
                     fillcolor="#e8f5ef", color="#1a7f5a")
        if i > 0:
            dot.edge(f"n{i-1}", nid)
    try:
        return dot.pipe(format="png")
    except Exception as e:
        st.error(f"Chart error: {e}"); return None


def make_inspection_checklist(steps, unit_name: str, unit_data: dict) -> bytes:
    doc = Document()
    _doc_header(doc, "Inspection Checklist", unit_name, unit_data)
    insp_steps = [s for s in steps if s.get("inspection") and s.get("step","").strip()]
    if not insp_steps:
        doc.add_paragraph("No inspection points defined.")
        return _docx_bytes(doc)
    t = doc.add_table(rows=1, cols=5)
    t.style = "Table Grid"
    for cell, hdr in zip(t.rows[0].cells, ["Process Step","What is Checked","Result","Checked By","Date"]):
        cell.text = hdr
        cell.paragraphs[0].runs[0].bold = True
    for s in insp_steps:
        row = t.add_row()
        row.cells[0].text = s["step"]
        row.cells[1].text = s.get("check","")
    return _docx_bytes(doc)


def make_inspection_records(unit_name: str, unit_data: dict) -> bytes:
    doc = Document()
    for stage in ["Incoming", "In-Process", "Final"]:
        _doc_header(doc, f"{stage} Inspection Record", unit_name, unit_data)
        t = doc.add_table(rows=1, cols=6)
        t.style = "Table Grid"
        hdrs = ["Date","Part / Material","Qty","Parameter Checked","Result (OK/NG)","Inspector"]
        for cell, hdr in zip(t.rows[0].cells, hdrs):
            cell.text = hdr; cell.paragraphs[0].runs[0].bold = True
        for _ in range(10):
            t.add_row()
        doc.add_page_break()
    return _docx_bytes(doc)


# ════════════════════════════════════════════════════════════════
# STEP 5 — REGISTERS
# ════════════════════════════════════════════════════════════════
def screen_step5(cfg):
    d = st.session_state.zed_data
    unit_name = d.get("unit_name") or st.session_state.zed_udyam
    udyam     = st.session_state.zed_udyam

    st.subheader("Step 5 — Registers & Records")
    st.caption("ZED Bronze — Clean Workplace, Safety, Quality, Timely Delivery parameters.")
    st.markdown("Generate blank, printable templates pre-filled with your unit name. Print and fill by hand.")

    if not HAS_DOCX:
        st.error("python-docx not installed. Run: pip install python-docx")
        _nav(5); return

    REGS = [
        ("cleaning",   "Cleaning Schedule",              "01_CleanWorkplace"),
        ("pest",       "Pest Control Record",            "01_CleanWorkplace"),
        ("safety_att", "Safety Training Attendance Sheet","03_OHS"),
        ("accident",   "Accident / Near-Miss Register",  "03_OHS"),
        ("ppe",        "PPE Issue Register",             "03_OHS"),
        ("delivery",   "Delivery Performance Register",  "05_Delivery"),
        ("rework",     "Rejection / Rework Log",         "04_Quality"),
        ("calibration","Calibration Record",             "04_Quality"),
    ]

    cols = st.columns(2)
    for idx, (key, label, folder) in enumerate(REGS):
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                if st.button(f"Generate {label}", key=f"reg_{key}", use_container_width=True):
                    b = make_register(key, unit_name, d)
                    fname = f"{folder}_{label.replace(' ','_')}_{unit_name.replace(' ','_')}.docx"
                    fp = unit_path(udyam) / fname
                    fp.write_bytes(b)
                    reg_files = d.get("register_files", {})
                    reg_files[key] = str(fp)
                    d["register_files"] = reg_files
                    st.download_button(f"↓ Download", data=b, file_name=fname,
                                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                       key=f"reg_dl_{key}")
                elif d.get("register_files",{}).get(key):
                    st.caption(f"✅ Generated: {Path(d['register_files'][key]).name}")

    _nav(5, d, udyam)


def make_register(key: str, unit_name: str, unit_data: dict) -> bytes:
    doc = Document()
    configs = {
        "cleaning": ("Cleaning Schedule", ["Area", "Cleaning Activity", "Frequency",
                      "Mon","Tue","Wed","Thu","Fri","Sat","Responsible"]),
        "pest":     ("Pest Control Record", ["Date","Service Provider","Activity Carried Out",
                      "Observations","Next Due Date","Verified By"]),
        "safety_att":("Safety Training Attendance Sheet", ["Date","Training Topic","Name",
                       "Designation","Signature"]),
        "accident": ("Accident / Near-Miss Register", ["Date","Time","Name of Person","Type (Accident/Near-Miss)",
                      "Description","Injury / Damage","Immediate Action","Root Cause","Corrective Action","Closed By"]),
        "ppe":      ("PPE Issue Register", ["Date","Employee Name","Designation","PPE Item",
                      "Size","Quantity","Condition (New/Replace)","Employee Signature"]),
        "delivery": ("Delivery Register", ["PO Number","Customer","PO Delivery Date","Invoice Date",
                      "Qty Ordered","Qty Shipped","On Time (Y/N)","Reason if Late","Action Taken"]),
        "rework":   ("Rejection / Rework Log", ["Date","Part No / Description","Qty Rejected",
                      "Defect Type","Stage Detected","Root Cause","Disposition (Rework/Scrap)","Action Taken"]),
        "calibration":("Calibration Record", ["Instrument Name","Instrument ID","Range / Least Count",
                        "Location","Last Calibrated","Due Date","Certificate No.","Status (OK/Due/Overdue)"]),
    }
    title, headers = configs[key]
    _doc_header(doc, title, unit_name, unit_data)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for cell, hdr in zip(t.rows[0].cells, headers):
        cell.text = hdr; cell.paragraphs[0].runs[0].bold = True
    for _ in range(15):
        t.add_row()
    return _docx_bytes(doc)


# ════════════════════════════════════════════════════════════════
# STEP 6 — SITE PHOTOS
# ════════════════════════════════════════════════════════════════
PHOTO_LIST = [
    ("exterior",    "Unit exterior — name board visible",
     "Stand outside the main gate. Make sure the unit name board is clearly readable."),
    ("gangways",    "Marked gangways / yellow lines on shop floor",
     "Walk lanes should be painted yellow. Photo should show the lines clearly."),
    ("labelled",    "Labelled areas (RM, WIP, FG, scrap)",
     "Show signs or tape marking where raw material, WIP, finished goods, and scrap are kept."),
    ("rm_storage",  "Raw material storage",
     "Stacked neatly, labelled, off the floor if possible. No mixed materials."),
    ("fg_storage",  "Finished goods storage",
     "Clearly separated from RM. Labelled bins or racks."),
    ("scrap",       "Scrap / waste storage area",
     "Separate, labelled container or area for scrap and waste. Metal and non-metal waste separated."),
    ("ppe",         "Workers wearing PPE at a machine",
     "Safety shoes, gloves, goggles, ear protection as relevant. Worker actively at a machine."),
    ("extinguisher","Fire extinguisher — mounted with refill tag",
     "Extinguisher on wall bracket. Refill date tag clearly visible in photo."),
    ("safety_signs","Safety signs and posters",
     "No Smoking, First Aid, PPE mandatory, emergency exit arrows visible."),
    ("guards",      "Machine guards on rotating parts",
     "Show the guard covering the rotating spindle, belt, or chuck. Guard must be in place."),
    ("first_aid",   "First aid box",
     "Mounted on wall, labelled FIRST AID. Box should be clearly stocked."),
    ("noticeboard", "Policies displayed on notice board",
     "Quality, Environment, OHS policies printed and pinned on a visible notice board."),
    ("qc_area",     "Quality inspection area with instruments",
     "Dedicated table or area. Instruments (vernier, micrometer, etc.) laid out."),
    ("cal_tags",    "Calibration tags on gauges",
     "Close-up of a gauge or instrument showing the calibration tag with due date."),
    ("cleaning_sch","Cleaning schedule displayed and signed",
     "Printed cleaning schedule on the wall, filled in and signed for the current month."),
]


def screen_step6(cfg):
    d     = st.session_state.zed_data
    udyam = st.session_state.zed_udyam

    st.subheader("Step 6 — Site Photos")
    st.caption("ZED Bronze — all parameters. Take photos inside the unit, in daylight, no stock images.")
    st.info("Note: The ZED portal also needs a live-location selfie from the unit representative, "
            "which must be taken directly on the portal — not here.")

    photos = d.get("photos", {})
    STATUS_OPTS = ["Pending", "Done", "Not applicable"]

    for key, title, instruction in PHOTO_LIST:
        ph = photos.get(key, {"status": "Pending", "file": ""})
        with st.expander(f"{'✅' if ph['status']=='Done' else ('—' if ph['status']=='Not applicable' else '🔲')}  {title}",
                          expanded=(ph["status"] == "Pending")):
            st.caption(instruction)
            c1, c2 = st.columns([2, 1])
            with c1:
                up = st.file_uploader("Upload / capture photo", type=["jpg","jpeg","png","heic"],
                                       key=f"photo_{key}")
                if up:
                    fp = unit_path(udyam) / f"06_Photos_{key}_{up.name}"
                    fp.write_bytes(up.read())
                    ph["file"] = str(fp)
                    ph["status"] = "Done"
                    st.image(up.getvalue(), width=300)
                elif ph.get("file") and Path(ph["file"]).exists():
                    st.image(Path(ph["file"]).read_bytes(), width=300)
            with c2:
                new_status = st.radio("Status", STATUS_OPTS,
                                       index=STATUS_OPTS.index(ph["status"]),
                                       key=f"photo_st_{key}")
                ph["status"] = new_status
            photos[key] = ph

    done  = sum(1 for p in photos.values() if p["status"] == "Done")
    na    = sum(1 for p in photos.values() if p["status"] == "Not applicable")
    total = len(PHOTO_LIST)
    st.progress((done + na) / total)
    st.caption(f"{done} done · {na} not applicable · {total - done - na} pending out of {total}")

    _nav(6, d, udyam, extra={"photos": photos})


# ════════════════════════════════════════════════════════════════
# STEP 7 — EVIDENCE PACK
# ════════════════════════════════════════════════════════════════
EVIDENCE_MAP = [
    ("01_Leadership", "Leadership", [
        ("licences",       "Licences & consents (factory, fire NOC, MPCB)"),
        ("org_chart_file", "Organisation chart"),
        ("org_roles",      "Roles & responsibilities"),
        ("policy_quality", "Quality Policy"),
        ("policy_env",     "Environment Policy"),
        ("policy_ohs",     "OHS Policy"),
    ]),
    ("02_CleanWorkplace", "Clean Workplace", [
        ("photos",         "Site photos (labelled areas, scrap storage, gangways)"),
        ("register_files", "Cleaning schedule register"),
    ]),
    ("03_OHS", "Occupational Health & Safety", [
        ("policy_ohs",       "OHS Policy"),
        ("register_files",   "Safety training attendance, accident register, PPE register"),
        ("photos",           "Photos — PPE, fire extinguisher, safety signs, machine guards, first aid"),
    ]),
    ("04_Quality", "Quality Management", [
        ("process_flow_generated", "Process flow chart"),
        ("process_steps",          "Inspection checklists"),
        ("register_files",         "Rejection/rework log, calibration record"),
        ("photos",                 "Photos — QC area, calibration tags"),
    ]),
    ("05_Delivery", "Timely Delivery", [
        ("register_files", "Delivery performance register"),
    ]),
]


def _item_status(d: dict, key: str) -> str:
    val = d.get(key)
    if not val:
        return "pending"
    if isinstance(val, dict):
        # Has a saved file → done; has text/answers only → partial; nothing → pending
        has_file = any("file" in k and v for k, v in val.items())
        has_any  = any(v for v in val.values())
        if has_file:
            return "done"
        if has_any:
            return "partial"
        return "pending"
    if isinstance(val, list):
        return "done" if len(val) > 0 else "pending"
    return "done"


def screen_step7(cfg):
    d         = st.session_state.zed_data
    unit_name = d.get("unit_name") or st.session_state.zed_udyam
    udyam     = st.session_state.zed_udyam

    st.subheader("Step 7 — Evidence Pack")
    st.caption("Review status and download your ZED Bronze evidence pack.")

    # Status table
    all_files: list[tuple[str, str]] = []  # (folder, filepath)

    for folder, param, items in EVIDENCE_MAP:
        st.markdown(f"#### {param}")
        rows = []
        for key, label in items:
            status = _item_status(d, key)
            icon   = "✅" if status == "done" else ("🟡" if status == "partial" else "⬜")
            rows.append(f"{icon}  {label}")
            # Collect generated files — only look at values whose key contains "file"
            val = d.get(key)
            if isinstance(val, str) and len(val) < 512 and Path(val).exists():
                all_files.append((folder, val))
            elif isinstance(val, dict):
                for k, v in val.items():
                    if "file" in k and isinstance(v, str) and len(v) < 512 and Path(v).exists():
                        all_files.append((folder, v))
        for r in rows:
            st.markdown(r)
        st.divider()

    # Photo files
    photos = d.get("photos", {})
    for ph in photos.values():
        fp = ph.get("file","")
        if fp and Path(fp).exists():
            all_files.append(("06_Photos", fp))

    # Summary
    done_count = sum(1 for f, _ in all_files for folder, _ in [(f,"")])
    st.markdown(f"**{len(all_files)} files ready for the pack.**")

    if not all_files:
        st.warning("No files generated yet. Complete the earlier steps first.")
    else:
        if st.button("📦 Download Evidence Pack (ZIP)", type="primary", use_container_width=True):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                seen = set()
                for folder, fp in all_files:
                    p = Path(fp)
                    arcname = f"{folder}/{p.name}"
                    if arcname not in seen and p.exists():
                        zf.write(p, arcname)
                        seen.add(arcname)
                # Summary text
                lines = [f"ZED Bronze Evidence Pack — {unit_name}", f"Generated: {date.today()}", ""]
                for folder, param, items in EVIDENCE_MAP:
                    lines.append(f"=== {param} ===")
                    for key, label in items:
                        status = _item_status(d, key)
                        icon   = "[DONE]" if status == "done" else ("[PARTIAL]" if status == "partial" else "[PENDING]")
                        lines.append(f"  {icon}  {label}")
                    lines.append("")
                lines.append("Note: The ZED portal also needs a live-location selfie taken directly on zed.msme.gov.in.")
                zf.writestr("00_Summary/Evidence_Pack_Summary.txt", "\n".join(lines))
            st.download_button(
                "↓ Download ZIP",
                data=buf.getvalue(),
                file_name=f"ZED_Bronze_Evidence_{unit_name.replace(' ','_')}.zip",
                mime="application/zip",
                use_container_width=True,
            )

    st.divider()
    cb = st.columns([1, 4])[0]
    with cb:
        if st.button("← Back", key="s7back", use_container_width=True):
            st.session_state.zed_step = 6; st.rerun()


# ── Shared navigation helper ──────────────────────────────────────
def _nav(step: int, d: dict = None, udyam: str = None, extra: dict = None):
    st.divider()
    cb, cs, cn = st.columns([1, 1, 2])
    with cb:
        if st.button("← Back", key=f"s{step}back", use_container_width=True):
            st.session_state.zed_step = step - 1; st.rerun()
    with cs:
        if st.button("Skip for now", key=f"s{step}skip", use_container_width=True):
            st.session_state.zed_step = step + 1; st.rerun()
    with cn:
        if st.button("Save and continue →", key=f"s{step}next", type="primary", use_container_width=True):
            if d is not None:
                if extra:
                    d.update(extra)
                d["_last_step"] = step + 1; d["_updated"] = datetime.now().isoformat()
                st.session_state.zed_data = d
                save_unit(udyam, d)
            st.success("Saved ✓")
            st.session_state.zed_step = step + 1; st.rerun()


# ════════════════════════════════════════════════════════════════
main()
