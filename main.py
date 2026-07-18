import requests
import json
import streamlit as st
from lookup import loadup_data, get_character_name, get_char_icon, get_item_name, get_item_icon_url


uid = st.text_input('Enter ur UID: ')

st.title("Genshin Tracker ")

char_data, loc_data = loadup_data()

url = f'https://enka.network/api/uid/{uid}/'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GenshinTracker/1.0"
    }

response = requests.get(url, headers=headers, timeout=20)
if response.status_code == 200:
    data = response.json()
    for char in data.get("avatarInfoList", []):
        char_id = char.get("avatarId")
        char_name = get_character_name(char_id, char_data, loc_data)
        
        if char_name is None:
            continue
        if char.get('talentIdList') is None:
            constellation_num = 0
        else:
            constellation_num = len(char.get('talentIdList'))
        char_level =  char.get('propMap').get('4001').get('val')
        st.write(char_name,'Lv.',char_level,'| Constellation: ',constellation_num)
        char_icon_url = get_char_icon(char_id, char_data) 
        st.image(char_icon_url, width=100)
else:
    st.write(f'Error: {response.status_code}')