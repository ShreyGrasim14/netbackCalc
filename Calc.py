import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(layout="centered", page_title="Freight Rate Calculator")

# Custom CSS for professional styling
st.markdown("""
<style>
/* Main container styling */
.stApp {
    background-color: #0a0808;
}

/* Header styling */
h1 {
    color: #2c3e50;
    font-weight: 700;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #3498db;
}

h2 {
    color: #2c3e50;
    font-weight: 600;
    margin-top: 1.5rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid #e0e0e0;
}

/* Button styling */
.stButton>button {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stButton>button:hover {
    background-color: #2980b9;
    transform: translateY(-1px);
    box-shadow: 0 2px 5px rgba(0,0,0,0.15);
}

/* Input field styling */
.stTextInput>div>div>input, 
.stNumberInput>div>div>input {
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 10px;
    font-size: 16px;
    transition: border-color 0.2s ease;
}

.stTextInput>div>div>input:focus, 
.stNumberInput>div>div>input:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52,152,219,0.2);
    outline: none;
}

/* Select box styling */
.stSelectbox>div>div>div {
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 5px;
    font-size: 16px;
    transition: all 0.2s ease;
}

.stSelectbox>div>div>div:hover {
    border-color: #3498db;
}

.stSelectbox>div>div>div:focus-within {
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52,152,219,0.2);
}

/* Status message styling */
.stAlert {
    padding: 1rem 1.5rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.stAlert.stAlert-success {
    background-color: #e8f5e9;
    color: #2e7d32;
    border-left: 4px solid #4caf50;
}

.stAlert.stAlert-warning {
    background-color: #fff8e1;
    color: #ff8f00;
    border-left: 4px solid #ffb300;
}

.stAlert.stAlert-error {
    background-color: #ffebee;
    color: #c62828;
    border-left: 4px solid #f44336;
}
</style>
""", unsafe_allow_html=True)

# Load the CSV file
try:
    df = pd.read_csv("Sample File - Export(Sample File).csv")

    required_freight_column = 'Rate 1st Half of Month'

    if required_freight_column not in df.columns:
        raise ValueError(
            f"Required freight rate column '{required_freight_column}' not found in the CSV file. "
            f"Please ensure the column name is exact (case-sensitive) and check for any leading/trailing spaces. "
            f"Available columns are: {', '.join(df.columns)}"
        )

    df[required_freight_column] = pd.to_numeric(
        df[required_freight_column], errors='coerce'
    )

except FileNotFoundError:
    st.error("Error: 'Sample File - Export(Sample File).csv' not found. Please ensure the file is in the correct directory.")
    st.stop()
except ValueError as ve:
    st.error(f"Data Processing Error: {ve}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while reading or processing the CSV file: {e}")
    st.stop()

# Title and description
st.title("Freight Rate Netback Calculator")
st.write("Select the specifications below to find the freight rate and calculate netback.")

st.header("Select Specifications")

required_unit_column = 'Unit'
required_destination_port_column = 'Destination Port'
required_country_column = 'Country'

try:
    if required_unit_column not in df.columns:
        raise ValueError(f"Required dropdown column '{required_unit_column}' not found. Available columns: {', '.join(df.columns)}")
    units = df[required_unit_column].unique().tolist()

    if required_destination_port_column not in df.columns:
        raise ValueError(f"Required dropdown column '{required_destination_port_column}' not found. Available columns: {', '.join(df.columns)}")

    if required_country_column not in df.columns:
        raise ValueError(f"Required dropdown column '{required_country_column}' not found. Available columns: {', '.join(df.columns)}")
    countries = df[required_country_column].unique().tolist()

except ValueError as ve:
    st.error(f"Data Processing Error for Dropdowns: {ve}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while preparing dropdown data: {e}")
    st.stop()

# Reordered dropdowns: Country first, then Destination Port, then Unit
selected_country = st.selectbox(f"Select {required_country_column}", (countries))

# Filter destination ports based on selected country
filtered_ports_df = df[df[required_country_column] == selected_country]
destination_ports_for_country = sorted(filtered_ports_df[required_destination_port_column].unique().tolist())

selected_destination_port = st.selectbox(f"Select {required_destination_port_column}", destination_ports_for_country)

selected_unit = st.selectbox(f"Select {required_unit_column}", sorted(units))

st.header("Freight Rate Information")

# Filter DataFrame based on all three selections
filtered_df = df[
    (df[required_unit_column] == selected_unit) &
    (df[required_destination_port_column] == selected_destination_port) &
    (df[required_country_column] == selected_country)
]

freight_rate = None
if not filtered_df.empty:
    potential_freight_rate = filtered_df[required_freight_column].iloc[0]

    if not pd.isna(potential_freight_rate):
        freight_rate = potential_freight_rate
        st.success(f"**Freight Rate ({required_freight_column}):** ${freight_rate:,.2f}")
    else:
        st.warning(f"No valid freight rate found (or rate is empty/non-numeric) for the selected combination. Please adjust your selections or check your data in column '{required_freight_column}'.")
else:
    st.warning("No freight rate data found for the selected combination. Please adjust your selections.")

st.header("Netback Calculation")

if freight_rate is not None:
    cif = st.number_input("Enter CIF (Cost, Insurance, Freight) in Dollars ($)", min_value=0.0, format="%.2f")

    local_rate_default = 0.02
    local_rate = st.number_input(f"Enter Local Rate (default: {local_rate_default})", min_value=0.0, value=local_rate_default, format="%.4f")

    divisor = 23000.0

    if cif > 0:
        netback = cif - (freight_rate / divisor) - local_rate
        st.success(f"**Calculated Netback:** ${netback:,.2f}")
    else:
        st.info("Enter a CIF value greater than 0 to calculate netback.")
else:
    st.info("Select a valid combination of Unit, Destination Port, and Country with an existing and valid freight rate to proceed with Netback calculation.")
