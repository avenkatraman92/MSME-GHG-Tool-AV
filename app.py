import pandas as pd
import streamlit as st
from io import BytesIO

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

st.set_page_config(page_title="MSME GHG Tool", layout="wide")

st.title("MSME GHG Data Collection Tool")
st.write(
    "This tool is designed for MSME data collection for Scope 1 and Scope 2 inventory preparation. "
    "It supports multi-unit businesses and creates a structured workbook for consulting-led GHG assessment."
)

st.header("1. Company Profile")
col1, col2 = st.columns(2)

with col1:
    company_name = st.text_input("Company Name")
    udyam_id = st.text_input("UDYAM ID")
    industry = st.text_input("Industry")
    nic_code = st.text_input("NIC Code (India)")

with col2:
    isic_code = st.text_input("International Industry Code (ISIC)")
    msme_class = st.selectbox("MSME Classification", ["Micro", "Small", "Medium"])
    turnover = st.number_input("Annual Turnover (INR)", min_value=0.0, step=100000.0)
    reporting_year = st.selectbox("Reporting Year", ["2023-24", "2024-25", "2025-26"])

st.subheader("Employees")
col3, col4 = st.columns(2)
with col3:
    perm_m = st.number_input("Permanent Employees - Male", min_value=0, key="perm_m")
    perm_f = st.number_input("Permanent Employees - Female", min_value=0, key="perm_f")
with col4:
    cont_m = st.number_input("Contract Employees - Male", min_value=0, key="cont_m")
    cont_f = st.number_input("Contract Employees - Female", min_value=0, key="cont_f")

st.header("2. Units Setup")
number_of_units = st.number_input(
    "How many operational units/facilities should be covered?",
    min_value=1,
    max_value=20,
    value=1,
    step=1,
)

UNIT_SOURCE_CATALOG = {
    "DG Set": ("Stationary Combustion", "Diesel Consumption", "Litres", "Fuel purchase bills", "Scope 1"),
    "Boiler": ("Stationary Combustion", "Fuel Consumption", "kg / Litres / SCM", "Fuel purchase and logbooks", "Scope 1"),
    "Furnace": ("Stationary Combustion", "Fuel Consumption", "kg / Litres / SCM", "Fuel purchase and process logs", "Scope 1"),
    "Thermic Fluid Heater": ("Stationary Combustion", "Fuel Consumption", "kg / Litres / SCM", "Fuel purchase and maintenance logs", "Scope 1"),
    "Kiln / Oven": ("Stationary Combustion", "Fuel Consumption", "kg / Litres / SCM", "Fuel purchase and production logs", "Scope 1"),
    "Process Steam Generation": ("Stationary Combustion", "Fuel Consumption", "kg / Litres / SCM", "Steam generation and fuel records", "Scope 1"),
    "Industrial HVAC": ("Fugitive Emissions", "Refrigerant Refill / Leakage", "kg/year", "Service and maintenance records", "Scope 1"),
    "Air Conditioners": ("Fugitive Emissions", "Refrigerant Refill / Leakage", "kg/year", "AMC/service records", "Scope 1"),
    "Chillers": ("Fugitive Emissions", "Refrigerant Refill / Leakage", "kg/year", "Service and maintenance records", "Scope 1"),
    "Cold Storage / Refrigeration": ("Fugitive Emissions", "Refrigerant Refill / Leakage", "kg/year", "Maintenance and gas refill records", "Scope 1"),
    "Fire Suppression Systems": ("Fugitive Emissions", "Refill Quantity", "kg/year", "Inspection and refill records", "Scope 1"),
    "Welding with CO2 shielding gas": ("Process / Fugitive", "CO2 Consumption", "kg/month", "Purchase invoices and usage logs", "Scope 1"),
    "LPG/CNG used in process": ("Stationary Combustion", "Fuel Consumption", "kg / SCM", "Fuel purchase bills", "Scope 1"),
    "Electricity Consumption": ("Purchased Electricity", "Electricity Consumption", "kWh", "Electricity bills", "Scope 2"),
}

VEHICLE_SOURCE_CATALOG = {
    "Two-wheelers (Petrol)": ("Mobile Combustion", "Petrol Consumption", "Litres", "Fuel logs / bills", "Scope 1"),
    "Cars (Petrol)": ("Mobile Combustion", "Petrol Consumption", "Litres", "Fuel logs / bills", "Scope 1"),
    "Cars (Diesel)": ("Mobile Combustion", "Diesel Consumption", "Litres", "Fuel logs / bills", "Scope 1"),
    "Light Commercial Vehicles": ("Mobile Combustion", "Diesel/CNG Consumption", "Litres / kg", "Fuel logs / bills", "Scope 1"),
    "Heavy Commercial Vehicles": ("Mobile Combustion", "Diesel Consumption", "Litres", "Fuel logs / bills", "Scope 1"),
    "Forklifts / Material Handling": ("Mobile Combustion", "Fuel/Energy Consumption", "Litres / kWh", "Fuel logs / charging logs", "Scope 1"),
}

HO_SOURCE_CATALOG = {
    "Head Office Electricity": ("Purchased Electricity", "Electricity Consumption", "kWh", "Electricity bills", "Scope 2"),
    "Head Office AC / Refrigerants": ("Fugitive Emissions", "Refrigerant Refill / Leakage", "kg/year", "AMC/service records", "Scope 1"),
    "Head Office DG Set": ("Stationary Combustion", "Diesel Consumption", "Litres", "Fuel purchase records", "Scope 1"),
}

units_data = []
for i in range(number_of_units):
    unit_no = i + 1
    with st.expander(f"Unit {unit_no} Profile and Module", expanded=(i == 0)):
        c1, c2 = st.columns(2)
        with c1:
            unit_name = st.text_input("Unit Name", value=f"Unit {unit_no}", key=f"unit_name_{i}")
            unit_location = st.text_input("Location (City/State)", key=f"unit_location_{i}")
            unit_area = st.number_input("Area (sq ft)", min_value=0.0, step=100.0, key=f"unit_area_{i}")
        with c2:
            unit_ownership = st.selectbox(
                "Ownership",
                ["Fully Owned", "Partly Owned", "Leased", "Contract Manufacturing"],
                key=f"unit_ownership_{i}",
            )
            principal_process = st.text_input("Primary production process", key=f"unit_process_{i}")
            annual_production = st.text_input("Annual production / throughput (optional)", key=f"unit_production_{i}")

        st.caption(
            "Unit module covers stationary combustion, fugitive emissions, and purchased electricity. "
            "Do not include vehicle fuel use here; vehicles are captured in the overall module."
        )

        selected_sources = st.multiselect(
            "Select machinery / process sources applicable for this unit",
            list(UNIT_SOURCE_CATALOG.keys()),
            key=f"unit_sources_{i}",
        )

        include_general_fuel = st.checkbox(
            "Include general stationary fuel use (exclude vehicle fuels)",
            key=f"include_general_fuel_{i}",
        )

        general_fuels = []
        if include_general_fuel:
            general_fuels = st.multiselect(
                "Select general stationary fuels",
                ["Diesel", "LPG", "Natural Gas", "Coal", "Biomass", "FO/HSD", "Other"],
                key=f"general_fuels_{i}",
            )

        units_data.append(
            {
                "unit_name": unit_name,
                "location": unit_location,
                "area_sqft": unit_area,
                "ownership": unit_ownership,
                "primary_process": principal_process,
                "annual_production": annual_production,
                "selected_sources": selected_sources,
                "general_fuels": general_fuels,
            }
        )

st.header("3. Overall Module (Common / Shared Sources)")
st.caption(
    "Capture mobile combustion (vehicles) and head-office emissions not already included at unit level."
)

vehicle_sources = st.multiselect(
    "Vehicle emissions sources (common/shared across units)",
    list(VEHICLE_SOURCE_CATALOG.keys()),
)

ho_sources = st.multiselect(
    "Head office / common electricity and fugitive sources",
    list(HO_SOURCE_CATALOG.keys()),
)

st.header("4. Download Data Collection Template")


def build_rows_from_catalog(selected_items, catalog):
    rows = []
    for item in selected_items:
        category, data_required, unit, guidance, scope = catalog[item]
        rows.append([category, item, item, data_required, unit] + [""] * 12 + [guidance, scope])
    return rows


def unit_sheet_dataframe(unit):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    columns = [
        "Category",
        "Emission Source",
        "Equipment / Activity",
        "Data Required",
        "Unit",
    ] + months + ["Guidance", "Scope"]

    rows = []
    rows.append(["UNIT GUIDANCE", "", "", "", ""] + [""] * 12 + ["Exclude vehicle fuel use in this sheet.", ""])

    rows.extend(build_rows_from_catalog(unit["selected_sources"], UNIT_SOURCE_CATALOG))

    for fuel in unit["general_fuels"]:
        rows.append(
            ["Stationary Combustion", f"General Fuel Use - {fuel}", "General", "Fuel Consumption", "Litres / kg / SCM"]
            + [""] * 12
            + ["Include only non-vehicle stationary/process fuel use", "Scope 1"]
        )

    if not rows:
        rows.append(["No sources selected", "", "", "", ""] + [""] * 12 + ["", ""])

    return pd.DataFrame(rows, columns=columns)


def overall_sheet_dataframe(vehicle_selection, ho_selection):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    columns = [
        "Category",
        "Emission Source",
        "Equipment / Activity",
        "Data Required",
        "Unit",
    ] + months + ["Guidance", "Scope"]

    rows = []
    rows.append(["OVERALL GUIDANCE", "", "", "", ""] + [""] * 12 + ["Capture shared/common sources only.", ""])
    rows.extend(build_rows_from_catalog(vehicle_selection, VEHICLE_SOURCE_CATALOG))
    rows.extend(build_rows_from_catalog(ho_selection, HO_SOURCE_CATALOG))

    if len(rows) == 1:
        rows.append(["No shared sources selected", "", "", "", ""] + [""] * 12 + ["", ""])

    return pd.DataFrame(rows, columns=columns)


def generate_excel(units, vehicle_selection, ho_selection):
    output = BytesIO()

    about_content = (
        "This MSME greenhouse gas data collection workbook has been designed as a practical bridge between operational records "
        "and a complete emissions inventory exercise. The objective of this tool is to support structured data gathering across "
        "multiple units, enable consistency in monthly evidence capture, and improve readiness for consulting-led greenhouse gas "
        "accounting and reporting. The workbook intentionally focuses on activity data and documentation quality, because accurate "
        "emissions estimation depends heavily on complete source identification, correct units, and verifiable source records. "
        "By collecting data in a standardized format, organizations can reduce rework, shorten clarification cycles, and accelerate "
        "the transition from raw logs to auditable inventories and management-ready disclosures."
    )

    guidance_content = (
        "Guidance for use: Start with the company profile and confirm reporting-year boundaries before filling source sheets. "
        "For each unit sheet, include only unit-level stationary combustion, process/fugitive emissions, and purchased electricity. "
        "Do not enter vehicle fuel use within unit sheets; mobile combustion should be captured in the overall module to avoid double counting. "
        "Record values month-wise using invoices, utility bills, refill records, maintenance logs, and production records as supporting evidence. "
        "Keep original units unchanged, avoid blank conversions, and flag exceptional months with comments during consulting review. "
        "Where data is unavailable, retain cells blank and add document requests separately instead of estimating unsupported values."
    )

    pro_tips = (
        "Pro tips and cautions: map metering boundaries before data entry; confirm whether head office electricity is already included in a unit; "
        "track refrigerant type and refill date together; separate process fuel from transport fuel; preserve invoice copies with clear period labels; "
        "and align monthly data cut-off dates with your financial closure cycle."
    )

    company_rows = [
        ["Company Name", company_name],
        ["UDYAM ID", udyam_id],
        ["Industry", industry],
        ["NIC Code", nic_code],
        ["ISIC Code", isic_code],
        ["MSME Classification", msme_class],
        ["Annual Turnover (INR)", turnover],
        ["Reporting Year", reporting_year],
        ["Permanent Employees - Male", perm_m],
        ["Permanent Employees - Female", perm_f],
        ["Contract Employees - Male", cont_m],
        ["Contract Employees - Female", cont_f],
        ["Number of Units", len(units)],
    ]

    about_rows = [
        ["ABOUT THE TOOL", about_content],
        ["GUIDANCE", guidance_content],
        ["KEY SUGGESTIONS", pro_tips],
        ["CONTACT", "Developed by Arun Venkatraman | Total Impact | arun@totalimpact.co.in | +91 6374350144"],
    ] + company_rows
    about_df = pd.DataFrame(about_rows, columns=["Section", "Details"])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        about_df.to_excel(writer, sheet_name="About & Profile", index=False)

        for idx, unit in enumerate(units, start=1):
            unit_df = unit_sheet_dataframe(unit)
            sheet_name = f"Unit {idx} Module"
            unit_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=6)
            ws = writer.sheets[sheet_name]

            ws["A1"] = "UNIT SUMMARY"
            ws["A2"] = "Unit Name"
            ws["B2"] = unit["unit_name"]
            ws["A3"] = "Location"
            ws["B3"] = unit["location"]
            ws["A4"] = "Area (sq ft)"
            ws["B4"] = unit["area_sqft"]
            ws["C2"] = "Ownership"
            ws["D2"] = unit["ownership"]
            ws["C3"] = "Primary Process"
            ws["D3"] = unit["primary_process"]
            ws["C4"] = "Annual Production"
            ws["D4"] = unit["annual_production"]
            ws["A6"] = (
                "Guidance: Capture only unit-level stationary combustion, fugitive emissions, and electricity. "
                "Do not include vehicle fuel use in this sheet."
            )

        overall_df = overall_sheet_dataframe(vehicle_selection, ho_selection)
        overall_df.to_excel(writer, sheet_name="Overall Module", index=False)

        # styles for all sheets
        header_fill = PatternFill("solid", fgColor="305496")
        section_fill = PatternFill("solid", fgColor="D9D9D9")
        yellow_fill = PatternFill("solid", fgColor="FFF2CC")
        light_fill = PatternFill("solid", fgColor="E7E6E6")
        header_font = Font(color="FFFFFF", bold=True)
        bold_font = Font(bold=True)
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        for name, ws in writer.sheets.items():
            max_col = ws.max_column
            max_row = ws.max_row

            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            start_month_col = 6
            end_month_col = 17
            if name in ["About & Profile"]:
                for r in range(2, max_row + 1):
                    ws.cell(r, 1).fill = light_fill
                    ws.cell(r, 1).font = bold_font
            else:
                for r in range(2, max_row + 1):
                    if isinstance(ws.cell(r, 1).value, str) and "GUIDANCE" in ws.cell(r, 1).value.upper():
                        for c in range(1, max_col + 1):
                            ws.cell(r, c).fill = section_fill
                            ws.cell(r, c).font = bold_font
                    for c in range(start_month_col, min(end_month_col, max_col) + 1):
                        ws.cell(r, c).fill = yellow_fill
                        ws.cell(r, c).border = thin_border

            for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
                for cell in row:
                    if cell.alignment is None:
                        cell.alignment = Alignment(vertical="center")

            for col_cells in ws.columns:
                length = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
                ws.column_dimensions[get_column_letter(col_cells[0].column)].width = min(length + 3, 45)

            ws.cell(max_row + 2, 1, "Developed by Arun Venkatraman | Total Impact")
            ws.cell(max_row + 3, 1, "Sustainability & ESG Advisory | GHG Accounting | Supply Chain Decarbonisation")
            ws.cell(max_row + 4, 1, "arun@totalimpact.co.in | +91 6374350144")

    output.seek(0)
    return output


if st.button("Generate Excel Template"):
    excel_file = generate_excel(units_data, vehicle_sources, ho_sources)
    st.download_button(
        label="Download Excel Template",
        data=excel_file,
        file_name="MSME_GHG_Data_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.markdown("---")
st.markdown(
    """
    **Developed by Arun Venkatraman | Total Impact**  
    Sustainability & ESG Advisory | GHG Accounting | Supply Chain Decarbonisation  
    📧 arun@totalimpact.co.in | 📞 +91 6374350144
    """
)
