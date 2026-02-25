import io
import math
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="CBAM Risk Calculator", layout="wide")

# ── Brand colours ─────────────────────────────────────────────────────────────
OLIVE_HEX  = "#6B7C45"
DARK_HEX   = "#1F2E12"
RED_HEX    = "#C0392B"
AMBER_HEX  = "#D4880A"
GREEN_HEX  = "#27AE60"

# ── Sector catalogue ──────────────────────────────────────────────────────────
# Emission intensity: tCO2e per tonne of product (or tCO2e per MWh for electricity)
SECTORS = {
    "Iron & Steel": {
        "unit": "tonnes",
        "products": {
            "Hot-rolled flat products (BF-BOF route)":  2.3,
            "Cold-rolled flat products (BF-BOF route)": 2.5,
            "Structural steel / Rebar (BF-BOF route)":  2.3,
            "Structural steel / Rebar (EAF route)":     1.8,
            "Stainless steel":                          3.5,
            "Pipes & tubes":                            2.4,
            "Other iron & steel products":              2.3,
        },
        "source": "IEA India Steel Sector; BEE benchmarks (2022-23)",
    },
    "Aluminium": {
        "unit": "tonnes",
        "products": {
            "Primary aluminium — coal-heavy grid":   14.0,
            "Primary aluminium — mixed grid":        11.0,
            "Secondary / recycled aluminium":         0.8,
            "Aluminium alloys (primary input)":      14.0,
            "Aluminium semi-fabricated products":    14.0,
        },
        "source": "International Aluminium Institute; India grid intensity (CEA 2022-23)",
    },
    "Cement": {
        "unit": "tonnes",
        "products": {
            "Ordinary Portland Cement (OPC)":      0.83,
            "Portland Pozzolana Cement (PPC)":     0.65,
            "Clinker":                             0.87,
            "Other blended cement":                0.70,
        },
        "source": "CSI GNR Database; CMA India average (2022-23)",
    },
    "Fertilisers": {
        "unit": "tonnes",
        "products": {
            "Ammonia":                   2.3,
            "Urea":                      2.5,
            "Ammonium nitrate":          8.0,
            "Mixed NPK fertilisers":     3.0,
            "Nitric acid":               7.5,
        },
        "source": "IFA India fertiliser sector data (2022)",
    },
    "Hydrogen": {
        "unit": "tonnes",
        "products": {
            "Grey hydrogen (SMR, no CCS)":    10.0,
            "Blue hydrogen (SMR + CCS)":       2.0,
            "Green hydrogen (renewable)":      0.5,
        },
        "source": "IRENA, IEA Hydrogen Report (2022)",
    },
    "Electricity": {
        "unit": "MWh",
        "products": {
            "India grid average":       0.716,
            "Coal-based generation":    1.020,
            "Gas-based generation":     0.490,
            "Renewable electricity":    0.050,
        },
        "source": "CEA CO2 Baseline Database (2022-23)",
    },
}

# Fuel emission factors (tCO2e per unit) for activity-data method
FUEL_FACTORS = {
    "Diesel (litres)":           0.00268,
    "LPG (kg)":                  0.00161,
    "Natural Gas (SCM)":         0.00200,
    "Coal (kg)":                 0.00242,
    "Furnace Oil / HSD (litres)":0.00315,
    "Petrol (litres)":           0.00231,
}
ELECTRICITY_FACTOR = 0.000716   # tCO2e per kWh (India CEA 2022-23)

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_inr(val):
    """Format a ₹ value as crore / lakh string."""
    if val >= 1e7:
        return f"₹{val/1e7:.2f} Cr"
    elif val >= 1e5:
        return f"₹{val/1e5:.2f} L"
    else:
        return f"₹{val:,.0f}"

def risk_label(liability_inr, revenue_inr):
    pct = (liability_inr / revenue_inr * 100) if revenue_inr > 0 else None
    if liability_inr >= 1e7 or (pct and pct > 10):
        return "HIGH", RED_HEX
    elif liability_inr >= 25e5 or (pct and pct > 3):
        return "MEDIUM", AMBER_HEX
    else:
        return "LOW", GREEN_HEX

def sensitivity_table(embedded_emissions, domestic_price, eur_inr):
    prices  = [30, 50, 70, 90, 110, 130]
    rows = []
    for p in prices:
        net = max(p - domestic_price, 0)
        lib_eur = embedded_emissions * net
        lib_inr = lib_eur * eur_inr
        rows.append({
            "EU ETS Price (€/tCO₂e)": f"€{p}",
            "Net Price (€/tCO₂e)": f"€{net:.0f}",
            "Annual Liability (€)": f"€{lib_eur:,.0f}",
            "Annual Liability (₹)": fmt_inr(lib_inr),
        })
    return pd.DataFrame(rows), prices, [
        max(p - domestic_price, 0) * embedded_emissions * eur_inr / 1e7
        for p in prices
    ]

def recommendations(sector, risk):
    base = {
        "HIGH": [
            "Commission a verified Scope 1 & 2 GHG inventory — sector defaults may over- or under-estimate your true exposure.",
            "Engage your EU importer immediately on cost-sharing arrangements for CBAM certificate costs.",
            "Review your supply and offtake contracts for CBAM pass-through clauses before the next renewal.",
            "Ensure CBAM transitional-period reports (mandatory since Oct 2023) are filed via the CBAM Transitional Registry.",
            "Seek expert support for CBAM declaration preparation for 2026 certificate submissions.",
        ],
        "MEDIUM": [
            "Measure your actual emission intensity — this will likely reduce or clarify your true liability.",
            "Identify quick-win energy efficiency measures to lower your embedded emission intensity.",
            "Begin setting up internal CBAM reporting systems and data collection processes.",
            "Review EU buyer contracts for CBAM cost allocation clauses.",
        ],
        "LOW": [
            "Monitor EU ETS price trends — prices above €100/tCO₂e could materially increase your exposure.",
            "Start basic emission monitoring even if not yet required.",
            "Ensure CBAM transitional reporting compliance is in place.",
        ],
    }
    sector_specific = {
        "Iron & Steel": [
            "Transition to Electric Arc Furnace (EAF) route with renewable electricity — this can cut intensity by 30–40%.",
            "Maximise scrap use in your production mix to reduce BF-BOF dependency.",
        ],
        "Aluminium": [
            "Electricity source is the single largest driver — consider renewable PPAs or captive solar.",
            "Procurement of green aluminium certificates may be recognised by EU buyers.",
        ],
        "Cement": [
            "Increase fly ash or slag substitution in blended cement to reduce clinker ratio.",
            "Waste heat recovery investments reduce both energy cost and Scope 1 intensity.",
        ],
        "Fertilisers": [
            "Evaluate green ammonia production pathways for long-term CBAM liability reduction.",
            "N₂O catalytic abatement in nitric acid plants significantly cuts Scope 1 intensity.",
        ],
        "Hydrogen": [
            "Green hydrogen carries near-zero CBAM liability — a key competitive differentiator.",
            "If producing grey hydrogen, CCS feasibility assessment is warranted at this liability level.",
        ],
        "Electricity": [
            "Renewable generation has near-zero CBAM liability — a strong market differentiator for EU buyers.",
        ],
    }
    recs = base.get(risk, base["LOW"]) + sector_specific.get(sector, [])
    return recs

# ── Sensitivity chart (matplotlib — also used in PDF) ─────────────────────────

def build_sensitivity_chart(prices, values_crore, current_ets, embedded, domestic, eur_inr):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    bar_colors = []
    for v in values_crore:
        if v * 1e7 >= 1e7:
            bar_colors.append(RED_HEX)
        elif v * 1e7 >= 25e5:
            bar_colors.append(AMBER_HEX)
        else:
            bar_colors.append(GREEN_HEX)

    bars = ax.bar([f"€{p}" for p in prices], values_crore, color=bar_colors, width=0.55, edgecolor="none")
    current_liability_crore = max(current_ets - domestic, 0) * embedded * eur_inr / 1e7
    ax.axhline(current_liability_crore, color=OLIVE_HEX, linewidth=1.5, linestyle="--", label=f"Current (€{current_ets})")
    ax.set_xlabel("EU ETS Carbon Price", fontsize=9)
    ax.set_ylabel("Annual CBAM Liability (₹ Crore)", fontsize=9)
    ax.set_title("Sensitivity of CBAM Liability to EU ETS Price", fontsize=10, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=8)
    for bar, val in zip(bars, values_crore):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=7.5, color="#333333")
    fig.tight_layout()
    return fig


# ── PDF generation ────────────────────────────────────────────────────────────

def generate_pdf(inputs: dict, results: dict, sens_df: pd.DataFrame,
                 sens_prices, sens_values, recs: list) -> bytes:

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    brand   = ParagraphStyle("brand",   fontSize=18, textColor=colors.HexColor(OLIVE_HEX),  fontName="Helvetica-Bold", spaceAfter=2)
    title_s = ParagraphStyle("title_s", fontSize=13, textColor=colors.HexColor(DARK_HEX),   fontName="Helvetica-Bold", spaceAfter=4)
    meta_s  = ParagraphStyle("meta_s",  fontSize=8,  textColor=colors.grey,                 spaceAfter=2)
    h2      = ParagraphStyle("h2",      fontSize=10, textColor=colors.HexColor(DARK_HEX),   fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
    body_s  = ParagraphStyle("body_s",  fontSize=8.5, leading=13, spaceAfter=3)
    bullet_s= ParagraphStyle("bullet",  fontSize=8.5, leading=13, leftIndent=12, spaceAfter=3)

    TBL_HEADER = colors.HexColor(OLIVE_HEX)
    TBL_ALT    = colors.HexColor("#F5F5F5")

    def section_rule():
        return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor(OLIVE_HEX), spaceAfter=6, spaceBefore=2)

    story = []

    # ── Header ──
    story += [
        Paragraph("Total Impact", brand),
        Paragraph("CBAM Risk Assessment", title_s),
        Paragraph(f"Prepared: {date.today().strftime('%d %B %Y')}  |  "
                  f"Sector: {inputs['sector']}  |  Product: {inputs['product']}", meta_s),
        section_rule(),
        Spacer(1, 0.2*cm),
    ]

    # ── Input summary ──
    story.append(Paragraph("1. Assessment Inputs", h2))
    inp_data = [
        ["Parameter", "Value"],
        ["Sector", inputs["sector"]],
        ["Product Type", inputs["product"]],
        ["Export Volume to EU", f"{inputs['volume']:,.0f} {inputs['unit']}/year"],
        ["Export Revenue (EU)", fmt_inr(inputs["revenue_inr"]) if inputs["revenue_inr"] > 0 else "Not provided"],
        ["Emission Intensity Method", inputs["intensity_method"]],
        ["Emission Intensity", f"{inputs['intensity']:.3f} tCO₂e/{inputs['unit']}"],
        ["EU ETS Carbon Price", f"€{inputs['ets_price']}/tCO₂e"],
        ["Domestic Carbon Price (India)", f"€{inputs['domestic_price']}/tCO₂e"],
        ["EUR / INR Rate", f"1 € = ₹{inputs['eur_inr']}"],
        ["Organisational Boundary", inputs.get("boundary", "Operational Control")],
    ]
    tbl = Table(inp_data, colWidths=[6*cm, 10*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), TBL_HEADER),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("BACKGROUND", (0,1), (0,-1), TBL_ALT),
        ("FONTNAME",   (0,1), (0,-1), "Helvetica-Bold"),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, TBL_ALT]),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ]))
    story += [tbl, Spacer(1, 0.3*cm)]

    # ── Key results ──
    story.append(Paragraph("2. Key Results", h2))
    risk_color = {
        "HIGH": colors.HexColor(RED_HEX),
        "MEDIUM": colors.HexColor(AMBER_HEX),
        "LOW": colors.HexColor(GREEN_HEX),
    }[results["risk"]]

    res_data = [
        ["Metric", "Value"],
        ["Total Embedded Emissions", f"{results['embedded']:,.1f} tCO₂e/year"],
        ["CBAM Certificates Required", f"{results['embedded']:,.1f} certificates/year"],
        ["Annual Liability (EUR)", f"€{results['liability_eur']:,.0f}"],
        ["Annual Liability (INR)", fmt_inr(results["liability_inr"])],
        ["Revenue Impact", f"{results['pct_revenue']:.1f}% of EU export revenue" if results["pct_revenue"] else "Revenue not provided"],
        ["Risk Rating", results["risk"]],
    ]
    tbl2 = Table(res_data, colWidths=[7*cm, 9*cm])
    risk_row = len(res_data) - 1
    tbl2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), TBL_HEADER),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("BACKGROUND", (0,1), (0,-1), TBL_ALT),
        ("FONTNAME",   (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",   (0,risk_row), (-1,risk_row), "Helvetica-Bold"),
        ("TEXTCOLOR",  (1,risk_row), (1,risk_row), risk_color),
        ("FONTSIZE",   (1,risk_row), (1,risk_row), 10),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, TBL_ALT]),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ]))
    story += [tbl2, Spacer(1, 0.3*cm)]

    # ── Sensitivity chart ──
    story.append(Paragraph("3. Sensitivity Analysis", h2))
    fig = build_sensitivity_chart(
        sens_prices, sens_values,
        inputs["ets_price"], results["embedded"],
        inputs["domestic_price"], inputs["eur_inr"],
    )
    chart_buf = io.BytesIO()
    fig.savefig(chart_buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    chart_buf.seek(0)
    story += [Image(chart_buf, width=14*cm, height=7*cm), Spacer(1, 0.2*cm)]

    # Sensitivity table
    sens_table_data = [list(sens_df.columns)] + sens_df.values.tolist()
    tbl3 = Table(sens_table_data, colWidths=[3.5*cm, 3.5*cm, 4*cm, 4*cm])
    tbl3.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), TBL_HEADER),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 7.5),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, TBL_ALT]),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
    ]))
    story += [tbl3, Spacer(1, 0.3*cm)]

    # ── Recommendations ──
    story.append(Paragraph("4. Recommendations", h2))
    for rec in recs:
        story.append(Paragraph(f"• {rec}", bullet_s))
    story.append(Spacer(1, 0.3*cm))

    # ── Footer ──
    story.append(section_rule())
    story.append(Paragraph(
        "Developed by Arun Venkatraman | Total Impact | arun@totalimpact.co.in | +91 6374350144 | totalimpact.co.in",
        ParagraphStyle("footer", fontSize=7.5, textColor=colors.grey, alignment=1)
    ))
    story.append(Paragraph(
        "Disclaimer: This assessment uses sector-average emission intensities and publicly available CBAM parameters. "
        "It is indicative only and should not substitute for verified GHG accounting or legal/regulatory advice.",
        ParagraphStyle("disc", fontSize=7, textColor=colors.grey, alignment=1, spaceBefore=3)
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ══════════════════════════════════════════════════════════════════════════════
# ── UI ────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

st.title("CBAM Risk Calculator")
st.markdown(
    "Assess your financial exposure to the EU **Carbon Border Adjustment Mechanism (CBAM)**, "
    "which entered full implementation on **1 January 2026**. "
    "Designed for Indian exporters across CBAM-covered sectors."
)

st.info(
    "**CBAM Status (as of Jan 2026):** The transitional reporting-only phase has ended. "
    "EU importers must now purchase and surrender CBAM certificates. "
    "Indian exporters bear the indirect cost — either absorbed by the importer or passed back through price negotiations.",
    icon="ℹ️",
)

st.divider()

# ── Section 1: Product & Export ───────────────────────────────────────────────
st.header("1. Product & Export Information")

col1, col2 = st.columns(2)
with col1:
    sector = st.selectbox("CBAM Sector", list(SECTORS.keys()))
    product = st.selectbox("Product Type", list(SECTORS[sector]["products"].keys()))
    unit = SECTORS[sector]["unit"]

with col2:
    volume = st.number_input(
        f"Annual Export Volume to EU ({unit}/year)",
        min_value=0.0, step=100.0, value=1000.0,
    )
    revenue_input = st.number_input(
        "Annual Export Revenue from EU (₹ Crore) — optional, used for % impact",
        min_value=0.0, step=0.5, value=0.0,
    )
    revenue_inr = revenue_input * 1e7

st.divider()

# ── Section 2: Emission Intensity ─────────────────────────────────────────────
st.header("2. Emission Intensity")

intensity_method = st.radio(
    "How do you want to determine your embedded emission intensity?",
    [
        "Use sector default (quick estimate)",
        "Enter my measured / verified intensity",
        "Calculate from activity data (fuel & electricity)",
    ],
    horizontal=True,
)

default_intensity = SECTORS[sector]["products"][product]

if intensity_method == "Use sector default (quick estimate)":
    intensity = default_intensity
    st.success(
        f"**Default intensity for {product}:** {intensity:.3f} tCO₂e/{unit}  \n"
        f"*Source: {SECTORS[sector]['source']}*"
    )

elif intensity_method == "Enter my measured / verified intensity":
    intensity = st.number_input(
        f"Emission Intensity (tCO₂e / {unit})",
        min_value=0.0, value=float(round(default_intensity, 3)),
        step=0.01, format="%.3f",
    )
    st.caption(f"Sector default for reference: {default_intensity:.3f} tCO₂e/{unit} ({SECTORS[sector]['source']})")

else:
    st.markdown("**Enter your annual activity data:**")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("*Fuel Consumption (Scope 1)*")
        fuel_inputs = {}
        for fuel, factor in FUEL_FACTORS.items():
            qty = st.number_input(fuel, min_value=0.0, step=10.0, key=f"fuel_{fuel}")
            fuel_inputs[fuel] = qty

    with col_b:
        st.markdown("*Electricity (Scope 2)*")
        elec_kwh = st.number_input(
            "Total Electricity Consumed (kWh/year)",
            min_value=0.0, step=1000.0,
        )
        production_vol = st.number_input(
            f"Total Annual Production / Output ({unit})",
            min_value=0.01, step=100.0, value=volume,
        )

    scope1 = sum(qty * FUEL_FACTORS[f] for f, qty in fuel_inputs.items())
    scope2 = elec_kwh * ELECTRICITY_FACTOR
    total_emissions_calc = scope1 + scope2
    intensity = total_emissions_calc / production_vol if production_vol > 0 else 0.0

    m1, m2, m3 = st.columns(3)
    m1.metric("Scope 1 (tCO₂e)", f"{scope1:,.1f}")
    m2.metric("Scope 2 (tCO₂e)", f"{scope2:,.1f}")
    m3.metric(f"Calculated Intensity (tCO₂e/{unit})", f"{intensity:.3f}")

st.divider()

# ── Section 3: CBAM Parameters ────────────────────────────────────────────────
st.header("3. CBAM Parameters")

col3, col4, col5 = st.columns(3)
with col3:
    ets_price = st.slider(
        "EU ETS Carbon Price (€/tCO₂e)",
        min_value=20, max_value=150, value=65, step=5,
    )
with col4:
    domestic_price = st.number_input(
        "Domestic Carbon Price recognised by EU (€/tCO₂e)",
        min_value=0.0, max_value=float(ets_price), value=0.0, step=1.0,
    )
    st.caption("India currently has no EU-recognised carbon price. Default = 0.")
with col5:
    eur_inr = st.number_input(
        "EUR / INR Exchange Rate",
        min_value=50.0, max_value=150.0, value=90.0, step=0.5,
    )

boundary_approach = st.selectbox(
    "Organisational Boundary",
    ["Operational Control", "Financial Control", "Equity Share"],
)

st.divider()

# ── Section 4: Results ────────────────────────────────────────────────────────
st.header("4. Results")

if volume <= 0:
    st.warning("Enter a non-zero export volume above to see results.")
else:
    embedded     = volume * intensity
    net_price    = max(ets_price - domestic_price, 0)
    liability_eur = embedded * net_price
    liability_inr = liability_eur * eur_inr
    pct_revenue  = (liability_inr / revenue_inr * 100) if revenue_inr > 0 else None
    risk, risk_color = risk_label(liability_inr, revenue_inr)

    # Key metrics
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Embedded Emissions", f"{embedded:,.1f} tCO₂e/yr")
    mc2.metric("CBAM Certificates", f"{embedded:,.1f}/yr")
    mc3.metric("Annual Liability (€)", f"€{liability_eur:,.0f}")
    mc4.metric("Annual Liability (₹)", fmt_inr(liability_inr))

    if pct_revenue:
        st.caption(f"This represents **{pct_revenue:.1f}%** of your stated EU export revenue.")

    # Risk rating banner
    risk_bg = {"HIGH": "#FDECEA", "MEDIUM": "#FEF9E7", "LOW": "#EAFAF1"}[risk]
    risk_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[risk]
    st.markdown(
        f"""
        <div style="background:{risk_bg}; border-left: 5px solid {risk_color};
                    padding:1rem 1.5rem; border-radius:4px; margin:1rem 0;">
            <span style="font-size:1.2rem; font-weight:700; color:{risk_color};">
                {risk_icon} CBAM Risk: {risk}
            </span><br>
            <span style="font-size:0.88rem; color:#333;">
                {'Annual liability exceeds ₹1 Cr or >10% of EU revenue — material financial impact, immediate action required.' if risk == 'HIGH'
                 else 'Annual liability between ₹25L–₹1 Cr — monitor closely and begin mitigation planning.' if risk == 'MEDIUM'
                 else 'Annual liability below ₹25L — low near-term impact, maintain awareness.'}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Sensitivity analysis
    st.subheader("Sensitivity Analysis")
    sens_df, sens_prices, sens_values = sensitivity_table(embedded, domestic_price, eur_inr)

    chart_col, table_col = st.columns([3, 2])
    with chart_col:
        fig = go.Figure()
        bar_colors_plotly = []
        for v in sens_values:
            if v * 1e7 >= 1e7:
                bar_colors_plotly.append(RED_HEX)
            elif v * 1e7 >= 25e5:
                bar_colors_plotly.append(AMBER_HEX)
            else:
                bar_colors_plotly.append(GREEN_HEX)

        fig.add_trace(go.Bar(
            x=[f"€{p}" for p in sens_prices],
            y=sens_values,
            marker_color=bar_colors_plotly,
            text=[f"₹{v:.2f} Cr" for v in sens_values],
            textposition="outside",
            showlegend=False,
        ))
        current_crore = net_price * embedded * eur_inr / 1e7
        fig.add_hline(
            y=current_crore, line_dash="dash", line_color=OLIVE_HEX,
            annotation_text=f"Current (€{ets_price})", annotation_position="top right",
        )
        fig.update_layout(
            xaxis_title="EU ETS Carbon Price",
            yaxis_title="Annual CBAM Liability (₹ Crore)",
            title="Sensitivity of CBAM Liability to EU ETS Price",
            template="simple_white",
            height=360,
            margin=dict(t=50, b=40, l=60, r=30),
        )
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        st.dataframe(sens_df, hide_index=True, use_container_width=True)

    st.divider()

    # Recommendations
    st.subheader("Recommendations")
    recs = recommendations(sector, risk)
    for i, rec in enumerate(recs, 1):
        st.markdown(f"**{i}.** {rec}")

    st.divider()

    # PDF download
    st.subheader("Download Report")
    pdf_inputs = {
        "sector": sector, "product": product, "volume": volume, "unit": unit,
        "revenue_inr": revenue_inr, "intensity_method": intensity_method,
        "intensity": intensity, "ets_price": ets_price,
        "domestic_price": domestic_price, "eur_inr": eur_inr,
        "boundary": boundary_approach,
    }
    pdf_results = {
        "embedded": embedded, "liability_eur": liability_eur,
        "liability_inr": liability_inr, "risk": risk,
        "pct_revenue": pct_revenue,
    }

    with st.spinner("Generating PDF…"):
        pdf_bytes = generate_pdf(
            pdf_inputs, pdf_results, sens_df,
            sens_prices, sens_values, recs,
        )

    safe_sector = sector.replace(" ", "_").replace("&", "and")
    st.download_button(
        label="⬇  Download CBAM Risk Assessment (PDF)",
        data=pdf_bytes,
        file_name=f"CBAM_Risk_Assessment_{safe_sector}_{date.today()}.pdf",
        mime="application/pdf",
    )

st.divider()
st.markdown(
    """
    **Developed by Arun Venkatraman | Total Impact**
    Sustainability & ESG Advisory | GHG Accounting | CBAM & Regulatory Compliance
    📧 arun@totalimpact.co.in | 📞 +91 6374350144
    """
)
