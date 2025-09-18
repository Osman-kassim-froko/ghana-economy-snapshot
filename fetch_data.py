import requests
import pandas as pd
import wbdata
import os

# FRED API Key
api_key = "467fe69919c067bbe2cf724fd86c501e"

# Dictionary of FRED series IDs for key economic indicators for Ghana
# These indicators help tell the story of the economy: inflation, GDP, growth, unemployment, interest rates, exchange rates, etc.
fred_series = {
    'inflation': 'FPCPITOTLZGGHA',  # Inflation, consumer prices (annual %)
    'gdp': 'MKTGDPGHA646NWDB',  # Gross Domestic Product (current US$)
    'gdp_per_capita': 'PCAGDPGHA646NWDB',  # GDP per capita (current US$)
    'gdp_growth': 'GHANGDPRPCPPPT',  # Real GDP growth (annual %)
    'unemployment': 'SLUEMTOTLZSGHA',  # Unemployment, total (% of total labor force)
    'youth_unemployment': 'SLUEM1524ZSGHA',  # Youth unemployment rate (% ages 15-24)
    'lending_rate': 'DDDI12GHA156NWDB',  # Lending interest rate (%)
    'deposit_rate': 'DDDI01GHA156NWDB',  # Deposit interest rate (%)
    'exchange_rate': 'FXRATEGHA618NUPN',  # Exchange rate to US Dollar (national currency per USD)
    'current_account_balance_percent_gdp': 'BPBLTT01GHA637S'  # Current account balance (% of GDP)
}

# Generalized function to fetch data from FRED for multiple series
def get_fred_data(series_dict):
    os.makedirs('data', exist_ok=True)  # Ensure 'data' directory exists
    
    for name, series_id in series_dict.items():
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json().get('observations', [])
            
            if not data:
                print(f"No data returned for series: {series_id}")
                continue
            
            df = pd.DataFrame(data)[['date', 'value']]
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'])
            
            # Save to CSV
            csv_path = f'data/{name}.csv'
            df.to_csv(csv_path, index=False)
            print(f"Saved {name} data to {csv_path}")
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {series_id}: {e}")

# Fetch GSE data (manual CSV or API)
def get_gse_data():
    try:
        # Fetch data from AFX GSE CSV URL (ensure the URL is correct)
        url = "https://afx.kwayisi.org/gse/data.csv"  # Update with the correct URL if needed
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the raw content temporarily to a file
        with open('temp_gse.csv', 'wb') as f:
            f.write(response.content)
        
        df = pd.read_csv('temp_gse.csv')
        
        # Filter the data for top 10 stocks (you can modify this based on your needs)
        df = df[['stock', 'price', 'ytd_return']].head(10)
        
        # Ensure 'data' directory exists
        os.makedirs('data', exist_ok=True)
        
        df.to_csv('data/gse_stocks.csv', index=False)
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GSE data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing GSE data: {e}")
        return pd.DataFrame()
    finally:
        # Clean up temporary file
        if os.path.exists('temp_gse.csv'):
            os.remove('temp_gse.csv')

# Hardcode bank data (for comparison)
def get_bank_data():
    try:
        # Example bank data with hardcoded product and rate information
        banks = pd.DataFrame({
            'Bank': ['Ecobank', 'GCB', 'Fidelity'],
            'Product': ['High-Yield Savings', 'Goal-Based Account', 'Fixed Deposit'],
            'Rate': [15, 12, 18]  # Interest rates
        })
        
        # Ensure 'data' directory exists
        os.makedirs('data', exist_ok=True)
        
        # Save bank data as CSV
        banks.to_csv('data/banks.csv', index=False)
        return banks
    
    except Exception as e:
        print(f"Error processing bank data: {e}")
        return pd.DataFrame()

# Run all functions to fetch data and save to CSV
def fetch_all_data():
    print("Fetching FRED economic indicators data...")
    get_fred_data(fred_series)
    
    print("Fetching GSE data...")
    get_gse_data()
    
    print("Fetching bank data...")
    get_bank_data()
    
    print("Data fetching complete!")

# Call the fetch_all_data function to execute all tasks
if __name__ == "__main__":
    fetch_all_data()