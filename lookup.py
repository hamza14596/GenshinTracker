import requests
import time

char_url = 'https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json'
loc_url = 'https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json'

def loadup_data():
    response_char = requests.get(char_url)
    response_loc = requests.get(loc_url)
    char_data = response_char.json()
    loc_data = response_loc.json()
    loc_data = loc_data['en']

    return char_data, loc_data

def get_character_name(char_id, char_data, loc_data):
    char_info = char_data.get(str(char_id))
    name_hash = char_info.get('NameTextMapHash')
    char_name = loc_data.get(str(name_hash))
    return char_name

def get_char_icon(char_id, char_data):
    char_info = char_data.get(str(char_id))
    icon_name = char_info.get('SideIconName')
    icon_name = icon_name.replace('_Side', '')
    icon_url = f'https://enka.network/ui/{icon_name}.png'
    return icon_url

def get_item_name(name_hash, loc_data):
    item_name = loc_data.get(str(name_hash))
    return item_name

def get_item_icon_url(icon_name):
    icon_url = f'https://enka.network/ui/{icon_name}.png'
    return icon_url

if __name__ == "__main__":
    char_data, loc_data = loadup_data()

    name = get_character_name(10000007, char_data, loc_data)
    print(name)

    icon = get_char_icon(10000007, char_data)
    print(icon)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GenshinTracker/1.0"
    }

    r = requests.get("https://enka.network/api/uid/611865256/", timeout=20,headers=headers)
    print("status code:", r.status_code)
    player_data = r.json()
    print("has avatarInfoList:", "avatarInfoList" in player_data)

    if "avatarInfoList" in player_data:
        weapon_entry = player_data["avatarInfoList"][0]["equipList"][-1]
        real_hash = weapon_entry["flat"]["nameTextMapHash"]
        print("hash:", real_hash)
        print("item name:", get_item_name(real_hash, loc_data))
        icon_name = weapon_entry["flat"]["icon"]
        print(get_item_icon_url(icon_name))
    else:
        print("avatarInfoList not found for this UID")
        print(r.text[:3000])