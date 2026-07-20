import requests
import json
import streamlit as st
from lookup import loadup_data, get_character_name, get_char_icon, get_item_name, get_item_icon_url,get_stat_name

artifact_name_shown = False
artifact_substats = []

uid = st.text_input('Enter ur UID: ')


st.title("Genshin Tracker ")

char_data, loc_data = loadup_data()

@st.cache_data
def get_player_data(uid):

    url = f'https://enka.network/api/uid/{uid}/'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GenshinTracker/1.0"
        }

    response = requests.get(url, headers=headers, timeout=20)
    return response

response = get_player_data(uid)
if response.status_code == 200:
    data = response.json()     
    if st.session_state.get('current_char') == None:
        if st.button('Account Details'):
            player_info = data.get('playerInfo')
            player_name = player_info.get('nickname','N/A')
            player_signature = player_info.get('signature','N/A')

            player_pp = player_info.get('profilePicture')
            player_avatar = player_pp.get('avatarId')
            player_avatar_icon = None
            if player_pp:
                player_avatar_icon = get_char_icon(str(player_avatar), char_data)

            player_AR = player_info.get('level','N/A')
            player_worldlvl = player_info.get('worldLevel','N/A')
            player_achievements = player_info.get('finishAchievementNum','N/A')

            player_abyss_T = player_info.get('towerFloorIndex','N/A')
            player_abyss_L = player_info.get('towerLevelIndex','N/A')

            player_theatre_level = player_info.get('fetterCount')
            player_theatre_Index = player_info.get('stygianIndex')
            player_theatre_time = player_info.get('stygianSeconds')

            st.subheader(player_name)
            st.subheader(f'**| AR:** {player_AR} **| World Level:** {player_worldlvl} |')
            st.image(player_avatar_icon,width=150)
            st.write(player_signature)


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
            if st.button(char_name):
                st.session_state.current_char = char_id
                st.rerun()
            char_icon_url = get_char_icon(char_id, char_data) 
            st.image(char_icon_url, width=100)
            st.subheader('')
    else:   
            if st.button('Character List'):
                del st.session_state['current_char']
                st.rerun()
            selected_id = st.session_state.get('current_char')
            selected_char = None

            for char in data.get("avatarInfoList", []):
                if char.get('avatarId') == selected_id:
                    selected_char = char
                    break
            char_name = get_character_name(selected_id, char_data, loc_data)
            if selected_char.get('talentIdList') is None:
                constellation_num = 0
            else:
                constellation_num = len(selected_char.get('talentIdList'))
            artifacts= []
            for item in selected_char.get('equipList'):
                if 'reliquary' in item:
                    artifacts.append(item)
            char_level =  selected_char.get('propMap').get('4001').get('val')
            char_icon_url = get_char_icon(selected_id, char_data)
            weapon_dict = selected_char.get('equipList')[-1]
            weapon_name = get_item_name(str(weapon_dict.get('flat').get('nameTextMapHash')), loc_data)
            weapon_image_url = get_item_icon_url(weapon_dict.get('flat').get('icon'))
            st.write(char_name,'Lv :',char_level,' | Constellations: ', constellation_num)
            st.image(char_icon_url, width=200)
            st.subheader(f'Weapon: {weapon_name}')
            st.image(weapon_image_url, width=100)
            for artifact in artifacts:
                flat = artifact.get('flat',{})

                raw_hash = flat.get('setNameTextMapHash')
                
                if raw_hash is None:
                    continue

                string_hash = str(raw_hash)

                artifact_name = get_item_name(string_hash, loc_data)
                if not artifact_name:
                    artifact_name = f"Unknown Artifact (Hash: {string_hash})" 
                if artifact_name_shown == False:
                    st.subheader(artifact_name)
                    artifact_name_shown = True
                    
                artifact_url = get_item_icon_url(flat.get('icon'))
                artifact_main = flat.get('reliquaryMainstat',{})
                artifact_substats = flat.get('reliquarySubstats',[])
                st.image(artifact_url, width=100)
                main_stat_name = get_stat_name(artifact_main.get('mainPropId'))
                main_stat_val =  str(artifact_main.get('statValue'))
                st.write(f"**{main_stat_name}** {main_stat_val}")
                for substat in artifact_substats:
                    st.write('-'+get_stat_name(substat.get('appendPropId')),str(substat.get('statValue')))
                st.subheader('')
 
 


else:
    st.write(f'Error: {response.status_code}')