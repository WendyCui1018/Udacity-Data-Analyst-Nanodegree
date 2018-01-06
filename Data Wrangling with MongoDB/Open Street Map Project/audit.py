#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 18:30:56 2017

@author: wendycui
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
#import phonenumbers

OSMFILE = "../MyLA_sample.osm"
# Matches very last word in a street name
#\S+ match strings that do not contain space
#\b is used to match one position
#? the character before can occur 0 or 1 time

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) # ignore whether the character is lower or capital
postcode_re = re.compile(r'^\d{5}(?:[-\s]\d{4})?$')
fix_postcode_with_stateabbr = re.compile(r'^[A-Z]{2}\s\d{5}(?:[-\s]\d{4})?$')


#problems discovery example#
# "Sepulveda" is a Boulevard, "Mansfield" refers to North Mansfield is an Avenue，"Figueroa" is a street, 'Penthouse'actually should not count 
#'Thibault': cannot find an accurate address called this, just a part of some places' name. Disgard!!
# add street type for first three
# ended with digit should be discard, because when auditing, we can just find the key word(street type) in attribute['v'] and decide which street type it is


street_type_standard = ['Plaza', 'Stars', 'West', 'North', 'Road', 'Floor','Avenue', 'Broadway', 'Way', 'Lane',
                        'Boulevard', 'Drive', 'Circle', 'East', 'South', 'Place', 'Terrace', 'Trail', 'Street',
                        'Wasteland', 'park', 'Fall', 'Falls', 'Garden', 'Gardens', 'Highway', 'Pond', 'Club', 
                        'Corner', 'Course', 'Center', 'Parkway', 'Tunnel', 'Ridge', 'Cross', 'Light', 'Esplanade', 
                        'Ford', 'Bridge', 'Bayou', 'Heights', 'Lake', 'Square', 'Manor', 'Way', 'Grove', 'Landing',
                        'Station', 'Junction', 'Hills', 'Hill', 'Freeway', 'Ranch', 'Lodge', 'Mall', 'Estates',
                        'Island', 'Village', 'Field', 'Boulevard', 'River', 'Spring', 'Alley', 'Drive', 'Haven', 
                        'Key', 'Pass', 'Bend', 'Court', 'Loop', 'Dam', 'Vista', 'Walk', 'Union', 'Place', 'Glen',
                        'Driveway', 'Commons', 'Pines', 'Row', 'Gateway', 'Arcade', 'Cliffs', 'Courts', 'Crescent', 
                        'Path', 'Cove', 'Branch', 'Creek', 'Hotel', 'Steps','Store', 'Stop', 'Wood', 'Block']

stree_type_ignore = ['E','#C','#A']
street_type_abbr_map = {"Dr" : "Drive", "Ave" : "Avenue", "avenue": "Avenue", "St" : "Street", "Str" : "Street", 
                        "St." : "Street", "Blvd" : "Boulevard", "blvd" : "Boulevard", "Rd" : "Road", "Fl" : "Floor", 
                        "floor" : "Floor", "Ct": "Court", "Hwy": "Highway", "Pkwy" : "Parkway", "Pky" : "Parkway",
                        "S" : "South", "W" : "West", "N" : "North", "E" : "East"}                     
def audit_street_type(street_types, street_name, need_map):
    stan = street_type_re.search(street_name)  
    if stan:
        street_type = stan.group().lower().title()
        if len(street_type) < 2: # wrong
            return
        if not street_type[-1].isalpha():
            street_type = street_type[:-1]
        if str(street_type[0]).isdigit(): #begin with digit
            return
        if street_type in street_type_abbr_map.keys():
            #street_type = street_type_abbr_map[street_type]
            need_map[street_name] = street_name.replace(street_type, street_type_abbr_map[street_type])
        elif street_type not in street_type_standard and street_type not in stree_type_ignore:
            street_types[street_type].add(street_name)

def audit_postcode(postcode,need_simplify,all_postcode):
    postcode = postcode.strip()
    stan = postcode_re.search(postcode)
    if postcode[0:3] == 'New': # begin with "New"
        #postcode = postcode[-5:]
        need_simplify[postcode] = postcode[-5]
        #return postcode
    if fix_postcode_with_stateabbr.search(postcode): #state abbreviation and five digit
        #postcode = postcode[3:]
        #return postcode
        need_simplify[postcode] = postcode[3:]
    if stan:  #only five digit
        #return postcode
        all_postcode.add(postcode)
        

def audit_file(filename,street_types, need_map,need_simplify,all_postcode):
    for event, element in ET.iterparse(filename, events=("start",)):
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                # first audit the value when key = 'addr:street'
                if tag.attrib['k'] == 'addr:street':
                    audit_street_type(street_types, tag.attrib['v'],need_map)
                elif tag.attrib['k'] == 'addr:postcode':
                    audit_postcode(tag.attrib['v'],need_simplify,all_postcode)
                    
               
if __name__ == "__main__":
    street_types = defaultdict(set)
    need_map = {}
    all_postcode = set()
    need_simplify = {}
    audit_file(OSMFILE,street_types,need_map,need_simplify,all_postcode)
    
    
    print("street name audit:")
    print("problem category with unique examples:", street_types)
    print("the number of problem categories:",len(street_types))
    print("abbr problem, need mapping:", need_map)
    print("the number of abbr problems encounter in dataset:", len(need_map))
    
    print("postcode audit:")
    print("all 5-digit postcode:", all_postcode)
    print("the number of unique postcode in dataset", len(all_postcode))
    print("postcode that need to simplify:", need_simplify)
    
    
    


'''

#objective data structure#
nodes: [id,user,uid,version,lat,lon,timestamp,changeset]
nodes_tags: [id,key,value,type]
ways: [id,user,uid,version,timestamp,changeset]
ways_nodes[id,node_id,position]
ways_tags: [id,key,value,type]

#discover the street types in dataset where k = name#
def observe_street_type(filename):
    street_type = set()
    for event, element in ET.iterparse(filename, events=("start",)):
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                if tag.attrib['k'] == 'name':
                    #use space to delimeter the string and return the last word
                    street_type.add(tag.attrib['v'].split(' ')[-1])
    return street_type
'''
    
'''
    #results of street types observation#
    street_type = observe_street_type(OSMFILE)
    print(street_type, ' ', len(street_type))
    
    dic = ['', 'North', 'Wasteland', 'Pacific', 'Custom', 'Pretzels', 'YU/MI', 'Rochester', 'chon', 'thrityeight', 
           'Only', 'Mall', 'Burgerim', 'Repair', 'Original', 'Obagi', 'Cafeteria', "Capriotti's", 'Minolta', 
           'McDonalds', 'Chopshop', 'Ritz-Carlton', '14', 'Substation', 'Sikh', 'Partner', 'Printing', 'Cheese', 
           'Valero', 'Thayer', 'Wasabi', 'Machine', '180', 'Trimana', '733', 'Cycles', 'Burberry', 'Clemetine',
           'Condominiums', 'Wa', 'News', 'Junction', 'City', 'Mania', 'Grill', 'Diablo', 'eight', 'Institute', 
           'Boba', 'Ricci', 'Essex', 'Baskin-Robbins', 'Travel', '(former)', 'Mail', 'i', 'AT&T', 'Crescent', 
           'Crane', 'Lauren', 'photography', "Ralph's", 'I', 'Vajar', 'Citigroup', 'MacArthur', 'Bru', 'Clothing',
           'Renner', 'Synapse', 'Cream', 'Wahlberg', 'Black', 'Westholme', 'Relaxtation', '52', 'Hudson', 'Vacuum', 
           'Guitar', 'Hunger', 'Metal', 'Unit', 'Apparel', '7', '11th', 'Vermont/Beverly', 'Scientist', 'Y-Que', 
           'Restroom', 'Course', '3/8', 'Springs)', 'Asia', 'Spago', 'Zarape', 'Chipotle', 'Duarte', 'Etc.', 'Plazza',
           'Stairway', 'ONSOMESHIT', '中华人民共和国驻洛杉矶领事馆', 'Box', 'Margareta', 'Don', 'Candy', '7092', 'LaserAway', 
           '39', 'Stores', 'Street/Hope', 'andTrims', 'Blends', 'Bandini', 'Archive', 'Ascent', 'Picture', 'Vergara', 'Avenue', 
           'Corp', 'Galbi', 'Wilder', 'Foster', 'Sunday', 'floor', 'Hayek', 'Pavilions', 'Triangle', 'NY-Pizza', 'Hilgard', 
           'Control', 'Chips', 'Brunch', 'Dam', 'Eddia', 'Eckhardt', 'Bone', 'UnitiBank', 'Farms', 'Theatres', 'Vehicles', 
           'Blushington', 'Center', 'Parts', '1782', 'Turbans', 'Pharmacy', 'Matter', 'Cuisine', 'Dawn', 'Automotive', 'hills', 
           'Cava', 'Stadium', "Vic's", 'Vitamins', 'Station', 'Baroda', 'Bee', 'Island', 'ATM', 'Field', 'Malone', 'Preschool',
           'Apple', 'Diner', 'Provocateur', 'Cat', 'Construction', 'Felix', 'Jinpachi', 'Westime', 'DASH', '757', 'BarCode', 
           'Fabric', 'Wilshire/Vermont', 'Häagen-Dazs', 'Hollywood/Highland', 'III', 'Patio', 'housing', 'Bites', 'Dynasty', 
           'Stairs', 'Bbq', 'Cartier', 'Runners', 'Koreatown', 'Arts', 'Chop', 'Villa', 'Dan', 'Tailor', 'Prada', 'Esquinita', 
           '71', 'Capriccio', '204', 'park', 'Ons', "Erik's", 'Nursery', 'Bark', 'Hands', 'Philanthropy', 'Yengmani', 
           'SoulCycle', 'Cigarette', 'Statue', 'Deli', 'Harmony', '17', 'Lilly', 'Otium', 'Jivago', 'Guild.', '.', 
           'Peoples', 'Falls', "Antonio's", 'Metro', 'Art', 'Witmer', 'Spring', 'Carolwood', '#8289', "Skooby's",
           'Rainbow', 'Tabernacle', 'Conte', "Yuca's", 'Courthouse', 'Rimowa', 'veteran', 'Judson', 'Reserve', 'Presley', 
           'Kids', 'BCN', 'Fame', '78', 'Arty', 'Corporation', 'MB/MF', 'Teddys', 'Wendell', 'Royale', 'Langham', 'Estates', 
           '3976', 'Wash', 'StateFarm', 'Cita', '16350', 'Selection', 'Gardens', 'Boos', 'ReTan', 'Hollywood/Western', 
           '33', 'Brasa', 'Astoria', 'Hamburgers', 'books)', 'Chon', 'Vinci', 'DWP', 'Convent', 'Posers', 'Homes', 
           'Rooster', 'Fresh', 'Lights', 'Wings', 'Chopsticks', 'VivaVuva', 'Cornell', 'Chrysalis', 'Mausoleum', 'Lines', 'Marmont', '3263', 'Marshalls', 'Lanvin', '7-eleven', 'Barn', 'Chiropractic', 'Cleaners', 'Lot', '76', 'Block', 'Truth', 'Angeles', 'Subdivision', "McCall's", "Men's", 'Murphy', 'construction)', 'Iceyo', 'Bow', 'Blood', 'Plate', 'Sparadise', 'Chick-fil-A', 'Margot', 'supply', 'Suede', 'Lot)', 'Ricos', 'Jewelry', 'Prova', 'Conservatory', 'Bayou', 'Palladium', 'Bungalow', 'SmogPros', 'DTLA', 'Nights', '207', 'B-175', 'Lodge', 'Village', 'PoshPetCare', 'Venus', 'Dot', 'Lofts', 'Bend', 'Josephine', 'Buffalo', 'Metaphysics', 'Susman', 'Chanel', 'Walk', 'Union', "Guadalupe's", 'Bui', '26', 'stop', 'Bagels', 'Schwarzenegger', 'Stillwell', 'Beanery', 'Rental', 'Sassoon', 'Hollywood/Vine', 'Pomellato', 'Clementine', 'Fellowship', 'Wildfox', 'Building', 'Motel', 'Platinumsmiths', 'Tower', '57', 'Vincente', 'Horn', 'Soo', 'Tech', '13000139', 'Courtyard', 'USA', 'Palms', '7/11', '(Former)', 'Goodman', '100', 'Midway', 'Court', 'Wilshire/Normandie', "Roni's", 'Kmart', 'PsyD', 'Tpwer', 'Planet', '2', 'Cheeks', '#129', 'Simone', 'Cyclery', 'cafe', 'LADOT', 'Marketplace', 'Degrees', 'R', 'Brazilian', 'Milano', 'Glow', 'Fatburger', 'Guisados', 'Standard', 'Tsunami', 'Outlook', 'Health', 'Jeans', 'Francisca', 'Labs', 'Caesars', 'Bulgari', 'Hardware', 'GameStop', 'Spot', 'only)', 'Sky', 'garden', 'surveillance-cam', 'ExtraMile', '1', 'Spain', '3237', 'Galaxy', 'Mart', 'Highway', 'Harlow', 'Vine', 'Annex', 'District', '2079', 'Culture', 'Ohio', 'Wahlburgers', 'Noontide', 'Figueroa', 'Juquila', '2491', 'Kahal', 'APC', 'Bak', 'Appartments', 'DOWNTOWN', 'Serra', 'Tuileries', 'gate', "Lucy's", 'Spa', 'Shapiro', 'Vase', 'Celine', 'zpizza', 'Pad', '8', 'Bread', 'Threading', '6', 'Bibibop', 'Newsstand', 'Pit', 'Counterpoint', 'Brigade', '25', 'Francisco', 'Emporium', 'hookah', 'Brows', 'Crab', 'Ponchikanoc', '#3', 'Cathedral', 'NatureWell2', 'Thai', 'Komitas', 'tree', 'Lotus', 'Disco', 'Jackson', 'Hilton', 'Amphitheatre', 'Eveleigh', 'Café', 'Checkers', 'Flagship', 'IV', 'Ambra', 'Nail', '451', "LaRue's", 'Alley', 'Furniture', 'Hancock', 'Bridal', 'Subway', 'World', 'Loco', 'Basin', 'Guelaguetza', 'Marketing', '62', 'Swanson', 'Dorchester', 'DSWshoes', 'Ford', 'Hall', 'Altivo', 'Hostel', 'Matrix', 'MD', 'Sol', 'Odditoriums', 'Sports', 'Jerusalem', 'Borough', 'Figaro', '#21', 'Walls', 'Perch', 'Hammond', 'Surawon', 'Optometric', 'Corner', "Malone's", 'Mayfair', 'Lindbrook', 'Exhibitions', 'Sea', 'Platinum', 'Handbag', 'CVS', '12441', 'Jardin', 'Science', 'Holistic', 'Oak', 'Aahs!', 'Bongchu', 'Pretzel', 'Bell', 'Paseo', 'Pitchoun', 'NE', 'Greens', 'Rite-Aid', '31', 'Navel', 'Loan', 'Loyandford', 'GNC', 'REDCAT', 'Delicacies', 'Brooks', 'Funk', 'Gun', '37', 'Versailles', 'Agapiou', 'bibigo', '71Above', '204;754', '16', 'Hill', 'Improv-LA', 'Semi-Tropic', 'Galleria', 'Cantina', 'Providence', 'Lumber', 'Crystal', '2000', 'Robeks', 'Rolex', 'Alcove', 'B-110', "DJ'S", 'Removal', 'Grog', 'BL/NKBAR', 'Death', 'Parkway', 'Nails', 'Elysee', 'Coffieur', 'Channel', 'Light', 'Surgery', 'Scott', 'Locos', 'Eden', 'Globe', 'Plant', 'Piercing', 'Perla', 'Vintage', 'Shed', 'Boots', 'Talesai', 'Steakhouse', 'Sinopot', 'Classic', 'Gay', 'Residences', '24', 'Final', 'Schulberg', 'East', 'Sephora', 'Colab', 'Door', 'Fleischer', 'Luma', 'Vermont', 'Schwab', 'Arianna', 'Spitz', 'Audrey', 'Ross', 'Jeep', 'Brown', 'Wako', 'Tavern', 'Evian', 'Police', '82', 'Square', '300', 'VA', 'Krüger', 'Madre', 'Projects', 'Inc', 'Sopressata', 'Bonaventure', 'Museum\u200e', 'Radio', 'ShoeSource', 'Row', 'L', 'Chapel', 'Starbucks', 'Surplus', '36', 'grocery', 'Eleven', 'Creek', 'Floyds', 'West', 'Mullet', 'InterContinental', 'Flores', 'Bulding', 'Entertainment', 'Industriecutz', 'Grove', 'Service', 'Nickelodeon', 'SCHOOL', 'Lane', 'Nazarene', 'OCTA', 'Lobster', 'Lawn', "Micky's", 'Sweetgreen', 'Crosswalk', 'Party', 'Greenhouse', 'Cristo', 'T-Mobile', 'Plein', "Dom's", 'Regent', '1540', 'Cork', 'Park', 'buy', 'David', 'Marquis', 'Mobil', 'Bikecology', 'Burgers', 'Centre', 'Delancey', 'Zen', 'Donuts', 'A', 'Behavior', 'Ventura', 'Fusion', 'bbq', 'Bar', 'Monica', 'Nori', 'Alloro', 'SoHo', 'Level', 'Branch', '68', 'Xhail', 'Mansfield', 'Copies', 'Connection', 'Farmacy', 'Alpine', 'Turnaround', 'Out', 'Stelle', 'York', 'Sunset', 'Tiverton', '2903', 'Anarbagh', 'Contractors', 'KHJ-AM', 'Head', 'Geophysics', 'Loop', 'Miu', '#3369', 'Tawanna', 'Pensive', 'Driveway', 'Terminal', 'way', 'PAINTS', 'Manning', 'Balcones', 'Saaks', 'Caffe', 'Rose', 'Performances', 'Lab', 'CARCEN', 'masala', 'Tinder', '30', 'Lube', 'field', 'Mares', '15', 'YMCA', "McDonald's", 'Crustacean', 'Hostels', 'Massage', 'Italian', 'BLOCK', "D'Etoile", 'Heretic', 'Saints', 'Power', "Maus's", 'Ampitheater', 'Services', 'Irish', 'Cavalli', 'Boathouse', "Goldie's", "Johnnie's", 'Bowl', 'Bakery', 'Nushii', '3rd', 'Salad', '18', 'River)', 'Amphitheater', 'Depp', '(korean)', 'ShowPro', '6033', 'SV', 'Mischka', 'place', '4', 'Kors', 'Hospital', 'Books', 'Roddenberry', 'Savior', 'Study', 'Delta', 'M.F.T.', 'Foods', 'Diamond', 'San-Sui', 'Cienega', '9', "Flanigan's", 'LosAngeles', 'Barrel', 'Cedar', 'Shell', 'Telecommunications', 'Sweetzer', 'hotel', 'Transit', 'CAFE', 'E', 'Hole', 'Talwar', 'Kings', 'chicken', 'Pattinson', "photographers'gallery.com", 'School', 'thritysix', 'Solutions', 'Architects', 'Spirits', 'Attorneys', 'Bags', '13', 'Akbar', 'Ju', 'Gold', 'Trocadero', 'LLC', 'Pinot', 'Pizzeria', 'Marriott', 'P', 'Croissant', 'Dancing', 'Camera', 'Project', 'Bottega', 'Nokia', 'SuperCuts', 'Agency', '(historical)', 'Car', 'Kitchen', 'Pavilion', 'Wigs', 'House)', 'Seminary', 'Highland', 'Vespaio', 'Studios', 'Homme', 'Israel', 'Table', 'Barth', 'Paint', 'Autosound', 'Bicicocina', 'Community', 'Programs', 'Tantris', 'Gym', 'Shepherd', 'Dragon', 'Fubar', 'Lucy`s', 'Attorney', 'Lencería', 'Wireless', 'Law', 'Pooch', 'H20', 'Burger', 'Theater', 'Cocktails', 'Bijan', 'Clutches', 'Brothers', 'Vuitton', 'Obicà', 'Tatyana', 'Centers', 'Neveux', 'Whittier', '(South)', 'Foothill', 'Hen', 'Provence', 'Apostle', 'Denim', 'Armani', 'Records', 'Bros.', 'Room', 'Gang', 'Dietrich', 'bowl', 'Voltaire', 'Astro', 'Washington', 'Broadway', 'Darkroom', 'Fratelli', 'Robbins', 'Tropical', 'Autozone', 'Garnish', 'hollywood', 'Loma', '5th', 'Ramada', 'Mervetty', 'Hair', 'POT', 'Atch-kotch', 'mart', "BJ's", 'Donut', 'Clinic', 'After', 'Kushfly', 'Crawfords', 'Wood', 'Vicente', 'Cahuenga', 'Tabacchi', 'Kitchen24', '29', 'Sheep', 'Summit', 'Tattoo', 'Effect', "Tussaud's", 'Miller', 'Rexford', 'Scoops', 'Connector', 'Land', 'Mobile', '63', 'Wrath', 'Hollywood-Vermont/Sunset', 'Taco', 'Arax', 'Skybar', 'Classics', "Abba's", 'cevicheria', 'Congregation', 'market', 'Poki', 'Garden', '3', 'Southbound', 'Bixel', "Babbo's", 'Metro;DASH;LADOT', 'Bleu', 'Nailnation', 'Pastaio', 'Two', 'Valet', 'Canelé', 'hair', "Denny's", 'Teagardins', 'Spoon', 'Carthay', 'Mac', 'Boulevard', 'Billionaire', '3)', "Marcel's", 'Broker', 'Fitness', '79', 'Burrito', 'Aid', 'Bl', 'exterior', "Miceli's", 'Boulevard3', 'Flowers', 'well', '#552', 'Tacos', 'Chun', 'CNN', '2665', 'Demille', 'Town', 'AMPM', 'Star', 'Aussie', 'Firehouse', 'Jang', 'Rebels', 'Kashtan', 'timeless', 'Pieology', 'Ramp', 'Mexican', 'Dialnet', "Langer's", 'Hillcrest', '60', 'Pita', 'Rockwell', 'Mullin', 'Pies', 'Am', 'Parlor', 'Co', 'Normandie', 'Ord', 'Pawn', "Rise'n'grind", 'Cuties', 'Cinefamily', 'Gateway', 'Moncler', 'Noosha', 'Beatles', 'Campero', '7eleven', 'Warehouse', 'Emmanuel', 'California', 'Midas', 'Couture', "Harrison's", 'Lake', 'Ramen', 'Dance', 'Hart', 'Reina', 'Charmed', 'Hut', 'Typhoon', 'Glo', 'Shack', '3119', 'DASH;LADOT', 'fame', 'grill', 'Walgreen', 'Pines', 'Monument', 'HollywoodHostels', 'D', 'Olympic', 'Academy', 'Virgil', 'Heliport', '#16', 'Arco', 'CopyCat', 'Ladera', 'Replay', 'M', 'Share', 'Bldgs.', 'Cossamia', '11-15', 'Chilieno', 'Weitzman', "Millie'S", 'Faculty', 'Massachusetts', 'South', 'Conversation', 'Winston', 'Drugs', 'Trail', 'Blvd', 'India', 'Market', 'barre', 'Willis', 'Graphics', 'Monica)', '2A', '34', 'Details', 'Philippe', 'Wilshire/Fairfax', 'Mapleton', "Shakey's", 'Mendes', 'DEUX', 'PRHollywood', 'Residence', 'Apartments', 'liquor', 'Centro', 'Yoga', '4-5', 'B', 'Weyburn', 'Faith', 'Lalique', 'One', 'Heart', 'Terrace', 'Dogwood', 'Schools', '61', 'Cardoso', 'Leaf', 'thrityseven', 'Dome', 'Sonoratown', 'Expansion', 'BMW', 'Enterprise', 'Bridge', '(North)', 'Ave', 'Bugatta', 'Scientology', 'Exchange', 'KFC', 'Kamsah', '(seafood)', 'Pass', 'VI', 'Coffee', 'Circle', 'Diamonds', '21', 'Sleeper', 'Polish', 'Bene', 'Veteran', 'DV8', 'Dentistry', 'Street', 'Animation', 'Gallery', 'CVS/pharmacy', 'Dogs', 'Plaza', 'Armenia', 'Roku', 'Max', 'Stallone', 'Dispela', 'Road', '7-Eleven', 'CARECEN', 'វត្តខ្មែរ', 'Leather', 'Alta', 'Jolibee', 'DD', 'repair', '23', 'Movers', 'Vermont/Sunset', 'Nusskern', 'Wiltern', 'Loft', 'Secret', 'Farfalla', 'Towers', 'Reservoir', 'Grand', 'Poubelle', 'Vie', 'Men', 'Home', 'Berry', 'Sizzler', 'Dental', 'Angolo', 'Cheebo', 'Pizza', 'Republic', 'Nikon', 'Universe', '#2015', '18|8', 'Tours', 'Pantry', 'Way', 'Fargo', 'Pub', 'Fashion', 'shop', 'River', 'Maker', 'Noodle', 'Sfixio', 'Laugh', 'center', 'Subs', 'Cheques', 'Nation', '64', 'Piaget', 'Groundlings', 'Diaz', "Puran's", 'Deux', 'Mapo', 'Affairs', 'IOTA', 'Gol', '20', 'PetCo', 'Mellon', 'Hollywood', 'Cordero', 'DDS', 'Walgreens', 'Mexico', 'Poke', 'Mathematics', 'Digital', 'Music', 'Enerjuicer', 'entrance', '498', 'Nark', 'Express', 'Buzz', "Macy's", 'Rockets', 'Path', 'Units', 'Church', 'Stars', 'Paredes', 'République', 'Garde', 'Moist', 'Riese', 'Tag', 'Collectibles', 'Oil', 'Cucinelli', 'Flight', 'ZARA', 'Pastry', 'NuLegal', 'Yonada', 'Norms', 'Key', '53', 'Rentals', 'Estate', 'Liquor', 'Madonna', 'Wilshire/Western', 'Holocaust', 'NetJets', 'stores', '22', 'Bank', 'Pool', 'KandiLand', 'Dior', 'Factory', 'Apt', 'Dining', 'Buffet', 'Cory', 'Rent-a-Car', 'Roo', 'Wokcano', 'Bedford', '2017)', 'Maxazria', 'Drive', 'Atwater', 'slow', 'Cemetery', 'Venue', 'Century', 'Frank', 'Italy', 'Assimarket', 'Dorado', 'Atelier', 'Glen', 'cuisine', 'Mozza', 'Dita', 'ash', 'Cow', 'Vermut', '28', 'Condos', 'Sprint', 'Colonnade', 'Collective', 'Drybar', '2-3', 'OD', 'http://www.agedcaretests.com/index.html', '(22CN)', 'Mercury', 'Tsuri', 'Bulan', 'Halls', 'Outlet', 'Main', '(historic)', '11', 'Auditorium', 'Lounge', "Albertson's", 'King', 'B-171', 'Harari', 'Westbourne', 'MAC', 'Smokehouse', "Quizno's", 'Supplies', 'Cusine', 'Holly', "Wang's", 'June', 'Guess', 'Karoki', 'Lombard', '#8', "Cole's", "Dearden's", 'motel', 'Landing', 'Consulate', 'Gate', 'Readings', 'Ontempo', '2268', 'Hotel', 'Temple', 'Tavola', 'Steps', 'goose', 'Chevron', 'Cooper', 'Pasquale', "L'Assiette", 'Jr.®', 'Laundry', 'Sheen', 'Management', 'Meadow', 'Courts', 'Rosslyn', 'Kinesiology', 'Live', 'Straw', 'Talent', 'Ranch', 'USPS', 'Theatre', 'Nosh', 'Ferretti', 'Sportsbar', 'Tolerance', 'Fir', 'GAP', 'PixL', 'Nursing', 'Robertson', 'Chase', "Cheetah's", 'Bear', 'Girl', 'Ridge', 'Rock', 'Atlcatl', '6th', 'lair', 'PowerZone', '12', 'Inc.', "50'S", 'Teddy', 'Mortgage', 'Kumon', "Rubio's", 'Trim', 'Fox', 'SpaceSports', 'residence', 'facility', '54', 'Emerson', 'Joy', 'Cinema', '7th', 'MarketShare', 'greenwork', 'Souvenirs', '(Little)', 'Wang', 'laksky', 'Lamps', 'Leggings', 'Juicy', '612', 'Karaoke', 'Kaplan', 'court', 'Peer', 'Murakami', 'Esplanade', 'Blind', 'Goody', 'Juice', 'Recess', 'Ball', '2261', 'Legacy', "Callender's", 'Electrics', 'B-24', 'Chef', 'Google', 'tower', '10', 'FIGat7th', 'Strip', 'Medicine', 'Canon', 'Goodwill', 'II', 'Vista', '35', 'Doheny', 'Tan', 'Laboratory', 'Bookshop', 'Phukaw', 'Motorcycles', 'Net', 'Indonesia', 'yummy.com', 'Keep', 'Crossroads', 'Salon', 'Christ', 'Cellini', 'Chan', 'Region', 'Clothes', 'drop-off', 'Zone', 'Chevalier', 'Haché', 'Museum', 'Birch', 'Swing', 'Necromance', 'Sons', 'Poppy', 'Jewelery', 'Locksmith', 'Muzika', 'Glendon', 'Cinespace', 'Troubadour', 'Theory', 'Sciences', 'Dr', 'G727', 'IAC', '648', 'Pickford', 'Zion', 'APT', 'factory', 'Nonglá', 'Gucci', 'Cuticle', 'GSEIS', 'Group', 'Bogart', 'Coach', 'Tank', 'Cigarettes4Less', 'B-25', 'Western', 'Whealthy', 'Verizon', 'Ralphs', 'Complex', 'Studio', '98', 'Crenshaw', 'Belgium', '7-9', 'Hi', 'Proper', 'Journe', 'Goddess', '728', 'Zinque', 'Northbound', 'Pavillon', 'FedEx', 'Wear', 'Site', 'Less', 'Eyeworks', 'Rover', 'Costumes', 'Namsan', 'Structure', 'sculpture', 'Bellows', 'kitchen', 'Yoshinoya', 'Cinemas', '58', 'Drive-In', 'MilesImprov', 'Zoo', 'Stuidos', 'Dreams', 'Whistle', 'Air', 'Hedrick', 'Mass', 'Phonomenal', '9th', 'workspeed.com', 'Elleven', 'Sign', 'Starlux', 'house', 'Playground', 'Rawberri', 'Nordstrom', 'Heights', '8th', 'Playhouse', 'Chinese', 'Food4Less', 'EagleRider', 'Puck', 'Obelisk', 'Store', 'Metropolis', 'Extra!', 'Motherlode', 'Yamadaya', 'Pavillions', 'Pig', 'Facility', 'Equipment', 'Vita', 'Demitasse', 'Mirabella', 'Entrance', 'Choo', "Wendy's", 'Pawbar', 'Roll', 'DGX', 'Maya', 'KBLA-AM', 'Bistro', 'Tramp', 'Transportation', 'Orgánico', 'Louie', 'Sturges', 'Malo', 'Location', 'Flasher', 'Midi', 'Deutsch', 'Properties', 'ResPub', '32', 'Pictures', 'Tea', 'GALLERY', 'Forecourt', 'Spas', 'me', "Wahoo's", 'Eatery', 'griddle', 'Cafe', 'station', 'Club', 'SpireWorks', 'Sushi', '41', 'Restaurant', 'Seven', 'Jubilate', 'Banker', 'Quiznos', 'Wilshire', 'Fountain', 'B.B.Q.', 'beyond', 'C', 'Shop', 'Bikes', 'Franco', 'Valentino', 'Maple', 'Hope', 'Markets', 'Suites', 'Pingtung', 'St', 'Gabbana', 'escalator', 'Arpels', '19', 'SapOr', 'Mash', 'Motors', 'al', 'Lighting', 'Pine', 'Laurent', 'Citizen', 'International', 'Hathaway', 'Sugarfish', 'Martens', 'Belly', 'Realty', 'Ermitage', 'Masachusetts', 'Redstone', 'Evensong', 'Gatehouse', '42', 'Freeway', 'Anarkali', 'Brea', 'Kyoja', 'Department', 'Gratitude', 'Streets)', 'Freeman', 'Citibank', '51', 'Apaartments', 'Arby`s', 'Holloway', 'Ana', 'Memorial', 'Tiki-Ti', 'IHOP', 'Sav-On', 'TAGS', 'Grunberg', 'Four', 'Equinox', 'Jackmond', 'Storage', 'Chicken', 'Abbey', 'Cross', 'Jewelers', 'MiniLuxe', 'H', 'Living', 'Supply', 'Cupcakes', 'Collection', 'Florist', 'Melrose', "Prado's", 'Pastor', 'Tiger', 'Schutz', '1st', 'Buster´s', 'greenhouse', 'Headlines!', 'MGM', 'Saddles', 'Hooters', 'Wine', 'Garage', 'T', 'Co.', 'Nutritions', 'Terroni', 'China-Wok', 'Genet', 'Knight', 'Koryu', 'Cliffs', 'Body', 'spot', 'Creamery', 'Cove', 'Ciudad', 'College', 'Buona', 'Films', 'Evergreen', '27', 'Twins', 'That', 'Everything', 'Rooms', 'Greek', 'Class', 'Alba', 'Area', 'Target', 'Shiloh', 'BBQ', '7088', 'Gavilan', 'RadioShack', 'Joli', 'Perfumes', 'Place', 'Synagogue', 'office', '2229', '7-11', 'Observatory', 'Song', 'Fabrics', 'Casbah', 'Plumbing', 'Overlook', 'Parks', 'Bluemercury', 'Blackjack', 'Modani', 'Tobacco', 'Ocha', 'Go', 'Tanning', 'Westbound', 'MS', 'Bouchon', 'Eateries', 'Ensenada', 'Etiquette', 'BELLE', 'Haven', "Togo's", 'Conception', 'Frame', '1919', 'Swimwear', 'Happyland', 'Fraternity', 'LA', '44', 'Biscuits', 'Rage', 'Galbee', 'Save', 'Nations', 'Check', 'Yogurtland', '40', 'Tour', 'Mortar', 'Gardenia', 'Westwood', 'Hertz', 'cricket', '770', 'Jr.', 'Acacia', 'Stop', 'Junior', 'Milk', 'Nabeeya', 'Third', 'Sepulveda', 'Gravié', 'Primo', 'Basturma', 'Mediterranean/Deli', 'Breads', '56', 'Lifestyle', 'HSBC', 'Monster-A-Gogo', 'Germany', 'Arcade', 'Safety', 'Glamsquad', 'Outfitters', 'Food', 'Photography', 'State', 'Bookstore', "Joe's", 'Beauty', "50's", 'Life', 'America', '754', 'Bethel', 'University', 'Architecture', 'Stout', '#1', 'Anthropologie', 'Raw', 'Barbershop', 'Edgemont', 'Brosnan', 'K.', 'Satellite', 'Equity', 'Mansion', 'Library', 'Scene', 'G', 'Boss', 'Beverly', 'Thailand', 'Juk', 'Parking', 'Lahav', 'Geology', 'meters', 'Famima', 'Ajisai', '91', 'newstand', '3965', 'Mexicana', 'Staples', 'Silverlake', 'Agave', 'Bliss', 'Company', 'SalonCentric', 'General', 'Mercedes', 'Hive', 'Tunnel', 'Line', 'Makeup', 'Manor', 'Collins', 'J', 'Hills', 'Clean', 'Mosaic', 'ramen', 'Hello', 'Leash', 'Pinkrose', 'Pits', 'Wax', 'Wholesale', 'Inn', 'Pond', 'Indigo', 'Trolley', 'Guys', '3960', 'Rain', '5', 'Valintin', 'Rey', 'SW', '163', 'Religions', 'Veggie', 'DeMille', 'Downtown', 'Rufcut', 'Pets', '1759', 'Order', 'Galleries', 'Flirt', 'Mademoiselle', 'Sapp', 'Supermarket', 'Olive', 'Angels', 'Fellas', 'Fish', 'Girls', 'Ride', 'Hermes', 'HostWanted.com', 'Juicery', 'Locker', 'Associates', 'Goods', '(Vacant)', 'Guidance', 'Space', 'U-Mini', 'Goat', 'Dune', 'H&M', 'building', 'Pilates', 'Yehuda', 'Office', 'Depot', 'Sisyphus', 'House', 'cvs', 'Condor', 'Bldg.', 'Commons', 'Counter', 'Ebisu', 'Nicole', 'Feliz', 
           'Galicuts', 'Eastbound']
    
    dic_stand = ['Ridge', 'Hills', 'Bottom', 'Union', 'Brook', 'Causeway', 'Heights', 'Station', 'Hill', 'Branch', 'Lodge',
            'Isle', 'Burg', 'Dam', 'Cove', 'Landing', 'Shores', 'Trailer', 'Path', 'Haven', 'Key', 'Island', 'Camp',
            'Ferry', 'River', 'Ville', 'Creek', 'Alley', 'Course', 'Prairie', 'Corner', 'Mill', 'Glen', 'Arcade',
            'Mills', 'Plains', 'Rest', 'Bypass', 'Circle', 'Walk', 'Fork', 'Run', 'Extension', 'Park', 'Lakes', 'Ford',
            'Grove', 'Courts', 'Cape', 'Spur', 'Fort', 'Ranch', 'Orchard', 'Harbor', 'Light', 'Plaza', 'Shore', 'Green',
            'Islands', 'Loop', 'Square', 'Stream', 'Point', 'Pines', 'Viaduct', 'Mall', 'Shoal', 'Pass', 'Place', 'Row',
            'Mountain', 'Boulevard', 'Inlet', 'Bayou', 'Forest', 'Way', 'Meadows', 'Tunnel', 'Dale', 'Trail', 'Pike',
            'Lane', 'Center', 'Corners', 'Mount', 'Summit', 'Turnpike', 'Flats', 'Parkway', 'Road', 'Loaf', 'Divide',
            'Hollow', 'Locks', 'Canyon', 'Oval', 'Avenue', 'Stravenues', 'Vista', 'Court', 'Lake', 'Field', 'Forge',
            'Expressway', 'Beach', 'Forks', 'Highway', 'Neck', 'Valley', 'Manor', 'Annex', 'Track', 'Wells', 'Falls',
            'Bluff', 'Fall', 'Bend', 'Knolls', 'Fields', 'Village', 'Drive', 'Freeway', 'Estates', 'Radial', 'Crossing',
            'Junction', 'Cliffs', 'Gardens', 'View', 'Bridge', 'Trace', 'Rapids', 'Spring', 'Shoals', 'Mission', 'Port',
            'Club', 'Street', 'Terrace', 'Plain', 'Rest', 'Springs', 'Crescent', 'Gateway', 'East', 'North', 'South',
            'West', "Southwest", "Slip", "Piers", "Driveway", "Promenade", "Americas", "Finest", "Esplanade", "Farm",
            "Close", "Bush", "Commons", "Concourse", "Cross", "Mews"]
    
    dic_set = set(dic)
    dic_stand_set = set(dic_stand)
    result = dic_set - dic_stand_set
    print(result)
'''



