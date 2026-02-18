import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MSME GHG Tool", layout="wide")

st.title("MSME GHG Data Collection Tool")
st.write("This tool helps MSMEs collect required data for Scope 1 and Scope 2 GHG emissions.")

# ---------------------------
# COMPANY PROFILE
# ---------------------------

st.header("1. Company Profile")

col1, col2 = st.columns(2)

with col1:
    company_name = st.text_input("Company Name")
    udyam_id = st.text_input("UDYAM ID")
    industry = st.text_input("Industry")
    nic_code = st.text_input("NIC Code (India)")

with col2:
    isic_code = st.text_input("International Industry Code (ISIC)")
    msme_class = st.selectbox(
        "MSME Classification",
        ["Micro", "Small", "Medium"]
    )
    turnover = st.number_input(
        "Annual Turnover (INR)",
        min_value=0,
        key="turnover"
    )

# ✅ ADD THIS BLOCK HERE
reporting_year = st.selectbox(
    "Reporting Year",
    ["2023-24", "2024-25", "2025-26"]
)

st.subheader("Employees")

col3, col4 = st.columns(2)

with col3:
    perm_m = st.number_input("Permanent Employees - Male", min_value=0, key="perm_m")
    perm_f = st.number_input("Permanent Employees - Female", min_value=0, key="perm_f")

with col4:
    cont_m = st.number_input("Contract Employees - Male", min_value=0, key="cont_m")
    cont_f = st.number_input("Contract Employees - Female", min_value=0, key="cont_f")

# ---------------------------
# MACHINERY SELECTION
# ---------------------------

st.header("2. Select Machinery / Emission Sources")

machinery = st.multiselect(
    "Select applicable equipment",
    [
        "DG Set",
        "Boiler",
        "Furnace",
        "Owned Vehicles",
        "Industrial HVAC",
        "Air Conditioners",
        "Fire Extinguishers",
        "Electricity Consumption"
    ]
)

# ---------------------------
# DYNAMIC DATA INPUT
# ---------------------------

st.header("3. Required Data Inputs")

scope1_data = []
scope2_data = []

if "DG Set" in machinery:
    st.subheader("DG Set (Scope 1)")
    dg_fuel = st.selectbox("Fuel Type (DG Set)", ["Diesel"])
    dg_qty = st.number_input("Diesel Consumption (litres/month)", min_value=0)
    scope1_data.append(["DG Set", "Diesel Consumption", "Litres/month"])

if "Boiler" in machinery:
    st.subheader("Boiler (Scope 1)")
    boiler_fuel = st.text_input("Boiler Fuel Type")
    boiler_qty = st.number_input("Fuel Consumption per month", min_value=0)
    scope1_data.append(["Boiler", "Fuel Consumption", "Units/month"])

if "Furnace" in machinery:
    st.subheader("Furnace (Scope 1)")
    furnace_fuel = st.text_input("Furnace Fuel Type")
    furnace_qty = st.number_input("Fuel Consumption (monthly)", min_value=0)
    scope1_data.append(["Furnace", "Fuel Consumption", "Units/month"])

if "Owned Vehicles" in machinery:
    st.subheader("Owned Vehicles (Scope 1)")
    vehicle_fuel = st.number_input("Fuel Consumption (litres/month)", min_value=0)
    scope1_data.append(["Owned Vehicles", "Fuel Consumption", "Litres/month"])

if "Industrial HVAC" in machinery:
    st.subheader("Industrial HVAC (Scope 1)")
    hvac_ref = st.text_input("Refrigerant Type")
    hvac_qty = st.number_input("Refrigerant Refill Quantity (kg/year)", min_value=0)
    scope1_data.append(["Industrial HVAC", "Refrigerant Refill", "kg/year"])

if "Air Conditioners" in machinery:
    st.subheader("Air Conditioners (Scope 1)")
    ac_qty = st.number_input("Refrigerant Refill Quantity (kg/year)", min_value=0,key="ac_ref")
    scope1_data.append(["Air Conditioners", "Refrigerant Refill", "kg/year"])

if "Fire Extinguishers" in machinery:
    st.subheader("Fire Extinguishers (Scope 1)")
    fe_qty = st.number_input("Refill Quantity (kg/year)", min_value=0)
    scope1_data.append(["Fire Extinguishers", "Refill Quantity", "kg/year"])

if "Electricity Consumption" in machinery:
    st.subheader("Electricity (Scope 2)")
    electricity = st.number_input("Electricity Consumption (kWh/month)", min_value=0)

# ---------------------------
# EXCEL GENERATION
# ---------------------------
# ---------------------------
# EXCEL GENERATION
# ---------------------------

from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

st.header("4. Download Data Collection Template")


def generate_excel(scope1, scope2, reporting_year):

    output = BytesIO()

    # ---------------------------
    # COMPANY PROFILE SHEET
    # ---------------------------
    intro_data = [

    ["COMPANY INFORMATION", ""],
    ["Company Name", company_name],
    ["UDYAM ID", udyam_id],
    ["Industry", industry],
    ["Reporting Year", reporting_year],
    ["", ""],

    ["ABOUT THIS TEMPLATE", ""],
    ["This template is designed to help MSMEs collect data required for Scope 1 and Scope 2 GHG emissions accounting.", ""],
    ["The collected data can be used for ESG reporting, carbon footprint assessment and decarbonisation planning.", ""],
    ["", ""],

    ["HOW TO USE THIS TEMPLATE", ""],
    ["1. Complete the company profile section above.", ""],
    ["2. Identify applicable equipment and emission sources.", ""],
    ["3. Enter data month-wise in the Emissions Data sheet.", ""],
    ["4. Use electricity bills, fuel purchase bills and maintenance logs.", ""],
    ["5. Do not change units or structure of the template.", ""],
    ["6. Leave cells blank if data is not applicable.", ""],
    ["", ""],

    ["REFERENCE LINKS", ""],
    ["NIC Industry Classification Guidance", "https://www.ncs.gov.in/Documents/NIC_Sector.pdf"],
    ["ISIC International Industry Classification", "https://unstats.un.org/unsd/publication/seriesm/seriesm_4rev4e.pdf"]
    ]

    intro_df = pd.DataFrame(intro_data, columns=["Field", "Value"])

    # ---------------------------
    # EMISSIONS DATA STRUCTURE
    # ---------------------------

    months = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]

    columns = [
        "Category",
        "Emission Source",
        "Equipment / Activity",
        "Data Required",
        "Unit"
    ] + months + ["Guidance", "Scope"]

    data_rows = []

    # ---- SECTION: STATIONARY COMBUSTION ----
    data_rows.append(["STATIONARY COMBUSTION","","","",""] + [""]*12 + ["",""])

    stationary_rows = [
        ["Stationary Combustion","Other Diesel Use","General","Diesel Consumption","Litres"],
        ["Stationary Combustion","LPG Use","General","LPG Consumption","kg"]
    ]

    for r in stationary_rows:
        data_rows.append(r + [""]*12 + ["Fuel purchase bills","Scope 1"])

    # ---- SECTION: MOBILE COMBUSTION ----
    data_rows.append(["MOBILE COMBUSTION","","","",""] + [""]*12 + ["",""])

    mobile_rows = [
        ["Mobile Combustion","Petrol Vehicles","General","Petrol Consumption","Litres"]
    ]

    for r in mobile_rows:
        data_rows.append(r + [""]*12 + ["Fuel logs or bills","Scope 1"])

    # ---- ADD MACHINERY SELECTION ROWS ----
    for row in scope1:
        data_rows.append(
            ["Combustion / Refrigerant",
             row[0],
             row[0],
             row[1],
             row[2]] +
            [""]*12 +
            ["Refer bills or maintenance logs","Scope 1"]
        )

    # ---- SECTION: ELECTRICITY ----
    data_rows.append(["PURCHASED ELECTRICITY","","","",""] + [""]*12 + ["",""])

    data_rows.append(
        ["Purchased Energy",
         "Electricity",
         "Electricity",
         "Electricity Consumption",
         "kWh"] +
        [""]*12 +
        ["Electricity bills","Scope 2"]
    )

    emissions_df = pd.DataFrame(data_rows, columns=columns)

    # ---------------------------
    # WRITE EXCEL
    # ---------------------------
    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        intro_df.to_excel(writer, sheet_name="Company Profile", index=False)
        emissions_df.to_excel(writer, sheet_name="Emissions Data", index=False)

        ws_profile = writer.sheets["Company Profile"]
        ws_emissions = writer.sheets["Emissions Data"]

        # ---------- COLORS ----------
        header_fill = PatternFill("solid", fgColor="305496")
        section_fill = PatternFill("solid", fgColor="D9D9D9")
        yellow_fill = PatternFill("solid", fgColor="FFF2CC")
        grey_fill = PatternFill("solid", fgColor="E7E6E6")

        header_font = Font(color="FFFFFF", bold=True)
        bold_font = Font(bold=True)

        center_align = Alignment(horizontal="center", vertical="center")
        wrap_align = Alignment(wrap_text=True)

        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # ---------- COMPANY PROFILE FORMAT ----------
        for cell in ws_profile[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        for r in range(2, ws_profile.max_row+1):
            ws_profile.cell(row=r, column=1).fill = grey_fill
            ws_profile.row_dimensions[r].height = 22

        for col_cells in ws_profile.columns:
            length = max(len(str(c.value)) if c.value else 0 for c in col_cells)
            ws_profile.column_dimensions[
                get_column_letter(col_cells[0].column)
            ].width = length + 4

        # ---------- EMISSIONS FORMAT ----------
        ws_emissions.freeze_panes = "A2"

        for cell in ws_emissions[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        # section headers
        for r in range(2, ws_emissions.max_row+1):
            if ws_emissions.cell(r,1).value.isupper():
                for c in range(1, ws_emissions.max_column+1):
                    ws_emissions.cell(r,c).fill = section_fill
                    ws_emissions.cell(r,c).font = bold_font

        # yellow monthly input cells
        for col in range(6,18):
            for row in range(2, ws_emissions.max_row+1):
                ws_emissions.cell(row=row,column=col).fill = yellow_fill
                ws_emissions.cell(row=row,column=col).border = thin_border

        # wrap guidance column
        guidance_col = ws_emissions.max_column - 1
        for r in range(2, ws_emissions.max_row+1):
            ws_emissions.cell(r,guidance_col).alignment = wrap_align

        # row height
        for r in range(1, ws_emissions.max_row+1):
            ws_emissions.row_dimensions[r].height = 20

        # auto column width
        for col_cells in ws_emissions.columns:
            length = max(len(str(c.value)) if c.value else 0 for c in col_cells)
            ws_emissions.column_dimensions[
                get_column_letter(col_cells[0].column)
            ].width = min(length+3,35)
        # ---------- OUTLINE BORDER FOR TABLES ----------

        outline_border = Border(
            left=Side(style='medium'),
            right=Side(style='medium'),
            top=Side(style='medium'),
            bottom=Side(style='medium')
        )

        # Company Profile outer border
        for col in range(1, ws_profile.max_column + 1):
            ws_profile.cell(1, col).border = outline_border
            ws_profile.cell(ws_profile.max_row, col).border = outline_border

        for row in range(1, ws_profile.max_row + 1):
            ws_profile.cell(row, 1).border = outline_border
            ws_profile.cell(row, ws_profile.max_column).border = outline_border

        # Emissions table outer border
        for col in range(1, ws_emissions.max_column + 1):
            ws_emissions.cell(1, col).border = outline_border
            ws_emissions.cell(ws_emissions.max_row, col).border = outline_border

        for row in range(1, ws_emissions.max_row + 1):
            ws_emissions.cell(row, 1).border = outline_border
            ws_emissions.cell(row, ws_emissions.max_column).border = outline_border


    output.seek(0)
    return output


if st.button("Generate Excel Template"):
    excel_file = generate_excel(scope1_data, scope2_data, reporting_year)

    st.download_button(
        label="Download Excel Template",
        data=excel_file,
        file_name="MSME_GHG_Data_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
