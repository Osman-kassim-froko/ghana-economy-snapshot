import requests
import pandas as pd
import wbdata

# Fetch FRED inflation data
def get_inflation():
    api_key = "bdc38ef22dd57d15be4ac28f78996659"  # FRED API Key
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GHACPIALLMINMEI&api_key={api_key}&file_type=json"
    
    try:
        # Request inflation data from FRED
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Extract the 'observations' key and load it into a DataFrame
        data = response.json().get('observations', [])
        
        if not data:
            print("No data returned from FRED API.")
            return pd.DataFrame()
        
        df = pd.DataFrame(data)[['date', 'value']]
        df['value'] = pd.to_numeric(df['value'], errors='coerce')  # Convert to numeric, handle invalid values
        df['date'] = pd.to_datetime(df['date'])  # Convert the date column to datetime
        
        # Save data as CSV in the 'data' directory
        df.to_csv('data/inflation.csv', index=False)
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FRED: {e}")
        return pd.DataFrame()

# Fetch GSE data (manual CSV or API)
def get_gse_data():
    try:
        # Fetch data from AFX GSE CSV URL (ensure the URL is correct)
        url = "https://afx.kwayisi.org/gse/data.csv"  # Update with the correct URL
        df = pd.read_csv(url)
        
        # Filter the data for top 10 stocks (you can modify this based on your needs)
        df = df[['stock', 'price', 'ytd_return']].head(10)
        df.to_csv('data/gse_stocks.csv', index=False)
        return df
    
    except Exception as e:
        print(f"Error fetching GSE data: {e}")
        return pd.DataFrame()

# Hardcode bank data (for comparison)
def get_bank_data():
    # Example bank data with hardcoded product and rate information
    banks = pd.DataFrame({
        'Bank': ['Ecobank', 'GCB', 'Fidelity'],
        'Product': ['High-Yield Savings', 'Goal-Based Account', 'Fixed Deposit'],
        'Rate': [15, 12, 18]  # Interest rates
    })
    
    # Save bank data as CSV
    banks.to_csv('data/banks.csv', index=False)
    return banks

# Run all functions to fetch data and save to CSV
def fetch_all_data():
    print("Fetching inflation data...")
    get_inflation()
    
    print("Fetching GSE data...")
    get_gse_data()
    
    print("Fetching bank data...")
    get_bank_data()
    
    print("Data fetching complete!")

# Call the fetch_all_data function to execute all tasks
fetch_all_data()
