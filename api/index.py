import os
from flask import Flask, render_template, request, redirect, url_for
from lookup import *
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        uid = request.form.get('uid').strip()
        if uid:
            return redirect(url_for('display_player',uid=uid))
    return render_template('search.html')

@app.route('/player/<uid>')
def display_player(uid):
    player_data = get_player_data(uid)

    if not player_data:
        return "Error: Could not find player", 404

    char_data,loc_data, namecard_data = loadup_data()

    player_info = player_data.get('playerInfo', {})
    player_pp = player_info.get('profilePicture',{})
    avatar_id = player_pp.get('avatarId') or player_pp.get('id')

    profile_icon_url = None
    if avatar_id:
        profile_icon_url = get_char_icon(str(avatar_id),char_data)

    for char in player_data.get('avatarInfoList', []):
        char_id = char.get('avatarId')
        char['name'] = get_character_name(char_id, char_data, loc_data)
        char['icon_url'] = get_char_icon(char_id, char_data)
    
    return render_template('player.html', player_data=player_data, profile_icon_url=profile_icon_url)

@app.route('/player/<uid>/character/<int:char_id>')
def display_character(uid, char_id):
    player_data = get_player_data(uid)
    if not player_data:
        return "Error: Could not load data",404

    char_data, loc_data, namecard_data = loadup_data()

    selected_char = None
    for char in player_data.get("avatarInfoList",[]):
        if char.get("avatarId") == char_id:
            selected_char = char
            break

    if not selected_char:
        return "Character not found", 404

    char_name = get_character_name(char_id, char_data, loc_data)
    char_level = selected_char.get('propMap',{}).get('4001',{}).get('val','N/A')
    char_icon = get_char_icon(char_id, char_data)
    constellations = len(selected_char.get('talentIdList',[])) if selected_char.get('talentIdList') else 0

    equip_list = selected_char.get('equipList',{})
    weapon_dict = equip_list[-1] if equip_list else {}
    weapon_flat = weapon_dict.get('flat',{})
    weapon_name = get_item_name(str(weapon_flat.get('nameTextMapHash')), loc_data)
    weapon_icon = get_item_icon_url(weapon_flat.get('icon'))

    fight_props = selected_char.get('fightPropMap', {})
    stats ={
        'hp': int(fight_props.get('2000',0)),
        'atk': int(fight_props.get('20001',0)),
        'def': int(fight_props.get('2002',0)),
        'em': int(fight_props.get('28',0)),
        'crit_rate': int(fight_props.get('20',0)*100),
        'crit_dmg': int(fight_props.get('22',0) * 100),
        'er': int(fight_props.get('23',0)*100)              
    }

    artifacts = []
    for item in equip_list:
        if 'reliquary' in item:
            flat = item.get('flat',{})
            main_stat = flat.get('reliquaryMainstat',{})

            artifact_info ={
                'name' : get_item_name(str(flat.get('setNameTextMapHash')), loc_data),
                'icon': get_item_icon_url(flat.get('icon')),
                'main_stat_name': get_stat_name(main_stat.get('mainPropId')),
                'main_stat_val' : main_stat.get('statValue'),
                'substats': []
            }

            for sub in flat.get('reliquarySubstats',[]):
                artifact_info['substats'].append({
                    'name': get_stat_name(sub.get('appendPropId')),
                    'val': sub.get('statValue')
                })

            artifacts.append(artifact_info)

        return render_template('character.html',
                               uid=uid, name=char_name, level=char_level,
                               icon=char_icon, constellations=constellations,
                               weapon_name=weapon_name,weapon_icon=weapon_icon,
                               stats=stats, artifacts=artifacts)