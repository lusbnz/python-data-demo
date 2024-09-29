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
                break  # Thoát khỏi vòng lặp nếu gọi thành công
            except requests.exceptions.HTTPError as err:
                player_data[key] = {"error": str(err)}
                break  # Thoát khỏi vòng lặp nếu gặp lỗi HTTP
            except requests.exceptions.SSLError as ssl_err:
                if attempt < retries - 1:  # Nếu không phải lần thử cuối
                    time.sleep(1)  # Chờ một chút trước khi thử lại
                else:
                    player_data[key] = {"error": str(ssl_err)}
            except Exception as e:
                player_data[key] = {"error": str(e)}
                break  # Thoát khỏi vòng lặp nếu gặp lỗi không xác định
    
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
    # Tải dữ liệu các câu lạc bộ từ file JSON
    club_data = load_json('club_data.json')
    
    # Lấy danh sách tất cả cầu thủ từ dữ liệu câu lạc bộ
    players = []
    for club_id, data in club_data.items():
        players.extend(data.get('players', {}).get('players', []))
    
    # Lấy dữ liệu cho tất cả cầu thủ
    player_data = fetch_all_player_data(players)
    
    # Lưu tất cả dữ liệu cầu thủ vào một file JSON duy nhất
    save_player_data_to_json(player_data, 'player_data.json')
