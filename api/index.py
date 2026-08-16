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
        extracted_name = get_character_name(char_id,char_data,loc_data)

        if char_id == 10000131:
            char['name'] = "Nicole"
        else:
            char['name'] = extracted_name 

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
    weapon_info = weapon_dict.get('weapon',{})

    weapon_level = weapon_dict.get('weapon',{}).get('level',1)
    affix_map = weapon_info.get('affixMap',{})

    if affix_map:
        weapon_refinement = list(affix_map.values())[0] + 1
    else:
        weapon_refinement = 1

    fight_props = selected_char.get('fightPropMap', {})
    stats ={
        'hp': int(fight_props.get('2000',0)),
        'atk': int(fight_props.get('2001',0)),
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

    base_skills = selected_char.get('skillLevelMap',{})
    bonus_skills = selected_char.get('proudSkillExtraLevelMap',{})

    char_ref = char_data.get(str(char_id),{})


    skill_order = char_ref.get('SkillOrder',[])
    skill_icons = char_ref.get('Skills',{})
    proud_map = char_ref.get('ProudMap',{})

    talents = []
    skill_names = ["Normal Attack","Elemental Skill", "Elemental Burst"]

    if int(char_id) in CUSTOM_CHARACTERS:
        raw_skill_ids = sorted(list(base_skills.keys()))

        custom_icons = CUSTOM_CHARACTERS[int(char_id)].get("talent_icons",[])


        for i,str_skill_id in enumerate(raw_skill_ids):

            if i>=3:
                break
            
            base_level = base_skills.get(str_skill_id,1)


            icon_url = custom_icons[i] if i < len(custom_icons) else None

            talents.append({
                'name': skill_names[i],
                'level': base_level,
                'icon_url':icon_url,
                'is_boosted': False
            })
    else:
        for i,skill_id in enumerate(skill_order):
            if i>=3:
                break

            str_skill_id = str(skill_id)
            base_level = base_skills.get(str_skill_id,1)
            proud_id = str(proud_map.get(str_skill_id,""))
            bonus_level = bonus_skills.get(proud_id,0)

            final_level = base_level + bonus_level

            icon_name = skill_icons.get(str_skill_id)
            icon_url = f"https://enka.network/ui/{icon_name}.png" if icon_name else None

            talents.append({
                "name": skill_names[i],
                "level": final_level,
                "icon_url":icon_url,
                "is_boosted":bonus_level > 0
            })

    return render_template('character.html',
                            uid=uid, name=char_name, level=char_level,
                            icon=char_icon, constellations=constellations,
                            weapon_name=weapon_name,weapon_icon=weapon_icon,weapon_level=weapon_level,
                            weapon_refinement=weapon_refinement,
                            stats=stats, artifacts=artifacts, talents=talents)