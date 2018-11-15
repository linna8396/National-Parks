## proj_nps.py
## Skeleton for Project 2, Fall 2018
## ~~~ modify this file, but don't rename it ~~~
from secrets import google_places_key
from bs4 import BeautifulSoup
from alternate_advanced_caching import Cache
import requests
import json

state_url_front = "https://www.nps.gov/state/"
state_url_end = "/index.htm"
nearbysearch_base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
geolocation_base_url = "https://maps.googleapis.com/maps/api/geocode/json"
## you can, and should add to and modify this class any way you see fit
  ## 这个class可以改
## you can add attributes and modify the __init__ parameters,
  ## 可以改constructor
##   as long as tests still pass
  ## 只要test过就行了
##
## the starter code is here just to make the tests run (and fail)
class NationalSite():
    def __init__(self, type, name, desc, url=None):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url

        # needs to be changed, obvi.
        self.address_street = '123 Main St.'
        self.address_city = 'Smallville'
        self.address_state = 'KS'
        self.address_zip = '11111'

## you can, and should add to and modify this class any way you see fit
  ## 这个class也可以随便改
## you can add attributes and modify the __init__ parameters,
  ## 可以改constructor
##   as long as tests still pass
  ## 只要test过就行了
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name):
        self.name = name

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov

## 也就是说，pass一个state进来，要返回一串nationalsites（并不知道是啥）
## 哦，知道了，就是nps.gov上的那些公园啥的
def get_sites_for_state(state_abbr):
    state_url = state_url_front + state_abbr + state_url_end
    cache = Cache("national_sites.json")
    national_sites = cache.get(state_url)

    if not national_sites:
        national_sites = []
        print("I retrieve this data online.")
        web_data = requests.get(state_url).text

        national_sites_soup = BeautifulSoup(web_data, "html.parser")
        national_sites_list = national_sites_soup.find_all("li", class_ = "clearfix")

        for national_site in national_sites_list:
            try:
                site_name = national_site.find("h3").text
                site_type = national_site.find("h2").text
                national_sites.append(site_name + " " + site_type)
            except:
                pass
        cache.set(state_url, national_sites, 30)
    return national_sites

def params_unique_combination(baseurl, params_d, private_keys=["key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

def get_geolocation_info(national_site):
    params_dic = {"key": google_places_key, "address": national_site}
    unique_identifier = params_unique_combination(geolocation_base_url, params_dic)
    cache = Cache("geolocation_info.json")
    geolocation_json = cache.get(unique_identifier)

    if not geolocation_json:
        print("I get this data from the Google API.")
        result = requests.get(geolocation_base_url, params = params_dic)
        geolocation_json = json.loads(result.text)
        cache.set(unique_identifier, geolocation_json, 30)

    lng = 0
    lat = 0
    try:
        geolocation = geolocation_json["results"][0]['geometry']['location']
        lng = geolocation['lng']
        lat = geolocation['lat']
    except:
        pass
    return lng, lat

## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list

## pass一个公园名啥的进来
## 返回一串10公里以内的NearbyPlaces
## 没有的话就返回空list
def get_nearby_places_for_site(national_site):
    lng, lat = get_geolocation_info(national_site)
    params_dic = { "key": google_places_key,
                   "location": str(lat) + "," + str(lng),
                   "radius": 10000 }
    unique_identifier = params_unique_combination(nearbysearch_base_url, params_dic)
    cache = Cache("nearby_places.json")
    places_json = cache.get(unique_identifier)

    if not places_json:
        print("I get this data from the Google API.")
        result = requests.get(nearbysearch_base_url, params = params_dic)
        places_json = json.loads(result.text)
        cache.set(unique_identifier, places_json, 30)

    nearby_places_list = []
    try:
        places = places_json["results"]
        for place in places:
            nearby_places_list.append(place['name'])
    except:
        pass

    return nearby_places_list

## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser

## pass一个state的缩写
## 画出所有公园的位置
## 如果google没找着这个地儿，直接pass
## 不用return任何东西，画就行了
## 画的时候需要在浏览器里打开一个画好的页面
def plot_sites_for_state(state_abbr):
    pass

## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser

## pass一个地儿，画不超过20个NearbyPlaces
## 不用return任何东西
## 画的时候需要在浏览器里打开一个画好的页面
def plot_nearby_for_site(site_object):
    pass

print(get_sites_for_state("al"))

print(get_nearby_places_for_site("Birmingham Civil Rights National Monument"))
print(get_nearby_places_for_site("Freedom Riders National Monument"))
