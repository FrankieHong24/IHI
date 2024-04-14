import streamlit as st
import pandas as pd
import plotly.express as px
from drugs_b_data_retrieval import fetch_data, process_data

def create_searchable_dropdown(df):
    search_options = pd.concat([df['Brand Name'], df['Generic Name']]).unique()
    search_options.sort()

    selected_option = st.selectbox("Search for a drug by name:", 
                                   options=search_options,
                                   format_func=lambda x: x if pd.notna(x) else "Not Available")
    
    columns_2022 = [
        'Brand Name', 'Generic Name', 'Total Spending 2022', 'Total Dosage Units 2022', 
        'Total Claims 2022', 'Total Beneficiaries 2022', 'Average Spending Per Dosage Unit 2022',
        'Average Spending Per Claim 2022', 'Average Spending Per Beneficiary 2022', 
        'Average Sales Price'
    ]

    if selected_option and selected_option != "Not Available":
        filtered_df = df[(df['Brand Name'] == selected_option) | (df['Generic Name'] == selected_option)]
        st.dataframe(filtered_df[columns_2022])
    else:
        st.dataframe(df[columns_2022])

def plot_spending_trends(df, selected_drug):
    spending_data = {
        'Year': ['2018', '2019', '2020', '2021', '2022'],
        'Average Spending Per Beneficiary': [
            df.at[selected_drug, 'Average Spending Per Beneficiary 2018'],
            df.at[selected_drug, 'Average Spending Per Beneficiary 2019'],
            df.at[selected_drug, 'Average Spending Per Beneficiary 2020'],
            df.at[selected_drug, 'Average Spending Per Beneficiary 2021'],
            df.at[selected_drug, 'Average Spending Per Beneficiary 2022'],
        ]
    }

    # Convert the data to a DataFrame
    spending_df = pd.DataFrame(spending_data)

    fig = px.line(spending_df, x='Year', y='Average Spending Per Beneficiary',
                  title=f"Spending Trends",
                  markers=True,
                  labels={'Average Spending Per Beneficiary': 'Average Spending ($)', 'Year': 'Year'})
    st.plotly_chart(fig)

def main():
    st.title("Medicare Part B Drug Spending Dashboard")
    st.markdown("""
                The Medicare Part B Drug Spending Dashboard allows you to explore drug spending trends for different medications.

                Part B drugs are administered by a healthcare provider and are typically covered under Medicare Part B. 
                This dataset provides information on the spending, dosage units, claims, and beneficiaries for various drugs in 2022.                
                """)
    raw_df = fetch_data()
    processed_df = process_data(raw_df)
    create_searchable_dropdown(processed_df)
        
    search_options = pd.concat([processed_df['Brand Name'], processed_df['Generic Name']]).unique()
    selected_option = st.selectbox("Select a drug to view spending trends:", options=search_options,
                                   format_func=lambda x: x if pd.notna(x) else "Not Available")
    if selected_option and selected_option != "Not Available":
        selected_index = processed_df[(processed_df['Brand Name'] == selected_option) | (processed_df['Generic Name'] == selected_option)].index
    if not selected_index.empty:
        plot_spending_trends(processed_df, selected_index[0])

if __name__ == "__main__":
    main() 

                                   
