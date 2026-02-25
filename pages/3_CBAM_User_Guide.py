import streamlit as st

st.set_page_config(page_title="CBAM User Guide & Methodology", layout="wide")

OLIVE = "#6B7C45"
DARK  = "#1F2E12"

st.title("CBAM Risk Calculator — User Guide & Methodology")
st.markdown(
    "A plain-language reference for understanding CBAM, interpreting your results, "
    "and using every section of the calculator correctly."
)
st.divider()

# ──────────────────────────────────────────────────────────────────────────────
st.header("Part 1 — What Is CBAM and Why Does It Matter?")
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
### 1.1 The Problem CBAM Is Solving

The European Union has been putting a price on carbon emissions since 2005 through its **Emissions Trading System (EU ETS)**.
Under the ETS, European manufacturers pay for every tonne of CO₂ they emit. This raises their production costs —
but it also means they have a financial incentive to invest in cleaner processes.

The problem: companies outside the EU — including in India — generally do not face equivalent carbon costs.
This creates what economists call **carbon leakage**: EU buyers may simply switch to cheaper imports from
countries with weaker climate regulations, undermining both EU competitiveness and global emission reduction efforts.

**CBAM — the Carbon Border Adjustment Mechanism — is the EU's solution.** It puts the same carbon price
on imported goods as European producers pay domestically. If you export carbon-intensive goods to the EU,
your EU importer now has to buy and surrender CBAM certificates to cover the carbon embedded in your products.

---

### 1.2 Key Dates

| Milestone | Date |
|---|---|
| Transitional Phase begins (reporting only, no payment) | October 2023 |
| Full Implementation begins (certificates must be purchased) | **1 January 2026** |
| First annual CBAM declaration due | 31 May 2026 |
| Full phase-in of CBAM / phase-out of free ETS allowances for industry | 2034 |

As of **January 2026**, CBAM is fully live. EU importers who bring in CBAM-covered goods **must purchase
CBAM certificates** in proportion to the embedded carbon content of those goods. If they don't, they face
significant penalties under EU regulation.

---

### 1.3 Which Goods Are Covered?

CBAM currently covers six sectors, chosen because they are carbon-intensive and at high risk of carbon leakage:

| Sector | Why It's Covered |
|---|---|
| **Iron & Steel** | Amongst the highest direct emission intensities per tonne |
| **Aluminium** | Highly electricity-intensive; grid carbon content matters greatly |
| **Cement** | Calcination of limestone releases CO₂ chemically, not just from energy |
| **Fertilisers** | Ammonia production is energy-intensive; N₂O emissions are high-GWP |
| **Hydrogen** | Strategic sector for the clean energy transition |
| **Electricity** | Cross-border power trade carries embedded carbon |

Each sector is defined by specific **CN codes** (Combined Nomenclature — the EU's product classification system).
Only goods with those CN codes, exported to the EU, are subject to CBAM. The calculator displays the relevant
CN codes for your selected product.

---

### 1.4 Who Pays — The Importer, or You?

**Legally, the EU importer pays.** They purchase CBAM certificates from the EU registry, one certificate
per tonne of embedded CO₂. However, in practice:

- Many EU importers **negotiate the CBAM cost back** into the price they pay you — your invoice price may be reduced
- Some importers ask suppliers to **absorb part of the cost** to remain competitive
- In competitive markets, suppliers who can demonstrate **lower carbon intensity** have a clear price advantage

This calculator helps you understand the **size of the exposure** so you can negotiate from an informed position.

---

### 1.5 India's Position

India is not among the countries whose carbon pricing systems are currently **recognised by the EU** as
equivalent to the EU ETS. This means Indian exporters receive **no credit** for domestic carbon costs
(the default domestic price in this calculator is €0).

India's domestic carbon market is under development (BEE's PAT scheme and the emerging Carbon Credit
Trading Scheme). If India achieves mutual recognition with the EU in future, the CBAM liability for
Indian exporters would reduce accordingly.
""")

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
st.header("Part 2 — Core Concepts")
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
### 2.1 Embedded Emissions

**Embedded emissions** are the total greenhouse gas (GHG) emissions associated with producing a good —
not just the emissions at the factory gate, but also the emissions embedded in the materials that went
into making it.

CBAM breaks embedded emissions into two layers:

**Layer 1 — Direct emissions** (always required)
> The GHG emissions from your own production process: burning fuels, calcination reactions,
process chemical reactions, and electricity consumption.

**Layer 2 — Precursor embedded emissions** (required for complex goods)
> The GHG emissions that were emitted when producing the input materials (precursors) you bought
and used. For example: if you make cold-rolled steel, the hot-rolled coil you purchased already
carries embedded carbon from the upstream rolling mill. Under CBAM, that carbon travels with the product.

**Total Embedded Emissions = Direct Emissions + Precursor Embedded Emissions**

For simple goods (e.g. clinker, pig iron, ammonia), only direct emissions are required.
For complex goods (e.g. cold-rolled steel, urea, semi-fabricated aluminium), precursors matter too.

---

### 2.2 CBAM Certificates

CBAM certificates are purchased by EU importers from the EU CBAM registry. The price of one certificate
equals the weekly average price of EU ETS allowances (in €/tCO₂e). One certificate covers one tonne of
embedded CO₂e in the imported goods.

**CBAM Certificates Required = Total Embedded Emissions (tCO₂e)**

The EU importer surrenders these certificates annually with their CBAM declaration. If the exporting
country has a carbon price already recognised by the EU, the importer can deduct certificates equivalent
to the carbon cost already paid in the country of origin.

---

### 2.3 CN Codes

**Combined Nomenclature (CN) codes** are the EU's 8-digit product classification system, used for customs
and trade statistics. CBAM applies only to goods with CN codes listed in **Annex I of Regulation (EU) 2023/956**.

When you export to the EU, your shipment's customs declaration includes a CN code. CBAM liability is
triggered when that CN code is on the CBAM list. The calculator shows you the applicable CN codes for
your selected product so you can verify whether your exports fall in scope.

---

### 2.4 Emission Intensity

Emission intensity is the amount of CO₂e emitted per unit of production:

> **Emission Intensity = Total GHG Emissions ÷ Total Production Output**
> (expressed as tCO₂e per tonne of product, or tCO₂e per MWh for electricity)

The lower your emission intensity, the lower your CBAM liability per tonne exported.
This is why energy efficiency and fuel switching directly reduce your CBAM exposure.

---

### 2.5 The Net Carbon Price

The CBAM certificate cost is not simply the EU ETS price. It is:

> **Net Carbon Price = EU ETS Price − Domestic Carbon Price (if EU-recognised)**

Since India's carbon pricing is not currently EU-recognised, the net price for Indian exporters
equals the full EU ETS price. If India achieves recognition in future, the net price — and your
liability — would reduce.

---

### 2.6 Risk Rating — How It Works

The calculator assigns one of three risk levels based on your annual CBAM liability:

| Rating | Condition |
|---|---|
| 🔴 **HIGH** | Liability ≥ ₹1 Crore **OR** >10% of EU export revenue |
| 🟡 **MEDIUM** | Liability ≥ ₹25 Lakh **OR** >3% of EU export revenue |
| 🟢 **LOW** | Liability below both thresholds |

The dual threshold (absolute ₹ value + % of revenue) ensures the rating reflects both the
absolute financial exposure and the relative materiality to your EU business.
""")

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
st.header("Part 3 — Methodology")
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
### 3.1 The Core Calculation

The calculator uses this chain of formulas:

```
Step 1 — Direct Embedded Emissions
Direct Emissions (tCO₂e/yr) = Export Volume (t/yr) × Direct Emission Intensity (tCO₂e/t)

Step 2 — Precursor Embedded Emissions (if applicable)
Precursor Emissions (tCO₂e/yr) = Σ [ Precursor Quantity (t/yr) × Precursor Emission Intensity (tCO₂e/t) ]

Step 3 — Total Embedded Emissions
Total Embedded (tCO₂e/yr) = Direct Emissions + Precursor Emissions

Step 4 — CBAM Liability
Liability (€/yr) = Total Embedded × max( EU ETS Price − Domestic Price, 0 )
Liability (₹/yr) = Liability (€/yr) × EUR/INR Exchange Rate

Step 5 — Revenue Impact (optional)
Revenue Impact (%) = Liability (₹) ÷ EU Export Revenue (₹) × 100
```

---

### 3.2 Emission Intensity Methods

The calculator offers three ways to determine your direct emission intensity. Choose the one that best
matches the data you have available.

#### Method A — Sector Default (Quick Estimate)
Pre-loaded values based on India-specific benchmarks from authoritative sources (IEA, BEE, IAI, CMA, IFA).
These represent **average Indian production conditions** and are appropriate for a first-pass assessment.
They are likely to **overestimate** your actual intensity if your plant is more efficient than the sector
average, and may **underestimate** it if your plant uses more fossil fuel than average.

**Use this when:** You want a quick indication of exposure and don't yet have plant-level data.

#### Method B — Measured / Verified Intensity
You enter your own emission intensity figure, ideally from a verified GHG inventory or third-party audit.
This is the most defensible method under CBAM's actual reporting requirements and will give you
the most accurate liability estimate.

**Use this when:** You have conducted a GHG inventory, have BEE/ISO 14064 certified data, or
have previously prepared CBAM transitional period reports.

#### Method C — Calculate from Activity Data
You enter annual fuel consumption (by fuel type) and electricity consumption. The calculator applies
published emission factors to derive total Scope 1 and Scope 2 emissions, then divides by your
production volume to arrive at an intensity figure.

Emission factors used:

| Fuel / Energy | Factor | Source |
|---|---|---|
| Diesel | 0.00268 tCO₂e/litre | MoEFCC India |
| LPG | 0.00161 tCO₂e/kg | MoEFCC India |
| Natural Gas | 0.00200 tCO₂e/SCM | MoEFCC India |
| Coal | 0.00242 tCO₂e/kg | MoEFCC India |
| Furnace Oil / HSD | 0.00315 tCO₂e/litre | MoEFCC India |
| Petrol | 0.00231 tCO₂e/litre | MoEFCC India |
| Electricity (India grid) | 0.000716 tCO₂e/kWh | CEA CO₂ Baseline 2022-23 |

**Use this when:** You have utility bills and fuel purchase records but have not yet formalised a GHG inventory.

---

### 3.3 Precursor Emission Methodology

The CBAM Implementing Regulation requires that for **complex goods**, the embedded emissions of
CBAM-covered precursor materials are included in the total embedded emission calculation.

The calculator provides pre-loaded precursor data for each product, including:
- **Default emission intensity** of the precursor (from sector LCA databases)
- **Typical consumption ratio** (how many tonnes of precursor per tonne of output — a starting point)

Users can and should edit both the quantity and the intensity for each precursor:
- **Quantity**: Change to your actual annual purchase / consumption of that input
- **Intensity**: Change if you know your specific supplier's carbon intensity (e.g. you source
  green aluminium ingots with a verified lower footprint)

**Key precursor relationships covered:**

| Output Product | Key Precursor | Why It Matters |
|---|---|---|
| Cold-rolled steel | Hot-rolled coil | Carries full upstream BF-BOF embedded carbon |
| Stainless steel | Ferro-alloys (Cr, Ni, Mn) | High-carbon alloys; intensity 3–8 tCO₂e/t |
| EAF rebar | Scrap steel + DRI | Coal-based DRI (India) has ~0.7 tCO₂e/t |
| Urea | Ammonia | ~0.57 t NH₃ per t urea; largest embedded source |
| Ammonium nitrate | Nitric acid | N₂O from Ostwald process drives high intensity |
| OPC cement | Clinker | Calcination = ~0.87 tCO₂e/t; clinker ratio is key lever |
| Primary aluminium | Alumina | ~1.93 t alumina per t Al; Bayer process energy |
| Semi-fab aluminium | Primary ingot | Upstream smelter footprint dominates |

---

### 3.4 Sensitivity Analysis

The sensitivity table and chart show your CBAM liability across six EU ETS price scenarios:
€30, €50, €70, €90, €110, and €130 per tonne of CO₂e.

**Why this matters:** The EU ETS price has ranged from €25 to €100 in recent years and is
subject to significant volatility. By showing liability at multiple price points, the calculator
helps you stress-test your exposure and understand your worst-case scenario.

The dashed horizontal line on the chart marks your liability at the **currently selected ETS price**.
Bar colours follow the risk rating logic (green = LOW, amber = MEDIUM, red = HIGH).

---

### 3.5 Data Sources

| Sector | Source |
|---|---|
| Iron & Steel | IEA India Steel Sector Report; BEE PAT Scheme Benchmarks (2022-23); World Steel Association |
| Aluminium | International Aluminium Institute (IAI) Life Cycle Assessment; CEA Grid Emission Factor (2022-23) |
| Cement | Cement Sustainability Initiative (CSI) GNR Database; Cement Manufacturers Association (CMA) India |
| Fertilisers | International Fertilizer Association (IFA); IPCC N₂O emission factors; Yara LCA data |
| Hydrogen | IRENA; IEA Hydrogen Report (2022) |
| Electricity | Central Electricity Authority (CEA) CO₂ Baseline Database (2022-23) |
| Precursors — General | IAI, ISSF, Outokumpu LCA; BEE India; Midrex / SPONGE India |
| Fuel Emission Factors | Ministry of Environment, Forest & Climate Change (MoEFCC), India |
""")

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
st.header("Part 4 — Step-by-Step Guide to Using the Calculator")
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("Navigate to the **CBAM Risk Calculator** page using the sidebar. Then follow these steps.")

with st.expander("**STEP 1 — Product & Export Information**", expanded=True):
    st.markdown("""
**What this section does:** Tells the calculator what you make, how much you export to the EU, and what your EU business is worth.

---

**Field: CBAM Sector**
Select the broad sector your product falls under. Options: Iron & Steel, Aluminium, Cement, Fertilisers, Hydrogen, Electricity.
If your product could fit more than one sector, choose based on your primary export product.

---

**Field: Product Type**
Select the specific product variant you export. This matters because different product types within a
sector have different default emission intensities and different CN code requirements.

For example, within Iron & Steel:
- *Hot-rolled flat products (BF-BOF route)* → typical of integrated steel mills
- *Structural steel / Rebar (EAF route)* → typical of electric arc furnace mini-mills

If your product isn't listed exactly, choose the closest match and use Method B or C for emission intensity
(entering your actual data) rather than relying on the default.

---

**Field: CN Code display**
After selecting your product, the applicable EU Combined Nomenclature codes appear automatically.
Cross-check these against the CN codes on your export customs documentation (shipping invoices, bill of
lading, DGFT forms) to confirm your exports are CBAM-in-scope. If your CN codes don't appear in the list,
your goods may not be covered by CBAM at this time.

---

**Field: Annual Export Volume to EU (tonnes/year)**
Enter the total quantity you exported — or plan to export — to the EU in a year, in tonnes (or MWh for electricity).
Use your EU-specific volume, not your total production. If you export to multiple EU countries, sum them all.

*Where to find this:* Shipping records, export invoices, DGFT export data, logistics company reports.

---

**Field: Annual Export Revenue from EU (₹ Crore) — optional**
Enter the total value of your EU exports in ₹ Crore. This is optional but enables the calculator to
show you the CBAM liability as a **% of your EU revenue** — often the most meaningful way to gauge materiality.

*Where to find this:* Your accounts / export billing records. Convert from € or USD using the prevailing exchange rate.
Leave at 0 if you don't have this figure — the calculator will still show absolute ₹ liability.
""")

with st.expander("**STEP 2 — Direct Emission Intensity**", expanded=True):
    st.markdown("""
**What this section does:** Establishes how carbon-intensive your production process is, per tonne of output.

Choose one of three methods:

---

**Method A: Use sector default (quick estimate)**

The calculator pre-fills the emission intensity with an India-average benchmark for your product type.
No additional input needed. A green info box shows the value and the data source.

*When to use:* First-pass screening; you don't yet have plant-level emission data.

*Limitation:* This is an industry average. Your actual intensity may be higher or lower. If your plant
is older, coal-heavy, or less efficient than the sector average, the default likely **understates** your exposure.
If you have invested in energy efficiency, it likely **overstates** it.

---

**Method B: Enter my measured / verified intensity**

A number input appears showing the sector default pre-filled. Overwrite it with your own figure.

*What to enter:* Your tCO₂e per tonne of product, ideally from:
- A third-party verified GHG inventory (ISO 14064, GHG Protocol)
- A BEE PAT scheme energy audit
- CBAM transitional period reports you have already prepared
- Internal energy/fuel records divided by production volume

*The sector default is shown as a caption for reference.*

---

**Method C: Calculate from activity data (fuel & electricity)**

Enter your annual consumption of each fuel type and total electricity consumed, plus your total annual production volume.

*Fuel inputs:* Enter the quantity purchased/consumed during the year. If a fuel is not used, leave it at 0.
- Diesel: in litres
- LPG: in kg
- Natural Gas: in Standard Cubic Metres (SCM) — check your gas utility bill
- Coal: in kg (convert from tonnes: 1 tonne = 1,000 kg)
- Furnace Oil / HSD: in litres
- Petrol: in litres

*Electricity:* Total units (kWh) consumed from the grid during the year. Read from your electricity bills.
Do NOT include captive renewable electricity if it has a near-zero emission factor — or enter it separately
once this feature is added.

*Total Annual Production:* Your total plant output in tonnes during the same year as the consumption data.
This is used to derive the intensity (emissions ÷ output). It should cover all production, not just the
EU-export portion — because emission intensity is a property of the production process, not the destination market.

*The calculator shows you Scope 1, Scope 2, and the derived intensity as output metrics.*
""")

with st.expander("**STEP 3 — Precursor Embedded Emissions**", expanded=True):
    st.markdown("""
**What this section does:** Adds the carbon embedded in your input raw materials to your total embedded emission figure.

This section only appears with meaningful options for **complex goods**. If your product is a simple good
(e.g. clinker, pig iron, ammonia, pure hydrogen), a note appears saying no CBAM precursors apply and
you can skip to the next section.

---

**The precursor multiselect**

All relevant precursors for your selected product are shown. By default, all are selected.
**De-select any precursor that you do not actually use** in your production process.

*Example:* If you make EAF rebar using only scrap (no DRI), de-select "Direct Reduced Iron (DRI / Sponge Iron)".

---

**For each selected precursor, an expandable panel appears with:**

**Quantity used (tonnes/year)**
The field is pre-filled with an estimate based on the typical consumption ratio for that precursor
(e.g. ~1.93 tonnes of alumina per tonne of primary aluminium). This is a starting point only.

*Replace this with your actual annual purchase / consumption of that material.*
*Where to find it:* Purchase orders, raw material ledgers, production records, material balance reports.

**Emission intensity (tCO₂e/tonne)**
Pre-filled with a sector-average intensity for that precursor material. This is what the calculator uses
to estimate how much carbon was emitted when producing the material you purchased.

*Ideally, replace this with your supplier's verified emission intensity* — particularly for major inputs
like primary aluminium ingot (which can vary enormously based on the smelter's electricity source:
coal grid vs hydro vs solar). A supplier with a verified low-carbon footprint can meaningfully
reduce your CBAM liability.

**Embedded Emissions metric**
Shows the tCO₂e/year contributed by that specific precursor (quantity × intensity), updated live.

---

**Total precursor emissions**
A green summary box shows the sum of embedded emissions across all selected precursors. This is
added to your direct emissions in Step 5.

---

*Note on what counts as a CBAM precursor:*
Not every input material is a CBAM precursor. Only inputs that are themselves CBAM-covered goods
(i.e. appear in Annex I of Regulation (EU) 2023/956) need to be tracked as precursors. The
calculator only lists inputs that meet this criterion. General consumables, water, packaging,
and non-CBAM raw materials are not included.
""")

with st.expander("**STEP 4 — CBAM Parameters**", expanded=True):
    st.markdown("""
**What this section does:** Sets the carbon pricing and exchange rate assumptions for your liability calculation.

---

**EU ETS Carbon Price (€/tCO₂e)**
Use the slider to set the carbon price assumption. The current price can be found on the
EU ETS price tracking websites (e.g. Ember, Sandbag, ICE exchange).

For planning and risk assessment purposes, it is advisable to run the calculator at multiple
price points — the sensitivity analysis in the results section does this automatically.

*As a reference:*
- 2022 peak: ~€98/tCO₂e
- 2023 average: ~€83/tCO₂e
- 2024 average: ~€60–65/tCO₂e
- Long-run forecasts (industry consensus): €80–120/tCO₂e by 2030

---

**Domestic Carbon Price recognised by EU (€/tCO₂e)**
This is the carbon price India's exporters are assumed to already "pay" — which the EU would
deduct from the CBAM certificate cost.

**Leave this at 0 for Indian exporters.** India's existing carbon pricing mechanisms (PAT, CCTS)
are not currently recognised as equivalent by the EU. This may change as India's Carbon Credit
Trading Scheme (CCTS) matures and bilateral negotiations progress.

---

**EUR / INR Exchange Rate**
Enter the current or expected exchange rate (₹ per €1). The default is ₹90/€ — adjust to the
current market rate or your company's hedged rate for more accurate ₹ liability figures.

*As of early 2026, the rate is approximately ₹88–92/€.*

---

**Organisational Boundary**
Select the boundary approach that matches how your company consolidates GHG emissions:

- **Operational Control:** Include all facilities over which you have operational control
  (ability to implement operating policies). Most common for MSMEs.
- **Financial Control:** Include all facilities where you have financial control
  (ability to direct financial and operating policies to gain economic benefits).
- **Equity Share:** Include emissions in proportion to your equity share in each operation.

This field is recorded in the PDF report for reference. For most single-site Indian SMEs,
Operational Control is the appropriate choice.
""")

with st.expander("**STEP 5 — Reading Your Results**", expanded=True):
    st.markdown("""
**What this section shows:** Your calculated CBAM liability, risk rating, sensitivity to price changes, and actionable recommendations.

---

**Emissions Breakdown (if precursors selected)**

Three metrics appear at the top:
- *Direct Production Emissions*: Emissions from your own process (volume × intensity)
- *Precursor Embedded Emissions*: Sum of emissions from your input materials
- *Total Embedded Emissions*: The sum — this is what CBAM applies to

If no precursors are selected, only Total Embedded Emissions is shown.

---

**Liability Metrics (four columns)**

- *CBAM Certificates Required*: Equal to Total Embedded Emissions in tCO₂e. This is the number
  of certificates your EU importer must surrender.
- *Net Carbon Price*: EU ETS Price minus Domestic Carbon Price. For India this equals the full ETS price.
- *Annual Liability (€)*: Certificates × Net Price. This is the cost to your EU importer.
- *Annual Liability (₹)*: The same cost converted to ₹ at your specified exchange rate.

If you entered revenue, a caption shows the liability as a % of revenue.

---

**Risk Rating Banner**

🔴 HIGH / 🟡 MEDIUM / 🟢 LOW — see Section 2.6 for the thresholds.
Read the text in the banner for a plain-language summary of what the rating means for your business.

---

**Sensitivity Analysis**

A bar chart and table show your liability across six ETS price scenarios (€30 to €130).
- Bars are colour-coded by risk level (green/amber/red)
- The dashed line shows liability at your currently selected ETS price
- The table shows both € and ₹ liability at each price point

Use this to understand:
- At what ETS price does your risk move from LOW to MEDIUM?
- What is your worst-case exposure if ETS reaches €130?

---

**Recommendations**

A numbered list of tailored actions, based on your risk level and sector. Covers:
- Data and measurement actions (GHG inventory, verified data)
- Regulatory compliance (CBAM registry, transitional reporting)
- Commercial actions (contract clauses, buyer engagement)
- Emission reduction levers specific to your sector

---

**Download PDF**

Click the download button to generate a PDF report containing all inputs, results, sensitivity
analysis, and recommendations. The PDF is formatted for sharing with management, EU buyers,
or financial institutions.

*The PDF is generated fresh each time you click the button, reflecting your current inputs.*
""")

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
st.header("Part 5 — Limitations and Important Caveats")
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
This calculator is a **screening and awareness tool**. It is not a substitute for formal CBAM compliance
reporting or verified GHG accounting. Please note the following limitations:

**1. Sector defaults are averages, not your specific plant.**
The pre-loaded emission intensities reflect India-average production conditions as of 2022-23.
If your plant is significantly more or less efficient than the sector average, use Method B or C
for a more accurate estimate.

**2. Precursor data uses typical ratios.**
The consumption ratios (tonnes of precursor per tonne of output) are representative of typical
production conditions. Actual ratios depend on your specific process, technology, and raw material mix.
Replace defaults with your actual purchase and production data for higher accuracy.

**3. CBAM regulation is still evolving.**
The EU is publishing implementing acts, guidance, and methodological updates through 2026 and beyond.
Default values and methodology in this calculator will be updated periodically, but may not always
reflect the very latest regulatory guidance. Always check the official EU CBAM registry and Directorate
General TAXUD publications for authoritative guidance.

**4. Indirect emissions from electricity (for non-electricity sectors) use a fixed grid factor.**
The electricity emission factor used (0.000716 tCO₂e/kWh) is the CEA 2022-23 average for the Indian grid.
If you use captive renewable power, the actual factor is much lower. Adjust accordingly in Method C.

**5. This tool covers embedded emissions only — not transport or logistics emissions.**
CBAM does not (currently) cover Scope 3 supply chain emissions beyond the defined precursor boundary.

**6. The calculator does not replace legal or compliance advice.**
CBAM has specific procedural requirements for EU importers including registration, declaration,
data verification, and certificate surrender. Consult a qualified CBAM advisor or the EU CBAM registry
guidance before submitting official declarations.
""")

st.divider()

# ──────────────────────────────────────────────────────────────────────────────
st.header("Part 6 — Glossary")
# ──────────────────────────────────────────────────────────────────────────────

glossary = {
    "CBAM (Carbon Border Adjustment Mechanism)":
        "An EU regulation (Regulation (EU) 2023/956) that requires EU importers of certain carbon-intensive "
        "goods to purchase certificates equivalent to the carbon price that would have been paid under EU carbon pricing rules. "
        "Fully in force from 1 January 2026.",

    "CBAM Certificate":
        "A digital instrument purchased by EU importers from the EU CBAM registry. One certificate = one tonne of "
        "embedded CO₂e in the imported goods. Certificates must be surrendered annually with the importer's CBAM declaration. "
        "The price of a CBAM certificate tracks the weekly average EU ETS price.",

    "CN Code (Combined Nomenclature)":
        "The EU's 8-digit product classification system used for customs, trade statistics, and tariffs. "
        "CBAM applies only to goods with CN codes listed in Annex I of Regulation (EU) 2023/956. "
        "Your export customs documentation should reference the applicable CN codes.",

    "CO₂e (CO₂ equivalent)":
        "A unit that expresses the global warming potential of different greenhouse gases in terms of the "
        "equivalent amount of CO₂ that would cause the same warming over 100 years. For example, 1 tonne "
        "of methane (CH₄) = ~25 tCO₂e; 1 tonne of N₂O = ~298 tCO₂e.",

    "Complex Good":
        "Under CBAM, a good whose embedded emissions must include not just its own direct production emissions, "
        "but also the emissions embedded in CBAM-covered precursor materials used to make it. "
        "Examples: cold-rolled steel, urea, ammonium nitrate, semi-fabricated aluminium.",

    "Direct Emissions":
        "GHG emissions from sources owned or controlled by the producer — burning fuels, process reactions, "
        "and electricity consumption at the plant. In GHG Protocol terms, this covers Scope 1 and Scope 2.",

    "Domestic Carbon Price":
        "The carbon cost already paid by an exporter in their home country, which the EU deducts from the "
        "CBAM certificate obligation. India currently has no EU-recognised domestic carbon price (= €0).",

    "DRI (Direct Reduced Iron)":
        "Also called sponge iron. Iron ore reduced to metallic iron without melting, using natural gas or "
        "coal as the reductant. A key feedstock for electric arc furnaces. India's DRI is predominantly "
        "coal-based, carrying ~0.7 tCO₂e/tonne intensity.",

    "EAF (Electric Arc Furnace)":
        "A steelmaking process that melts steel scrap (and/or DRI) using electric arc heat. "
        "More flexible than the BF-BOF route and can use renewable electricity. "
        "Typically lower emission intensity than integrated BF-BOF mills (~1.0–1.8 tCO₂e/t vs 2.0–2.5 tCO₂e/t).",

    "Embedded Emissions":
        "The total GHG emissions associated with producing a good, including both direct production emissions "
        "and the emissions from CBAM-covered precursor materials. This is the quantity CBAM applies to.",

    "Emission Factor":
        "A coefficient that converts an activity (litres of diesel burned, kWh of electricity consumed) into "
        "a quantity of GHG emissions (tCO₂e). Published by national and international bodies (MoEFCC, CEA, IPCC).",

    "Emission Intensity":
        "GHG emissions per unit of production output (e.g. tCO₂e per tonne of steel, tCO₂e per MWh of electricity). "
        "The lower the intensity, the lower the CBAM liability per unit exported.",

    "EU ETS (EU Emissions Trading System)":
        "The EU's cap-and-trade carbon market, operational since 2005. EU manufacturers must buy allowances "
        "for their emissions. The market-determined price of these allowances forms the basis of the CBAM certificate price.",

    "BF-BOF (Blast Furnace – Basic Oxygen Furnace)":
        "The integrated steelmaking route: iron ore is reduced in a blast furnace using coke (coal) to produce "
        "pig iron, which is then converted to steel in a basic oxygen furnace. High emission intensity "
        "(2.0–2.5 tCO₂e/tonne) due to coal use.",

    "GHG (Greenhouse Gas)":
        "Gases that trap heat in the atmosphere: CO₂, CH₄, N₂O, HFCs, PFCs, SF₆, NF₃. "
        "CBAM covers all GHGs expressed as CO₂ equivalents (CO₂e).",

    "GHG Protocol":
        "The most widely used international standard for corporate GHG accounting and reporting, "
        "developed by the World Resources Institute (WRI) and World Business Council for Sustainable "
        "Development (WBCSD). Defines Scope 1, 2, and 3 emissions.",

    "Grey Hydrogen":
        "Hydrogen produced from natural gas via steam methane reforming (SMR) without carbon capture. "
        "Most hydrogen produced today is grey. High emission intensity (~10 tCO₂e/tonne H₂).",

    "Green Hydrogen":
        "Hydrogen produced by electrolysis of water using renewable electricity. Near-zero emissions "
        "(~0.5 tCO₂e/tonne when using renewable power). Carries near-zero CBAM liability.",

    "Clinker Factor":
        "The proportion of clinker in a cement blend, expressed as a fraction. OPC has a high clinker "
        "factor (~0.92–0.97); blended cements (PPC, slag cement) have lower clinker factors, resulting "
        "in lower embedded emission intensity.",

    "N₂O (Nitrous Oxide)":
        "A powerful greenhouse gas (GWP = 298 tCO₂e/tonne N₂O) emitted as a by-product of the Ostwald "
        "process in nitric acid production. N₂O emissions are the primary reason ammonium nitrate has "
        "a very high CBAM embedded emission intensity (~8 tCO₂e/tonne).",

    "Operational Control (Boundary Approach)":
        "A GHG accounting boundary approach where a company reports 100% of emissions from all operations "
        "over which it has the authority to implement operating policies. The most common approach for Indian MSMEs.",

    "PAT (Perform Achieve Trade)":
        "India's mandatory energy efficiency scheme for large energy-intensive industries, administered by "
        "BEE (Bureau of Energy Efficiency). PAT scheme data can be a useful source of energy benchmarks "
        "for GHG calculations.",

    "Precursor":
        "A CBAM-covered input material used to produce a complex good. Its embedded emissions must be "
        "included in the total embedded emission calculation. Only inputs that are themselves on the CBAM "
        "Annex I list qualify as precursors under the regulation.",

    "Scope 1 Emissions":
        "Direct GHG emissions from sources owned or controlled by the organisation — burning fuels in "
        "furnaces, boilers, vehicles; process reactions such as calcination; fugitive emissions from "
        "equipment. Scope 1 is always included in CBAM embedded emissions.",

    "Scope 2 Emissions":
        "Indirect GHG emissions from the generation of purchased electricity, steam, heat, or cooling "
        "consumed by the organisation. In the CBAM context, the electricity emission factor of the grid "
        "(or captive source) determines the Scope 2 contribution to embedded emissions.",

    "Sensitivity Analysis":
        "An analysis showing how the output (CBAM liability) changes as a key input assumption (EU ETS price) "
        "is varied. Helps identify the range of potential outcomes and understand which scenarios are most material.",

    "Simple Good":
        "Under CBAM, a good whose embedded emissions consist only of direct production emissions — no "
        "precursor embedded emissions need to be tracked. Examples: clinker, pig iron, ammonia, hydrogen.",

    "SMR (Steam Methane Reforming)":
        "The dominant process for producing hydrogen from natural gas. Natural gas reacts with steam at "
        "high temperature to produce hydrogen and CO₂. Without carbon capture, this produces grey hydrogen.",

    "Sponge Iron":
        "See DRI (Direct Reduced Iron). Term commonly used in India for coal-based DRI.",

    "Transitional Period":
        "The CBAM transitional period ran from October 2023 to December 2025. During this period, EU "
        "importers were required to report embedded emissions quarterly but did not yet need to purchase "
        "certificates. The full obligation (reporting + certificate purchase) began 1 January 2026.",
}

for term, definition in sorted(glossary.items()):
    with st.expander(f"**{term}**"):
        st.markdown(definition)

st.divider()
st.markdown(
    """
    **Developed by Arun Venkatraman | Total Impact**
    Sustainability & ESG Advisory | GHG Accounting | CBAM & Regulatory Compliance
    📧 arun@totalimpact.co.in | 📞 +91 6374350144
    """
)
