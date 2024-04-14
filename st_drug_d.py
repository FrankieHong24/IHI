import streamlit as st
import pandas as pd
import plotly.express as px
from drugs_d_data_retrieval import fetch_data, process_data

def create_searchable_table(df):
    search_query = st.text_input("Search for a drug by brand name or generic name:")
    if search_query:
        df_filtered = df[
            df['Brand Name'].str.contains(search_query, case=False) |
            df['Generic Name'].str.contains(search_query, case=False)
        ]
    else:
        df_filtered = df
    
    columns_to_display = [
        'Brand Name', 'Generic Name', 'Total Spending 2022', 'Total Beneficiaries 2022', 
        'Average Spending Per Beneficiary 2022','Average Spending Per Dosage Unit Weighted 2022', 
        'Average Spending Per Claim 2022', 
        'Change Average Spending Per Dosage Unit 2021-2022',
        'CAGR Average Spending Per Dosage Unit 2018-2022'
    ]
    
    st.dataframe(df_filtered[columns_to_display])

def plot_spending_trends(df, drug_choice):
    drug_data = df[(df['Brand Name'] == drug_choice) | (df['Generic Name'] == drug_choice)]
    spending_data = pd.DataFrame({
        'Year': [col.split()[-1] for col in df.columns if 'Average Spending Per Dosage Unit Weighted' in col],
        'Average Spending Per Beneficiary': drug_data[[col for col in df.columns if 'Average Spending Per Beneficiary' in col]].iloc[0].values
    })
    spending_data['Year'] = spending_data['Year'].astype(int)

    # Create line chart using Plotly
    fig = px.line(spending_data, x='Year',
                  y=['Average Spending Per Beneficiary'],
                  title=f"Spending Trends for {drug_choice}",
                  labels={'value': 'Average Spending ($)', 'Year': 'Year'},
                  markers=True)
    st.plotly_chart(fig)

def main():
    st.title("Medicare Part D Drug Spending Dashboard")
    st.markdown("""
        The Medicare Part D Drug Spending Dashboard allows you to explore drug spending trends for different medications.

        Part D drugs are drugs patients administer themselves and are paid through the Medicare Part D subscription program.
    """)
    raw_df = fetch_data()
    processed_df = process_data(raw_df)
    create_searchable_table(processed_df)

    drug_choices = pd.concat([processed_df['Brand Name'], processed_df['Generic Name']]).unique()
    drug_choices = st.selectbox("Select a drug to view spending trends:", drug_choices)

    if drug_choices:
        plot_spending_trends(processed_df, drug_choices)

if __name__ == "__main__":
    main()  

