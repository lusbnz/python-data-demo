import requests
import concurrent.futures
import json

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch_club_profile(club_id):
    base_url_profile = f"https://transfermarkt-api.fly.dev/clubs/{club_id}/profile"
    try:
        response = requests.get(base_url_profile)
        response.raise_for_status()
        return {"club_id": club_id, "profile": response.json()}
    except requests.exceptions.HTTPError as err:
        return {"club_id": club_id, "profile_error": str(err)}

def fetch_club_players(club_id):
    base_url_players = f"https://transfermarkt-api.fly.dev/clubs/{club_id}/players?season_id=2024"
    try:
        response = requests.get(base_url_players)
        response.raise_for_status()
        return {"club_id": club_id, "players": response.json()}
    except requests.exceptions.HTTPError as err:
        return {"club_id": club_id, "players_error": str(err)}

def fetch_club_data(club_ids):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_club_profile, club_id): club_id for club_id in club_ids}
        futures.update({executor.submit(fetch_club_players, club_id): club_id for club_id in club_ids})
        
        for future in concurrent.futures.as_completed(futures):
            club_id = futures[future]
            try:
                result = future.result()
                if club_id not in results:
                    results[club_id] = {}
                if 'profile' in result:
                    results[club_id]['profile'] = result['profile']
                elif 'players' in result:
                    results[club_id]['players'] = result['players']
            except Exception as e:
                print(f"Error fetching data for club ID {club_id}: {e}")
    
    return results

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    competition_data = load_json('raw_data/competition.json')
    
    club_ids = []
    for competition in competition_data:
        for club in competition.get('clubs', []):
            club_ids.append(club['id'])

    club_data = fetch_club_data(club_ids)

    save_to_json(club_data, 'raw_data/club.json')
