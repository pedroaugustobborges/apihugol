import requests
import json
import pandas as pd
import streamlit as st
import altair as alt


# Streamlit app
st.title("Dashboard para o API")

# API endpoint URL for retrieving JSON data
api_url = "https://agir.api.neovero.com/api/queries/execute/consulta_os?data_abertura_inicio=2022-12-01T00:00&empresa_id=4&situacao_int=1,2,3"

# API key for authentication
api_key = "2050ee77-2cc7-47e0-8b82-4c8dda75ef5f"

# Set up the headers with the API key
headers = {
    "X-API-KEY": api_key,
}

# Make the request to the API
response = requests.get(api_url, headers=headers)

try:
    # Try to parse the JSON response
    data = response.json()
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    exit()

# Check the status code of the response
if response.status_code != 200:
    print(f"Request failed with status code {response.status_code}")
    exit()

# Extract 'empresa' values from each entry
empresas = [entry.get("empresa") for entry in data]
# Extract 'data_atendimento' values from each entry
data_atendimento = [entry.get("data_atendimento") for entry in data]
# Extract 'fornecedor' values from each entry
fornecedor = [entry.get("fornecedor") for entry in data]
# Extract 'responsavel' values from each entry
responsavel = [entry.get("responsavel") for entry in data]

#-------------------------- INVENÇÃO --------------

# Create a DataFrame using pandas
df = pd.DataFrame({"Empresa": empresas, "Data Atendimento": data_atendimento, "Fornecedor": fornecedor, "Responsavel": responsavel})


# Convert "Data Atendimento" column to datetime with errors='coerce'
df["Data Atendimento"] = pd.to_datetime(df["Data Atendimento"], format='%Y-%m-%dT%H:%M:%S', errors='coerce')

# Filter out rows where the date could not be parsed (NaT)
df = df.dropna(subset=["Data Atendimento"])

# Extract year, month, and quarter
df["Year"] = df["Data Atendimento"].dt.year
df["Month"] = df["Data Atendimento"].dt.month
df["Quarter"] = df["Data Atendimento"].dt.quarter

# Create a "Year-Quarter" column
df["Year-Quarter"] = df["Year"].astype(str) + "-T" + df["Quarter"].astype(str)

# If you want to create a "Year-Month" column, you can use the following line
df["Year-Month"] = df["Data Atendimento"].dt.strftime("%Y-%m")





# Sort the unique values in ascending order
unique_year_month = sorted(df["Year-Month"].unique())
unique_year_quarter = sorted(df["Year-Quarter"].unique())


# Add "All" as an option for both filters
unique_year_month.insert(0, "Todos")
unique_year_quarter.insert(0, "Todos")


# Create a sidebar for selecting filters
month = st.sidebar.selectbox("Mês", unique_year_month)
quarter = st.sidebar.selectbox("Trimestre", unique_year_quarter)



# Check if "All" is selected for the "Year-Month" filter
if month == "Todos":
    month_filtered = df
else:
    month_filtered = df[df["Year-Month"] == month]

# Check if "All" is selected for the "Year-Quarter" filter
if quarter == "Todos":
    filtered_df = month_filtered
else:
    filtered_df = month_filtered[month_filtered["Year-Quarter"] == quarter]

# Display the filtered DataFrame
st.write("Dados Selecionados:")
st.dataframe(filtered_df)

col1, col2 = st.columns(2)


#--------------------- FIM DA INVENÇÃO ------------------------------

# Count occurrences and sort by count in descending order
responsavel_counts = filtered_df['Responsavel'].value_counts().reset_index().rename(columns={'index': 'Responsavel', 'Responsavel': 'count1'})
fornecedor_counts = filtered_df['Fornecedor'].value_counts().reset_index().rename(columns={'index': 'Fornecedor', 'Fornecedor': 'count2'})



# Bar chart for 'responsavel'
st.subheader("Quantidade por Responsável")
responsavel_chart = alt.Chart(responsavel_counts).mark_bar().encode(
    x=alt.X('Responsavel:N', sort=alt.EncodingSortField(field='count', op='sum', order='descending')),
    y='count1:Q'
)
st.altair_chart(responsavel_chart, use_container_width=True)

# Bar chart for 'fornecedor'
st.subheader("Quantidade Fornecedor")
fornecedor_chart = alt.Chart(fornecedor_counts).mark_bar().encode(
    x=alt.X('Fornecedor:N', sort=alt.EncodingSortField(field='count', op='sum', order='descending')),
    y='count2:Q'
)
st.altair_chart(fornecedor_chart, use_container_width=True)




