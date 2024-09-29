import requests
import concurrent.futures
import json

list_ids = ["GB1", "ES1"]

base_url = "https://transfermarkt-api.fly.dev/competitions/{}/clubs?season_id=2024"

def fetch_api(id):
    try:
        response = requests.get(base_url.format(id))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        return {"id": id, "error": str(err)} 

def fetch_all_apis(list_ids):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_api, id) for id in list_ids]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    api_results = fetch_all_apis(list_ids)
    save_to_json(api_results, 'competition_data.json')