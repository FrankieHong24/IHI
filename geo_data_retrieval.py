import requests
import streamlit as st
import pandas as pd
import numpy as np

def fetch_data():

    # Define the base URL and dataset type identifier
    base_url = "https://data.cms.gov/data-api/v1/dataset"
    dataset_type_identifier = "6219697b-8f6c-4164-bed4-cd9317c58ebc"

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
    raw_df['YEAR'] = pd.to_numeric(raw_df['YEAR'], errors='coerce')
    df = raw_df[(raw_df['YEAR'] >= 2017) & (raw_df['YEAR'] <= 2021)].reset_index(drop=True)
    df = df[df['BENE_AGE_LVL'] == 'All'].reset_index(drop=True)
    df['BENE_GEO_CD'] = df['BENE_GEO_CD'].astype(str)
    non_numeric_columns = ['BENE_GEO_LVL', 'BENE_GEO_DESC', 'BENE_GEO_CD', 'BENE_AGE_LVL']

    for col in df.columns:
        if col not in non_numeric_columns:
            # replace "*" with 0.0001 so it's negligible
            df[col] = df[col].replace('*',0.0001)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    standardized_costs_dict = {
        'total_costs': 'TOT_MDCR_STDZD_PYMT_PC',
        'inpatient': 'IP_MDCR_STDZD_PYMT_PC',
        'outpatient': 'OP_MDCR_STDZD_PYMT_PC',
        'ambulatory_surgery': 'ASC_MDCR_STDZD_PYMT_PC',
        'skilled_nursing_facility': 'SNF_MDCR_STDZD_PYMT_PC',
        'inpatient_rehab': 'IRF_MDCR_STDZD_PYMT_PC',
        'long_term_care_hospital': 'LTCH_MDCR_STDZD_PYMT_PC',
        'home_health': 'HH_MDCR_STDZD_PYMT_PC',
        'hospice': 'HOSPC_MDCR_STDZD_PYMT_PC',
        'evaluation_management': 'EM_MDCR_STDZD_PYMT_PC',
        'procedures': 'PRCDRS_MDCR_STDZD_PYMT_PC',
        'tests': 'TESTS_MDCR_STDZD_PYMT_PC',
        'imaging': 'IMGNG_MDCR_STDZD_PYMT_PC',
        'durable_medical_equipment': 'DME_MDCR_STDZD_PYMT_PC',
        'outpatient_dialysis': 'OP_DLYS_MDCR_STDZD_PYMT_PC',
        'fqhc_rhc': 'FQHC_RHC_MDCR_STDZD_PYMT_PC',
        'ambulance': 'AMBLNC_MDCR_STDZD_PYMT_PC',
        'part_b_drugs': 'PTB_DRUGS_MDCR_STDZD_PYMT_PC',
    }
    # Combine the categories for per capita costs
    aggregated_categories_dict = {
        'total_costs_per_capita':[
            standardized_costs_dict['total_costs']
        ],
        'inpatient_per_capita': [
            standardized_costs_dict['inpatient']
        ],
        'post_acute_care_per_capita': [
            standardized_costs_dict['skilled_nursing_facility'],
            standardized_costs_dict['inpatient_rehab'],
            standardized_costs_dict['long_term_care_hospital'],
            standardized_costs_dict['home_health']
        ],
        'hospice_per_capita': [
            standardized_costs_dict['hospice']
        ],
        'physician_opd_per_capita': [
            standardized_costs_dict['evaluation_management'],
            standardized_costs_dict['outpatient'],
            standardized_costs_dict['ambulatory_surgery'],
            standardized_costs_dict['outpatient_dialysis'],
            standardized_costs_dict['fqhc_rhc'],
            standardized_costs_dict['tests'],
            standardized_costs_dict['imaging'],
            standardized_costs_dict['procedures']
        ],
        'durable_medical_equipment_per_capita': [
            standardized_costs_dict['durable_medical_equipment']
        ],
        'part_b_drug_per_capita': [
            standardized_costs_dict['part_b_drugs']
        ],
        'ambulance_per_capita': [
            standardized_costs_dict['ambulance']
        ]
    }

    additional_elements_dict = {
        'beneficiary_count': 'BENES_WTH_PTAPTB_CNT',  # Count of Medicare beneficiaries with Part A and Part B
        'percent_eligible_medicaid': 'BENE_DUAL_PCT',  # Percent eligible for Medicaid
        'hospital_readmission_rate': 'ACUTE_HOSP_READMSN_PCT',  # Hospital readmission rate
        'ed_visits_per_1000_beneficiaries': 'ER_VISITS_PER_1000_BENES',  # ED visits per 1,000 beneficiaries
    }

    for per_capita_category, cost_columns in aggregated_categories_dict.items():
        df[per_capita_category] = df[cost_columns].sum(axis=1)
    for new_col, existing_col in additional_elements_dict.items():
        df[new_col] = df[existing_col].astype(float)

    columns_needed = set(aggregated_categories_dict.keys())
    columns_needed.update(additional_elements_dict.keys())
    essential_columns = ['YEAR', 'BENE_GEO_LVL', 'BENE_GEO_DESC', 'BENE_GEO_CD']
    columns_needed.update(essential_columns)
    df1 = df[list(columns_needed)].copy()
    columns_renames = {
        'BENE_GEO_LVL': 'geo_level',
        'BENE_GEO_DESC': 'geo_desc',
        'BENE_GEO_CD': 'geo_code',
        'YEAR': 'year'
    }
    df1 = df1.rename(columns=columns_renames)
    dashboard_df = df1.copy()
    dashboard_df = dashboard_df[['year', 'geo_level', 'geo_desc', 'geo_code', 'total_costs_per_capita',
                                'inpatient_per_capita', 'ambulance_per_capita', 'post_acute_care_per_capita',
                                'durable_medical_equipment_per_capita', 'part_b_drug_per_capita',
                                'physician_opd_per_capita', 'hospice_per_capita', 'beneficiary_count',
                                'percent_eligible_medicaid', 'hospital_readmission_rate', 
                                'ed_visits_per_1000_beneficiaries']]
    return dashboard_df

def calculate_pct_diff(dashboard_df):
    state_df = dashboard_df[dashboard_df['geo_level'].isin(['National','State'])]
    national_df = state_df[state_df['geo_level'] == 'National']

    for column in state_df.columns:
        if state_df[column].dtype == 'float64':
            # Merge national data for comparison based on the year
            state_df = state_df.merge(national_df[['year', column]], on='year', suffixes=('', '_national'))
            # Calculate percentage difference to the national value
            state_df[f'{column}_pct_diff_to_national'] = ((state_df[column] - state_df[f'{column}_national']) / state_df[f'{column}_national']) *100

    return state_df


def get_us_state_geojson(url):
    response = requests.get(url)
    geo_data = response.json()
    return geo_data

