## proj_nps.py
## Skeleton for Project 2, Fall 2018
## ~~~ modify this file, but don't rename it ~~~
from secrets import google_places_key
from bs4 import BeautifulSoup
from alternate_advanced_caching import Cache
import requests
from states_dict import abbr_dict # import the state abbreviations dictionary
import json
import plotly.plotly as py

nps_home_url = "https://www.nps.gov"
geolocation_base_url = "https://maps.googleapis.com/maps/api/geocode/json"
nearbysearch_base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NationalSite():
    def __init__(self, type, name, desc, url = None):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url

        self.address_street = None
        self.address_city = None
        self.address_state = None
        self.address_zip = None

        self.lat = None
        self.lng = None

    def __str__(self):
        return "{} ({}): {}, {}, {} {}".format(self.name, self.type,
                                               self.address_street,
                                               self.address_city,
                                               self.address_state,
                                               self.address_zip)

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name):
        self.name = name

        self.lat = None
        self.lng = None

    def __str__(self):
        return "{}, Geolocation: (lat) {}, (lng) {}".format(self.name, self.lat, self.lng)


# Accept a web url, use that url to get the content of the corresponding webpage.
# If the content is already cached, get the concent directly from the cache file.
# If the content is not cached, scrape the webpage to get the content and cache it.
# Return the content as a BeautifulSoup object.
def website_scraping_and_cache(url):
    cache = Cache("national_sites.json")
    result = cache.get(url)

    if not result:
        result = requests.get(url).text
        cache.set(url, result, 30)

    return BeautifulSoup(result, 'html.parser')


## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):
    national_sites = [] # the result list that stores the national sites

    # get the national sites url for the given state from the content of the homepage
    homepage_soup = website_scraping_and_cache(nps_home_url)
    all_states = homepage_soup.find("ul", class_= "dropdown-menu")
    state_url = all_states.find('a', string = abbr_dict.get(state_abbr.upper()))['href']

    # scrape the national sites page for the given state_url,
    # get the information for each national site,
    # and create a NationalSite class to store those information
    state_sites_soup = website_scraping_and_cache(nps_home_url + state_url)
    sites_wrapper = state_sites_soup.find("ul", id = "list_parks")
    sites_list = sites_wrapper.find_all("li", class_ = "clearfix")
    for site in sites_list:
        # here we find the name, type, description for each national site
        name = site.find("h3").text.strip()
        type = site.find("h2").text.strip()
        description = site.find("p").text.strip()
        # here we find the url for the specific national site
        # since we want to find the detailed address
        site_url = nps_home_url + site.find("a")["href"].strip()

        # scrape the webpage of the specific national site to get the address info
        site_soup = website_scraping_and_cache(site_url)
        try:
            # handle the special case that some sites only provide box number instead of formal address
            if site_soup.find("span", itemprop = "postOfficeBoxNumber"):
                street = "P.O. Box " + site_soup.find("span", itemprop = "postOfficeBoxNumber").text.strip()
            else:
                street = site_soup.find("span", itemprop="streetAddress").text.strip()

            street = street.replace("\n", ", ")
            city = site_soup.find("span", itemprop = "addressLocality").text.strip()
            state = site_soup.find("span", itemprop = "addressRegion").text.strip()
            zip = site_soup.find("span", itemprop = "postalCode").text.strip()

        except:
            street = city = state = zip = "N/A"

        site_class = NationalSite(type, name, description, site_url)
        site_class.address_street = street
        site_class.address_city = city
        site_class.address_state = state
        site_class.address_zip = zip
        national_sites.append(site_class)

    return national_sites


# A unique identifier generator for Google APIs based on the passed base url, params dictionary,
# and the private keys list
def params_unique_combination(baseurl, params_d, private_keys=["key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)


# Get the longitude and latitude information for the passed national site from the Google API
# Return the longitude and latitude as a tuple
def get_geolocation_info(national_site):
    params_dic = {"key": google_places_key, "address": national_site.name + " " + national_site.type}
    unique_identifier = params_unique_combination(geolocation_base_url, params_dic)
    cache = Cache("geolocation_info.json")
    geolocation_json = cache.get(unique_identifier)

    if not geolocation_json:
        result = requests.get(geolocation_base_url, params = params_dic)
        geolocation_json = json.loads(result.text)
        cache.set(unique_identifier, geolocation_json, 30)

    try:
        geolocation = geolocation_json["results"][0]['geometry']['location']
        lng = geolocation['lng']
        lat = geolocation['lat']
    except:
        lng = None
        lat = None

    return lng, lat


## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    nearby_places_list = [] # the result list that stores the nearby places

    lng, lat = get_geolocation_info(national_site)
    national_site.lat = lat
    national_site.lng = lng

    if lng == None and lat == None:
        print("There is no geolocation info for " + str(national_site) + ".")
    else:
        params_dic = { "key": google_places_key,
                       "location": str(lat) + "," + str(lng),
                       "radius": 10000 }
        unique_identifier = params_unique_combination(nearbysearch_base_url, params_dic)
        cache = Cache("nearby_places.json")
        places_json = cache.get(unique_identifier)

        if not places_json:
            result = requests.get(nearbysearch_base_url, params = params_dic)
            places_json = json.loads(result.text)
            cache.set(unique_identifier, places_json, 30)

        try:
            places = places_json["results"]
            for place in places:
                place_class = NearbyPlace(place['name'])
                try:
                    place_class.lat = place['geometry']['location']['lat']
                    place_class.lng = place['geometry']['location']['lng']
                except:
                    pass
                nearby_places_list.append(place_class)
        except:
            pass

    return nearby_places_list


# Given a list of latitude values, a list of longitude values, and
# a border adjustment value, calculate and return the geo information
# for the border and center point of the map
def find_border_and_midpoint(lat_vals, lon_vals, border_adjustment):
    min_lat = min(lat_vals)
    max_lat = max(lat_vals)
    min_lon = min(lon_vals)
    max_lon = max(lon_vals)

    lat_axis = [min_lat - border_adjustment, max_lat + border_adjustment]
    lon_axis = [min_lon - border_adjustment, max_lon + border_adjustment]
    center_lat = (max_lat + min_lat) / 2
    center_lon = (max_lon + min_lon) / 2

    return lat_axis, lon_axis, center_lat, center_lon


# Given the lists of longitude values, latitude values, and place names,
# and the size and symbol of the marker
# return a dict for the data parameter of plotly
def generate_data(lon_vals, lat_vals, text_vals, marker_size, marker_symbol):
    return dict(type = "scattergeo",
                 locationmode = 'USA-states',
                 lon = lon_vals,
                 lat = lat_vals,
                 text = text_vals,
                 mode = "markers",
                 marker = dict(size = marker_size, symbol = marker_symbol, color = "rgb(52, 52, 51)"))


# plot a map using the given data param, map title, longitude values, latitude values, and border adjustment value
def plotter(data, title, lat_vals, lon_vals, border_adjustment):
    lat_axis, lon_axis, center_lat, center_lon = find_border_and_midpoint(lat_vals, lon_vals, border_adjustment)
    layout = dict(title = title,
                  geo = dict(scope = "usa",
                             projection = dict(type = "albers usa"),
                             lataxis = dict(range = lat_axis),
                             lonaxis = dict(range = lon_axis),
                             showland = True,
                             landcolor = "rgb(237, 227, 202)",
                             subunitcolor = "rgb(176, 173, 156)",
                             center = {'lat': center_lat, 'lon': center_lon},
                             countrycolor = "rgb(217, 100, 217)",
                             showlakes = True,
                             lakecolor = "rgb(174, 218, 246)",
                             countrywidth = 3,
                             subunitwidth = 3
                            ),
                )
    fig = dict(data = data, layout = layout)
    py.plot(fig, validate = False, filename = title)


## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    lat_vals = []
    lon_vals = []
    text_vals = []

    national_sites = get_sites_for_state(state_abbr)
    for site in national_sites:
        lng, lat = get_geolocation_info(site)
        if lng != None and lat != None:
            lat_vals.append(lat)
            lon_vals.append(lng)
            text_vals.append(site.name + " " + site.type)

    sites = generate_data(lon_vals, lat_vals, text_vals, 16, "star")
    title = "National Sites for {}".format(abbr_dict[state_abbr.upper()])
    plotter([sites], title, lat_vals, lon_vals, 1)


## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_nearby_for_site(site_object):
    nearby_places = get_nearby_places_for_site(site_object)
    if site_object.lat != None and site_object.lng != None:
        lat_vals = []
        lon_vals = []
        text_vals = []
        for place in nearby_places:
            if site_object.lat != place.lat or site_object.lng != place.lng:
                lat_vals.append(place.lat)
                lon_vals.append(place.lng)
                text_vals.append(place.name)

        places = generate_data(lon_vals, lat_vals, text_vals, 10, "square")
        site = generate_data([site_object.lng], [site_object.lat], [site_object.name + " " + site_object.type], 16, "star")
        title = "Nearby Places for {}".format(site_object.name + " " + site_object.type)
        plotter([places, site], title, lat_vals, lon_vals, 0.01)
    else:
        print("There is no geolocation info for this site. No map generated.")



welcome_instruction = '''Welcome to the National Sites Program.
Here you can:
1) get a list of all the national sites in a state by providing the state's abbreviation.
2) plot all the national sites in the state you just indicate on a map.
3) get a list of 20 nearby places of a national site by providing the sequence number
of that site in the previous national sites list.
4) plot all the nearby places of a national site you just find on a map.'''

commands_instruction = '''Here is a list of commands that you can use to achieve the above
functions:
* list <stateabbr> - e.g. list MI
This command lists all the national sites in the state you indicate, with numbers beside them.

* nearby <national_site_number> - e.g. nearby 2
This command lists at most 20 nearby places of the national site with the sequence number in
the national sites list. This command is only available if you have already input list <stateabbr>.

* map - e.g. map
This command displays national sites or nearby places on a map. Whether it displays national
sites or nearby places depends on the last list you searched. If you have not searched for
anything, this command shows nothing.

* exit - e.g. exit
This command exits the program.

* help - e.g. help
This command lists all available commands you can input right now.'''

all_commands = ['list <stateabbr>', 'nearby <national_site_number>', 'map', 'exit', 'help']
available = [True, False, True, True, True]
map_what = None

print("\n")
print(welcome_instruction)
print("-" * 100)
print("\n")
print(commands_instruction)
print("-" * 100)
print("\n")
user_input = input("Please enter your command: ")
while user_input != "exit":
    if user_input.startswith("list") and len(user_input.split()) > 1:
        available[1] = True
        map_what = "sites"
        state = user_input.split()[1]
        if state.upper() in abbr_dict:
            sites_result = get_sites_for_state(state)
            for i in range(len(sites_result)):
                print("{}. {} {}".format(i + 1, sites_result[i].name, sites_result[i].type))
        else:
            print("Sorry, please enter a valid state abbreviation.")
    elif user_input.startswith("nearby") and len(user_input.split()) > 1:
        if available[1]:
            map_what = "nearby"
            try:
                index = int(user_input.split()[1]) - 1
                places_result = get_nearby_places_for_site(sites_result[index])
                for i in range(len(places_result)):
                    print("{}. {}".format(i + 1, str(places_result[i])))
            except:
                print("Sorry, please enter a valid sequence number.")
        else:
            print('''Sorry, you cannot search for nearby places unless you have already
            find a list of national sites.''')
    elif user_input == "map":
        if map_what == "sites":
            plot_sites_for_state(state)
        elif map_what == "nearby":
            plot_nearby_for_site(sites_result[index])
        else:
            print('''Sorry, I cannot show the map if you have not list national sites
            or nearby places.''')
    elif user_input == "help":
        print("All available commands right now are: ")
        for i in range(len(available)):
            if available[i]:
                print(all_commands[i])
    else:
        print("Sorry, your command is not valid. Please enter a valid command.")
    print("-" * 100)
    print("\n")
    user_input = input("Please enter your command: ")

print("You have exited the program. Thanks!")
