import streamlit as st
import pandas as pd
import plotly.express as px

st.set_option('deprecation.showPyplotGlobalUse', False)
# Ensure Streamlit uses the entire page width and sets padding to 0 on left and right
st.set_page_config(layout="wide", page_title="Air Quality Dashboard")

# Load the dataset
@st.cache_data  # This decorator caches the data to prevent reloading on every interaction
def load_data():
    df = pd.read_csv("data/data.csv", encoding="ISO-8859-1")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Ensure 'date' is in datetime format
    df.dropna(subset=['date'], inplace=True)  # Drop rows where datetime conversion failed
    # Extract year and month for easier filtering
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df.drop(['agency', 'rspm', 'spm', 'location_monitoring_station', "pm2_5"], axis=1, inplace=True)
    return df

def aggregate_small_slices(df, column_name, threshold=0.05):
    # Calculate the frequency of each category
    frequencies = df[column_name].value_counts(normalize=True)
    # Identify categories that are below the threshold
    small_slices = frequencies[frequencies < threshold].index
    # Replace small slice values with 'Other'
    df_replaced = df.copy()
    df_replaced[column_name] = df_replaced[column_name].replace(small_slices, 'Other')
    return df_replaced

df = load_data()

# Dashboard title
st.title('India Air Quality Data Dashboard')



# Layout adjustments - Create two columns
col1, col2 = st.columns(2)
col1_1, col1_2, col1_3 = st.columns(3)

# Selections for state, location, and type
state = col1.selectbox('Select a State', df['state'].unique())
location = col2.selectbox('Select a Location', df[df['state'] == state]['location'].unique())
type_selection = col1_1.selectbox('Select Type (Optional)', list(df['type'].unique()))

# Year and month selection
years = list(df['year'].unique())
years.sort()
years = ['all']+years
year = col1_2.selectbox('Select Year', years, index=0)
months = list(df['month'].unique())
months.sort()
months = ['all'] + months
month = col1_3.selectbox('Select Month', months, index=0)

# Filtering data based on selections
filtered_data = df[(df['state'] == state) & (df['location'] == location)]
if year != 'all':
    filtered_data = filtered_data[(df['year'] == year)]
if month != 'all':
    filtered_data = filtered_data[(df['month'] == month)]

filtered_data = filtered_data[filtered_data['type'] == type_selection]
filtered_data = filtered_data.sort_values(by='date')


df_state_aggregated = aggregate_small_slices(df, 'state', 0.03)
df_type_aggregated = aggregate_small_slices(df, 'type')

# Create pie charts
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text(f"state: {state} \nlocation: {location} \ntype: {type_selection}")
        st.write(filtered_data.drop(['state', 'location','type', 'year', 'month'], axis=1))
    with col2:
        fig_state = px.pie(df_state_aggregated, names='state', title='State Distribution')
        st.plotly_chart(fig_state, use_container_width=True)
    with col3:
        fig_type = px.pie(df_type_aggregated, names='type', title='Type Distribution')
        st.plotly_chart(fig_type, use_container_width=True)



# Create line graph based on selections
if not filtered_data.empty:
    fig_line = px.line(filtered_data, x='date', y=['so2', 'no2'], title=f'SO2 and NO2 Levels Over Time in {month}/{year}')
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.write("No data available for the selected filters.")


