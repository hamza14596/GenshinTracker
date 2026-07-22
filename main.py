import requests
import json
import streamlit as st
from lookup import loadup_data, get_character_name, get_char_icon, get_item_name, get_item_icon_url,get_stat_name, get_namecard_url

artifact_name_shown = False
artifact_substats = []

uid = st.text_input('UID: ')

st.set_page_config(layout='wide')
st.title("Genshin Tracker ")

char_data, loc_data, namecard_data = loadup_data()

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
    if 'show_acc_info' not in st.session_state:
         st.session_state.show_acc_info = False

    if st.session_state.show_acc_info:
                player_info = data.get('playerInfo')
                player_name = player_info.get('nickname','N/A')
                player_signature = player_info.get('signature','N/A')

                player_pp = player_info.get('profilePicture')
                player_avatar = player_pp.get('avatarId') or player_pp.get('id')
                player_avatar_icon = None
                player_namecardId = player_info.get('nameCardId')
                player_MainNamecardURL = get_namecard_url(player_namecardId,namecard_data)

                if player_avatar:
                    player_avatar_icon = get_char_icon(str(player_avatar), char_data)

                player_AR = player_info.get('level','N/A')
                player_worldlvl = player_info.get('worldLevel','N/A')
                player_achievements = player_info.get('finishAchievementNum','N/A')

                player_abyss_T = player_info.get('towerFloorIndex','N/A')
                player_abyss_L = player_info.get('towerLevelIndex','N/A')

                player_theatre_data = player_info.get('theater',{})
                player_theatre_act = player_info.get('actIndex','N/A')

                stygian_data = player_info.get('stygian',{})
                player_stygian_level = player_info.get('stygianLevel','N/A')
                player_stygian_time = player_info.get('stygianSeconds','N/A')

                showcased_namecard_ids = player_info.get('showNameCardIdList',[])
            
                showcase_urls = []

                for namecard_id in showcased_namecard_ids:
                     url = get_namecard_url(namecard_id, namecard_data)
                     if url:
                          showcase_urls.append(url)
                          


                if st.button('Character List'):
                    st.session_state.show_acc_info = False
                    st.rerun()
                st.subheader(player_name)
                st.subheader(f'**| AR:** {player_AR} **| World Level:** {player_worldlvl} |')
                if player_avatar_icon:
                    st.image(player_avatar_icon,width=150)
                else:
                     st.write('No Avatar Icon')
                if player_signature:
                    st.write('Signature:',player_signature)
                if player_MainNamecardURL:
                    st.write('**Profile Namecard**')
                    st.image(player_MainNamecardURL,width=200)
                if showcase_urls:
                     st.write("**Namecards:**")
                     st.image(showcase_urls,width=100)
                st.write('Achievements: ', player_achievements)
                st.write(f'**Spiral Abyss:** {player_abyss_T}-{player_abyss_L}')
                st.write(f'**Theater:** {player_theatre_act} ')
                st.write(f'**Stygian Onslaught in:** {player_stygian_time}s')
                
 

    elif st.session_state.get('current_char') == None:
            
            if st.button('Show Player Details'):
                 st.session_state.show_acc_info = True
                 st.rerun()
            st.subheader('')   

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

                talent_labels = ["Normal", "Skill", "Burst", "Sprint"]

                skill_level = selected_char.get('skillLevelMap',{})
                
                char_info = char_data.get(str(selected_id),{})
                skill_order = char_info.get('SkillOrder',[])
                skill_info = char_info.get('Skills',{})



                    


                fight_props = selected_char.get('fightPropMap', {})

                total_hp = int(fight_props.get('2000',0))
                total_atk = int(fight_props.get('2001',0))
                total_def = int(fight_props.get('2002',0))
                total_em = int(fight_props.get('28',0))

                crit_rate = int(fight_props.get('20',0) * 100)
                crit_dmg = int(fight_props.get('22',0) * 100)
                er = int(fight_props.get('23',0) * 100)


                char_level =  selected_char.get('propMap').get('4001').get('val')
                char_icon_url = get_char_icon(selected_id, char_data)
                weapon_dict = selected_char.get('equipList')[-1]
                weapon_name = get_item_name(str(weapon_dict.get('flat').get('nameTextMapHash')), loc_data)
                weapon_image_url = get_item_icon_url(weapon_dict.get('flat').get('icon'))
                st.write(char_name,'Lv :',char_level,' | Constellations: ', constellation_num)
                st.image(char_icon_url, width=200)
                st.subheader(f'Weapon: {weapon_name}')
                st.image(weapon_image_url, width=100)

                st.subheader('**Total Character Stats**')
                st.write(f'**Attack:** {total_atk}')
                st.write(f'**HP:** {total_hp}')
                st.write(f'**CRIT RATE:** {crit_rate}%')
                st.write(f'**CRIT DMG:** {crit_dmg}%')
                st.write(f'**Energy Recharge:** {er}%')
                st.write(f'**Elemental Mastery:** {total_em}')
                st.subheader('**Talents**')
        
                for i,skill_id in enumerate(skill_order):
         
                    str_skill_id = str(skill_id)

                    level = skill_level.get(str_skill_id,'1')
                    

                    skill_icon = skill_info.get(str_skill_id)

                    talent_name = talent_labels[i] if i < len(talent_labels) else "Special"
                
                    st.write(f"**{talent_name} | Level:** {level} ")

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
                    st.write(f'**Main Stat:** {main_stat_name} {main_stat_val}')
                    for substat in artifact_substats:
                        artifact_substat_name = get_stat_name(substat.get('appendPropId'))
                        artifact_substat_val = str(substat.get('statValue'))
                        st.write(f" - {artifact_substat_name} : {artifact_substat_val}")
                            
                    st.subheader('')

    
else:
    st.write(f'Error: {response.status_code}')