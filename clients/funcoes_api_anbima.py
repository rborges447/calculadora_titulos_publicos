import pandas as pd
import requests
from tqdm import tqdm
import base64
 
client_id = "ZJoAwzdT3k8U"
client_secret = "JvuVr9L4wsjG"
 
 
def auth_anbima(client_id, client_secret):
    url = 'https://api.anbima.com.br/oauth/access-token'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}
    data = {'grant_type': 'client_credentials'}
    response = requests.post(url, headers=headers, json=data)
    print(response.text)
    return response.json()['access_token']
 
access_token = auth_anbima(client_id, client_secret)
 
 
headers = {'Content-Type': 'application/json',
           'client_id': client_id,
           'access_token': access_token}
 
 
# Function to fetch data from the API for a given date
def fetch_data(url, date):
    params = {'data': date}
    try:
        response = requests.get(url, headers=headers, params=params)
        # If the response is 404, skip to the next date
        if response.status_code == 404:
            return None
        else:
            return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
 
# Function to loop through dates from start_date to end_date
def fetch_data_for_dates(url, date_list):
    data_list = []

    for current_date in tqdm(date_list):
        result = fetch_data(url, current_date)
        if result is not None:
            json_response = result
            data_list.append(json_response)
 
    return data_list
 
from datetime import datetime, timedelta
 
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
# Example usage
start_date = yesterday  # Start from this date
end_date = '2018-01-03'  # End at this date
 
# Convert strings to datetime objects
current_date = datetime.strptime(start_date, "%Y-%m-%d")
end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
 
# Generate list of all dates between start_date and end_date (inclusive)
date_list = [(current_date - timedelta(days=x)).strftime("%Y-%m-%d") for x in range((current_date - end_date_dt).days - 1)]

#data_list_debentures = fetch_data_for_dates("https://api.anbima.com.br/feed/precos-indices/v1/titulos-publicos/mercado-secundario-TPF", date_list)




# Bloco condicional para garantir que o código só execute quando for executado diretamente
if __name__ == "__main__":
    # Teste simples no arquivo principal
    data = pd.Timestamp.today()
    url = "https://api.anbima.com.br/feed/precos-indices/v1/titulos-publicos/vna"
    vna= fetch_data(url, date)
    print(vna)