# To experiment with this code freely you will have to run this code locally.
# We have provided an example json output here for you to look at,
# but you will not be able to run any queries through our UI.
import json
import requests


BASE_URL = "http://musicbrainz.org/ws/2/"
ARTIST_URL = BASE_URL + "artist/"

query_type = {  "simple": {},
                "atr": {"inc": "aliases+tags+ratings"},
                "aliases": {"inc": "aliases"},
                "releases": {"inc": "releases"}}


def query_site(url, params, uid="", fmt="json"):
    params["fmt"] = fmt
    r = requests.get(url + uid, params=params)
    print ("requesting", r.url)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()


def query_by_name(url, params, name):
    params["query"] = "artist:" + name
    return query_site(url, params)


def pretty_print(data, indent=4):
    if type(data) == dict:
        print (json.dumps(data, indent=indent, sort_keys=True))
    else:
        print (data)


def main():
    ''' original examples Udacity gives
    results = query_by_name(ARTIST_URL, query_type["simple"], "Nirvana")
    print(type(results))
    pretty_print(results)

    artist_id = results["artists"][1]["id"]
    print ("\nARTIST:")
    pretty_print(results["artists"][1])

    artist_data = query_site(ARTIST_URL, query_type["releases"], artist_id)
    releases = artist_data["releases"]
    print ("\nONE RELEASE:")
    #pretty_print(releases[0], indent=2)
    release_titles = [r["title"] for r in releases]

    print ("\nALL TITLES:")
    for t in release_titles:
        print (t)
    '''
    
    # question 1 how many bands named "first aid kit"?
    results = query_by_name(ARTIST_URL, query_type["simple"], "First aid kit")
    counter = 0
    for i, artist in enumerate(results["artists"]):
        if artist["name"].lower() == "first aid kit":
            counter += 1
    print (str(counter) + ' bands named first aid kit')
    
    #question 2 begin_area name for queen
    results = query_by_name(ARTIST_URL, query_type["simple"], "queen")
    begin_area_name = []
    for artist in results['artists']:
        if(artist['name'].lower() == 'queen' and artist.__contains__('begin-area')):
            begin_area_name.append(artist['begin-area']['name'])
    print(begin_area_name)       
    
    # question3 spanish alias for beatles?
    results = query_by_name(ARTIST_URL, query_type["simple"], "beatles") 
    with open("../output_beatles_artisits.json","w") as f2:
        json.dump(results['artists'],f2) 
    alias_name = []
    for artist in results['artists']:
        if(artist['name'].lower() == "the beatles"):
            for alias in artist['aliases']:
                if(alias.__contains__('locale') and alias['locale'] == "es"):
                    #print(alias["name"])
                    if(alias.__contains__("name")):
                        alias_name.append(alias['name'])      
    print(alias_name)
    
    # question4 nirvana disambiguation?
    results = query_by_name(ARTIST_URL, query_type["simple"], "Nirvana")
    disambiguation = []
    for artist in results['artists']:
        if(artist['name'].lower() == "nirvana" and artist.__contains__('disambiguation')):
            disambiguation.append(artist['disambiguation'])
    print(disambiguation) 
    
    # question5 when was one direction formed?
    results = query_by_name(ARTIST_URL, query_type["simple"], "one direction")
    form_time = []
    for artist in results['artists']:
        if(artist['name'].lower() == "one direction" and artist.__contains__('life-span')):
            form_time.append(artist['life-span']['begin'])
    print(form_time) 
    
if __name__ == '__main__':
    main()
