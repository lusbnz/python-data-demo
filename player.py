import requests
import json
import concurrent.futures
import time

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch_player_data(player_id, retries=3):
    urls = {
        "profile": f"https://transfermarkt-api.fly.dev/players/{player_id}/profile",
        "market_value": f"https://transfermarkt-api.fly.dev/players/{player_id}/market_value",
        "transfers": f"https://transfermarkt-api.fly.dev/players/{player_id}/transfers",
        "stats": f"https://transfermarkt-api.fly.dev/players/{player_id}/stats",
        "injuries": f"https://transfermarkt-api.fly.dev/players/{player_id}/injuries"
    }
    
    player_data = {}
    
    for key, url in urls.items():
        for attempt in range(retries):
            try:
                response = requests.get(url)
                response.raise_for_status()
                player_data[key] = response.json()
                break
            except requests.exceptions.HTTPError as err:
                player_data[key] = {"error": str(err)}
                break
            except requests.exceptions.SSLError as ssl_err:
                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    player_data[key] = {"error": str(ssl_err)}
            except Exception as e:
                player_data[key] = {"error": str(e)}
                break
    
    return {player_id: player_data}

def fetch_all_player_data(players):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_player_data, player['id']): player for player in players}
        
        for future in concurrent.futures.as_completed(futures):
            player_id = futures[future]['id']
            try:
                result = future.result()
                results.update(result)
            except Exception as e:
                print(f"Error fetching data for player ID {player_id}: {e}")
    
    return results

def save_player_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    club_data = load_json('club_data.json')
    
    players = []
    for club_id, data in club_data.items():
        players.extend(data.get('players', {}).get('players', []))
    
    player_data = fetch_all_player_data(players)
    
    save_player_data_to_json(player_data, 'player_data.json')
