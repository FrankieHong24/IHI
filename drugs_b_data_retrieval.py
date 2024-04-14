import requests
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def fetch_data():
    # Define the base URL and dataset type identifier
    base_url = "https://data.cms.gov/data-api/v1/dataset"
    dataset_type_identifier = "76a714ad-3a2c-43ac-b76d-9dadf8f7d890"

    # Initialize variables for pagination
    data = []
    size = 5000  # The maximum allowed by the CMS API
    offset = 0

    while True:
        # Construct the URL with pagination parameters
        paginated_url = f"{base_url}/{dataset_type_identifier}/data?size={size}&offset={offset}"

        # Make the GET request
        response = requests.get(paginated_url)

        # Check if the request was successful
        if response.status_code == 200:
            page_data = response.json()
            # Break the loop if no data is returned
            if not page_data:
                break
            # Append the data from the current page to the overall data list
            data.extend(page_data)
            # Update the offset to get the next page of data in the subsequent iteration
            offset += size
        else:
            print("Failed to retrieve data:", response.status_code, response.text)
            break

    return pd.DataFrame(data)

def process_data(raw_df):
    rename_columns = {
        'HCPCS_Cd': 'Medicare Billing Code (HCPCS Code)',
        'HCPCS_Desc': 'Drug Description',
        'Brnd_Name': 'Brand Name',
        'Gnrc_Name': 'Generic Name',
        'Tot_Spndng_2018': 'Total Spending 2018',
        'Tot_Dsg_Unts_2018': 'Total Dosage Units 2018',
        'Tot_Clms_2018': 'Total Claims 2018',
        'Tot_Benes_2018': 'Total Beneficiaries 2018',
        'Avg_Spndng_Per_Dsg_Unt_2018': 'Average Spending Per Dosage Unit 2018',
        'Avg_Spndng_Per_Clm_2018': 'Average Spending Per Claim 2018',
        'Avg_Spndng_Per_Bene_2018': 'Average Spending Per Beneficiary 2018',
        'Outlier_Flag_2018': 'Outlier Flag 2018',
        'Tot_Spndng_2019': 'Total Spending 2019',
        'Tot_Dsg_Unts_2019': 'Total Dosage Units 2019',
        'Tot_Clms_2019': 'Total Claims 2019',
        'Tot_Benes_2019': 'Total Beneficiaries 2019',
        'Avg_Spndng_Per_Dsg_Unt_2019': 'Average Spending Per Dosage Unit 2019',
        'Avg_Spndng_Per_Clm_2019': 'Average Spending Per Claim 2019',
        'Avg_Spndng_Per_Bene_2019': 'Average Spending Per Beneficiary 2019',
        'Outlier_Flag_2019': 'Outlier Flag 2019',
        'Tot_Spndng_2020': 'Total Spending 2020',
        'Tot_Dsg_Unts_2020': 'Total Dosage Units 2020',
        'Tot_Clms_2020': 'Total Claims 2020',
        'Tot_Benes_2020': 'Total Beneficiaries 2020',
        'Avg_Spndng_Per_Dsg_Unt_2020': 'Average Spending Per Dosage Unit 2020',
        'Avg_Spndng_Per_Clm_2020': 'Average Spending Per Claim 2020',
        'Avg_Spndng_Per_Bene_2020': 'Average Spending Per Beneficiary 2020',
        'Outlier_Flag_2020': 'Outlier Flag 2020',
        'Tot_Spndng_2021': 'Total Spending 2021',
        'Tot_Dsg_Unts_2021': 'Total Dosage Units 2021',
        'Tot_Clms_2021': 'Total Claims 2021',
        'Tot_Benes_2021': 'Total Beneficiaries 2021',
        'Avg_Spndng_Per_Dsg_Unt_2021': 'Average Spending Per Dosage Unit 2021',
        'Avg_Spndng_Per_Clm_2021': 'Average Spending Per Claim 2021',
        'Avg_Spndng_Per_Bene_2021': 'Average Spending Per Beneficiary 2021',
        'Outlier_Flag_2021': 'Outlier Flag 2021',
        'Tot_Spndng_2022': 'Total Spending 2022',
        'Tot_Dsg_Unts_2022': 'Total Dosage Units 2022',
        'Tot_Clms_2022': 'Total Claims 2022',
        'Tot_Benes_2022': 'Total Beneficiaries 2022',
        'Avg_Spndng_Per_Dsg_Unt_2022': 'Average Spending Per Dosage Unit 2022',
        'Avg_Spndng_Per_Clm_2022': 'Average Spending Per Claim 2022',
        'Avg_Spndng_Per_Bene_2022': 'Average Spending Per Beneficiary 2022',
        'Outlier_Flag_2022': 'Outlier Flag 2022',
        'Avg_DY22_ASP_Price': 'Average Sales Price',
        'Chg_Avg_Spndng_Per_Dsg_Unt_21_22': 'Change in Average Spending Per Dosage Unit (2021-2022)',
        'CAGR_Avg_Spnd_Per_Dsg_Unt_18_22': 'Annual Growth Rate in Average Spending Per Dosage Unit (2018-2022)',
    }

    df_processed = raw_df.rename(columns=rename_columns)
    string_columns = ['Drug Description', 'Brand Name', 'Generic Name']
    for col in string_columns:
        df_processed[col] = df_processed[col].astype(str).str.strip()
    float_columns = df_processed.columns.difference(string_columns)
    for col in float_columns:
        df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
    
    df_processed[float_columns] = df_processed[float_columns].fillna(0).apply(lambda x: x.round(2))
    return df_processed

