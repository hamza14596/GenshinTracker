import requests
import time
from functools import lru_cache

char_url = 'https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json'
namecard_url = 'https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/namecards.json'
loc_url = 'https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json'

STAT_NAME = {
    'FIGHT_PROP_HP' : 'HP',
    'FIGHT_PROP_HP_PERCENT' : 'HP %',
    'FIGHT_PROP_ATTACK' : 'ATK',
    'FIGHT_PROP_ATTACK_PERCENT': 'ATK %',
    'FIGHT_PROP_DEFENSE': 'DEF',
    'FIGHT_PROP_DEFENSE_PERCENT': 'DEF %',
    'FIGHT_PROP_CRITICAL': 'CRIT RATE %',
    'FIGHT_PROP_CRITICAL_HURT': 'CRIT DMG %',
    'FIGHT_PROP_CHARGE_EFFICIENCY': 'ENERGY RECHARGE %',
    'FIGHT_PROP_ELEMENT_MASTERY': 'Elemental Mastery',
    'FIGHT_PROP_HEAL_ADD': 'Healing Bonus %',
    'FIGHT_PROP_FIRE_ADD_HURT': 'Pyro DMG Bonus %',
    'FIGHT_PROP_ICE_ADD_HURT': 'Cryo DMG Bonus %',
    'FIGHT_PROP_WIND_ADD_HURT': 'Anemo DMG Bonus %',
    'FIGHT_PROP_ROCK_ADD_HURT': 'Geo DMG Bonus %',
    'FIGHT_PROP_GRASS_ADD_HURT': 'Dendro DMG Bonus %',
    'FIGHT_PROP_ELEC_ADD_HURT': 'Electro DMG Bonus %',
    'FIGHT_PROP_WATER_ADD_HURT': 'Hydro DMG Bonus %',
    'FIGHT_PROP_PHYSICAL_ADD_HURT': 'Physical DMG Bonus %',
     }

CUSTOM_CHARACTERS = {
    10000131: {
        "name": "Nicole",
        "icon":"https://enka.network/ui/UI_AvatarIcon_Nicole.png",
    },
    10000125: {
        "name": "Columbina",
        "icon": "https://enka.network/ui/UI_AvatarIcon_Columbina.png"
    },
    10000128: {
        "name": "Varka:",
        "icon": "https://enka.network/ui/UI_AvatarIcon_Varka.png"
    },
    10000129:{
    "name": "Lohen",
    "icon": "https://enka.network/ui/UI_AvatarIcon_Lohen.png"
    },
    10000133: {
        "name": "Sandrone",
        "icon":"https://enka.network/ui/UI_AvatarIcon_Sandrone.png"
    },
    10000134: {
        "name":"Odette",
        "icon":"https://enka.network/ui/UI_AvatarIcon_Odette.png"
    },
    10000134:{
        "name":"Alyosha",
        "icon":"https://enka.network/ui/UI_AvatarIcon_Alyosha.png"
    }
    }


_cache = {}

@lru_cache(maxsize=1)
def get_player_data(uid):

    url = f'https://enka.network/api/uid/{uid}/'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GenshinTracker/1.0"
        }

    response = requests.get(url, headers=headers, timeout=20)
    return response.json() if response.status_code == 200 else None

def loadup_data():
    response_char = requests.get(char_url)
    response_loc = requests.get(loc_url)
    response_namecard = requests.get(namecard_url)

    char_data = response_char.json()
    loc_data = response_loc.json()
    namecard_data = response_namecard.json()
    loc_data = loc_data['en']

    return char_data, loc_data, namecard_data

def get_character_name(char_id, char_data, loc_data):

    if int(char_id) in CUSTOM_CHARACTERS:
        return CUSTOM_CHARACTERS[int(char_id)]["name"]

    char_info = char_data.get(str(char_id))
    if char_info is None:
        return f"Missing ID: {char_id}"
    
    name_hash = char_info.get('NameTextMapHash')
    char_name = loc_data.get(str(name_hash))

    return char_name

def get_char_icon(char_id, char_data):

    if int(char_id) in CUSTOM_CHARACTERS:
        return CUSTOM_CHARACTERS[int(char_id)]["icon"]

    char_info = char_data.get(str(char_id))
    if char_info is None:
        return None
    icon_name = char_info.get('SideIconName')

    if icon_name:
        icon_name = icon_name.replace('_Side', '')
        return  f'https://enka.network/ui/{icon_name}.png'

    return None

def get_namecard_url(namecard_id,namecard_data):
    if namecard_id is None:
        return None
    namecard_info = namecard_data.get(str(namecard_id),{})
    icon_name = namecard_info.get('icon')
    if icon_name:
        return f"https://enka.network/ui/{icon_name}.png"

def get_item_name(name_hash, loc_data):
    if str(name_hash).isdigit():
        for offset in [0,512,1024,1536,2048]: 
            test_hash = str(int(name_hash)+ offset)
            item_name = loc_data.get(str(test_hash))

            if item_name is not None:
                return item_name
    elif item_name is None:
        return f"Unknown Item (Hash: {name_hash})"
    return item_name
 
def get_stat_name(prop_id):
    return STAT_NAME.get(prop_id, prop_id)

def get_item_icon_url(icon_name):
    icon_url = f'https://enka.network/ui/{icon_name}.png'
    return icon_url

if __name__ == "__main__":
    fresh_loc = requests.get(loc_url).json()['en']
    print("does 3625393307 exist now:", "3625393307" in fresh_loc)
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