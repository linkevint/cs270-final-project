from owlready2 import *
import pandas as pd
import json
import math

onto = get_ontology("file:///Users/kevinlin/Documents/classes/cs270/final-project/cs270-final-project/ontology/business.owl").load()
business_csv = '../yelp_dataset/yelp_academic_dataset_business.csv'
business_df = pd.read_csv(business_csv)

# retrieve businesses that have 'Restaurant' and 'Food' in 'categories'
df = business_df[business_df['categories'].notnull()]
df = df[df['categories'].str.contains('Restaurants')]
df = df[df['categories'].str.contains('Food')]

# parse 'attributes.DietaryRestrictions'
df['attributes.DietaryRestrictions'] = df['attributes.DietaryRestrictions'].replace([float('nan'), 'None'], "{'dairy-free': False, 'gluten-free': False, 'vegan': False, 'kosher': False, 'halal': False, 'soy-free': False, 'vegetarian': False}")
df['attributes.DietaryRestrictions'] = df['attributes.DietaryRestrictions'].str.replace("\'", "\"").str.replace("False", "\"False\"").str.replace("True", "\"True\"")
df = df.join(df['attributes.DietaryRestrictions'].apply(json.loads).apply(pd.Series))

# parse 'attributes.Ambience' attribute
df['attributes.Ambience'] = df['attributes.Ambience'].replace(float('nan'), "{'touristy': False, 'hipster': False, 'romantic': False, 'divey': False, 'intimate': False, 'trendy': False, 'upscale': False, 'classy': False, 'casual': False}")
df['attributes.Ambience'] = df['attributes.Ambience'].str.replace("\'", "\"").str.replace("False", "\"False\"").str.replace("True", "\"True\"").str.replace("None", "\"False\"")
df = df.join(df['attributes.Ambience'].apply(json.loads).apply(pd.Series))

# loop through dataset and create instances
i = 0
for _, row in df.iterrows():
    individual = onto.Business(row['business_id'])

    # fill 'characteristic' data properties
    individual.businessName = row['name']
    individual.stars = row['stars']
    individual.reviewCount = row['review_count']

    # fill 'location' data properties
    individual.city = row['city']
    individual.latitude = row['latitude']
    individual.longitude = row['longitude']
    ## min/max lat/long for places within 100km of business
    r = 100 / 6371
    lat_rad = math.radians(row['latitude'])
    long_rad = math.radians(row['longitude'])
    individual.minLat = math.degrees(lat_rad - r)
    individual.maxLat = math.degrees(lat_rad + r)
    d_lon = math.asin(math.sin(r) / math.cos(lat_rad))
    individual.minLon = math.degrees(long_rad - d_lon)
    individual.maxLon = math.degrees(long_rad + d_lon)

    # fill in 'operations' data properties
    hourAttributes = ['hours.Monday', 'hours.Tuesday', 'hours.Wednesday', 'hours.Thursday', 'hours.Friday',
                      'hours.Saturday', 'hours.Sunday']
    dayPrefixes = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']
    openProperties = [dayPrefix + 'OpenTime' for dayPrefix in dayPrefixes]
    closeProperties = [dayPrefix + 'CloseTime' for dayPrefix in dayPrefixes]
    for hourAttr, openProp, closeProp in zip(hourAttributes, openProperties, closeProperties):
        hours = row[hourAttr]
        if isinstance(hours, str):
            openTime, closeTime = hours.split('-')
            openHour, openMinute = [int(i) for i in openTime.split(':')]
            closeHour, closeMinute = [int(i) for i in closeTime.split(':')]
            setattr(individual, openProp, openHour + (openMinute * 0.01))
            # handle next day scenario
            if closeHour < openHour:
                setattr(individual, closeProp, 23.59)
            else:
                setattr(individual, closeProp, closeHour + (closeMinute * 0.01))

    # make multi-class individual (assign relevant parent classes)
    ## categories + dietary restriction (specialization & restaurant type)
    categories = row['categories']
    if isinstance(categories, str):
        categories = categories.split(', ')

        # American restaurants
        if 'American (Traditional)' in categories:
            individual.is_a.append(onto.TraditionalAmericanRestaurant)
        if 'American (New)' in categories:
            individual.is_a.append(onto.NewAmericanRestaurant)
        if 'Cajun/Creole' in categories:
            individual.is_a.append(onto.CajunRestaurant)
        if 'Tex-Mex' in categories:
            individual.is_a.append(onto.TexMexRestaurant)
        if 'Southern' in categories:
            individual.is_a.append(onto.SouthernRestaurant)
        if 'Hawaiian' in categories:
            individual.is_a.append(onto.HawaiianRestaurant)

        # Asian restaurants
        if 'Pan Asian' in categories:
            individual.is_a.append(onto.PanAsianRestaurant)
        if 'Taiwanese' in categories:
            individual.is_a.append(onto.TaiwaneseRestaurant)
        if 'Hakka' in categories:
            individual.is_a.append(onto.HakkaRestaurant)
        if 'Singaporean' in categories:
            individual.is_a.append(onto.SingaporeanRestaurant)
        if 'Korean' in categories:
            individual.is_a.append(onto.KoreanRestaurant)
        if 'Japanese' in categories:
            individual.is_a.append(onto.JapaneseRestaurant)
        if 'Chinese' in categories:
            individual.is_a.append(onto.ChineseRestaurant)
        if 'Shanghainese' in categories:
            individual.is_a.append(onto.ShanghaineseRestaurant)
        if 'HongKongStyleCafe' in categories:
            individual.is_a.append(onto.HongKongStyleCafe)
        if 'Cantonese' in categories:
            individual.is_a.append(onto.CantoneseRestaurant)
        if 'Asian Fusion' in categories:
            individual.is_a.append(onto.AsianFusionRestaurant)

        # Specializations
        if 'Dumplings' in categories:
            individual.specializesIn.append(onto.Dumplings)
        if 'Dim Sum' in categories:
            individual.specializesIn.append(onto.Dimsum)

        diet = row['attributes.DietaryRestrictions']
        if 'Vegetarian' in categories or row['vegetarian'] == 'True':
            individual.specializesIn.append(onto.Vegetarian)
        if 'Vegan' in categories or row['vegan'] == 'True':
            individual.specializesIn.append(onto.Vegetarian)

    ## ambience
    if row['casual'] == 'True':
        individual.hasAmbience.append(onto.CasualAmbience)
    if row['classy'] == 'True':
        individual.hasAmbience.append(onto.ClassyAmbience)
    if row['divey'] == 'True':
        individual.hasAmbience.append(onto.DiveyAmbience)
    if row['hipster'] == 'True':
        individual.hasAmbience.append(onto.HipsterAmbience)
    if row['intimate'] == 'True':
        individual.hasAmbience.append(onto.IntimateAmbience)
    if row['romantic'] == 'True':
        individual.hasAmbience.append(onto.RomanticAmbience)
    if row['touristy'] == 'True':
        individual.hasAmbience.append(onto.TouristyAmbience)
    if row['trendy'] == 'True':
        individual.hasAmbience.append(onto.TrendyAmbience)
    if row['upscale'] == 'True':
        individual.hasAmbience.append(onto.UpscaleAmbience)

    # debug
    i += 1
    if i > 1000:
        break  # full run takes a long time... save for later

lat = None
lon = None
day = 'mon'
time = 11.45
categories = ['TaiwaneseRestaurant']
ambiences = []
minStars = 2.0
minReviewCount = 1

# json = parse(json that nicholas gives us)
# lat, lon ,day ... = json
# lat = json['lat']

query = "SELECT ?x\nWHERE {\n\t?x rdf:type ?type\n\t?x business:businessName ?businessName\n"
if lat is not None and lon is not None:
    query += "\t?x business:minLat ?minLat\n\t?x business:maxLat ?maxLat\n\t?x business:minLon ?minLon\n\t?x business:maxLon ?maxLon\n"
    query += "\tFILTER (" + str(lat) + " < ?maxLat && " + str(lat) + " > ?minLat && " + str(lon) + " < ?maxLon && " + str(lon) + " > ?minLon)\n"
if day is not None and time is not None:
    query += "\t?x business:" + day + "OpenTime ?openTime\n\t?x business:" + day + "CloseTime ?closeTime\n"
    query += "\tFILTER (" + str(time) + " > ?openTime && " + str(time) + " < ?closeTime)\n"
if minStars is not None:
    query += "\t?x business:stars ?stars\n\tFILTER(?stars > " + str(minStars) + ")\n"
if minReviewCount is not None:
    query += "\t?x business:reviewCount ?reviewCount\n\tFILTER(?reviewCount > " + str(minReviewCount) + ")\n"
if len(categories) > 0:
    for cat in categories:
        """
        if cat in dishes:
            query += "\t?x business:hasDish" + cat + "\n"
        elif cat in 
        """
        query += "\t?type rdfs:subClassOf* business:" + cat + "\n"
if len(ambiences) > 0:
    for amb in ambiences:
        query += "\t?x business:hasAmbience business:" + amb + "\n"

query += "}"

print(query)
results = list(default_world.sparql(query))
print(results)