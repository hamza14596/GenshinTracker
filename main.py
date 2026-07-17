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
        
        # If lookup.py returns None, skip to the next character
        if char_name is None:
            continue
            
        st.write(char_name)
        st.write("id:", char_id)
else:
    st.write(f'Error: {response.status_code}')