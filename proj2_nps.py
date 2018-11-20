## proj_nps.py
## Skeleton for Project 2, Fall 2018
## ~~~ modify this file, but don't rename it ~~~
from secrets import google_places_key
from bs4 import BeautifulSoup
from alternate_advanced_caching import Cache
import requests
from states_dict import abbr_dict
import json

nps_home_url = "https://www.nps.gov"

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
    def __init__(self, type, name, desc, url = None):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url

        # needs to be changed, obvi.
        self.address_street = ''
        self.address_city = ''
        self.address_state = ''
        self.address_zip = ''
        self.lat = 0
        self.lng = 0

    def __str__(self):
        return "{} ({}): {}, {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state, self.address_zip)
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
    def __str__(self):
        print(self.name)

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov

## 也就是说，pass一个state进来，要返回一串nationalsites（并不知道是啥）
## 哦，知道了，就是nps.gov上的那些公园啥的
def website_scraping_and_cache(url):
    cache = Cache("national_sites.json")
    result = cache.get(url)

    if not result:
        result = requests.get(url).text
        cache.set(url, result, 30)

    return BeautifulSoup(result, 'html.parser')

def get_sites_for_state(state_abbr):
    national_sites = []

    # scrape the homepage and get the national sites url for the given state
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
        name = site.find("h3").text.strip()
        type = site.find("h2").text.strip()

        description = site.find("p").text.strip()
        # here we find the url for the specific national site
        site_url = nps_home_url + site.find("a")["href"].strip()
        # scrape the webpage of the specific national site to get the location info
        site_soup = website_scraping_and_cache(site_url)
        try:
            # handle the special issue of Death Valley in CA
            if site_soup.find("span", itemprop = "postOfficeBoxNumber"):
                # 这里不知道是不是要排成一行比较好
                street = "P.O. Box " + site_soup.find("span", itemprop = "postOfficeBoxNumber").text.strip()
            else:
                street = site_soup.find("span", itemprop="streetAddress").text.strip()

            city = site_soup.find("span", itemprop = "addressLocality").text.strip()
            state = site_soup.find("span", itemprop = "addressRegion").text.strip()
            zip = site_soup.find("span", itemprop = "postalCode").text.strip()

        except: # the location info hides in the next page level
            # get the url of the contact info page and scrape it to get the location info
            # print(name + "does not have mailing address")
            try:
                print(name)
                print(site_url)
                contact_info_url = nps_home_url + site_soup.find("a", string = "Contact the Park")["href"]
                contact_info_soup = website_scraping_and_cache(contact_info_url)
                contact_info = contact_info_soup.find("div", class_ = "ArticleTextGroup").text
                # find the index of where the address part start in the bulk of text
                address_idx = contact_info.find("Mailing Address")
                contact_info = contact_info[address_idx:]
                contact_info = contact_info.split("\n")[1:]
                contact_info_clean = [item for item in contact_info if item is not '']
                street = contact_info_clean[0].strip()
                for each_street in contact_info_clean[1:-1]:
                    street +=  " " + each_street.strip()
                city = contact_info_clean[-1].split()[0][:-1]
                state = contact_info_clean[-1].split()[1]
                zip = contact_info_clean[-1].split()[2]
            except:
                street = ""
                city = ""
                state = ""
                zip = ""

        site_class = NationalSite(type, name, description, site_url)
        site_class.address_street = street
        site_class.address_city = city
        site_class.address_state = state
        site_class.address_zip = zip
        national_sites.append(site_class)

    # for c in national_sites:
    #     print(c)
    print(len(national_sites))
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
    lng, lat = get_geolocation_info(national_site.name + " " + national_site.type)
    if lng == 0 and lat == 0:
        print("wrong location info for " + str(national_site))
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
            nearby_places_list.append(NearbyPlace(place['name']))
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

# for key in abbr_dict:
#     print(key)
#     get_sites_for_state(key)
#     print("-" * 100)
# get_sites_for_state("ca")
#print(get_nearby_places_for_site("Birmingham Civil Rights National Monument"))
#print(get_nearby_places_for_site("Freedom Riders National Monument"))
