
import requests

char_url =  'https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/characters.json'
loc_url = 'https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json' 

def loadup_data():
    response_char = requests.get(char_url)
    response_loc = requests.get(loc_url)
    char_data = response_char.json()
    loc_data = response_loc.json()
    loc_data = loc_data['en']

    return char_data,loc_data

if __name__ == '__main__':
    char_data, loc_data = loadup_data()
    print(type(char_data))
    print(len(char_data))
    print(type(loc_data))
    print(len(loc_data))
    print(loc_data.get("1006042610"))
