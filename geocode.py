import requests
import json

URL = "https://geocoder.ls.hereapi.com/6.2/geocode.json"
KEY = "cPICkfe3-CN03mffsk2OmeH_Sz_E9UeIePwJfQq1AAo"
BATCH_URL = "https://batch.geocoder.ls.hereapi.com/6.2/job"
CONTENT_TYPE_HEADER = {"Content-Type: text/plain"}


def here(api_key, addresses_list):
    coords = []
    for address in addresses_list:
        params = {"apiKey": api_key, "searchtext": address}
        resp = requests.get(url=URL, params=params)
        if not resp.json()["Response"]["View"]:
            address_label = 'No data'
            geocoded_address_coords = {"Latitude": 0, "Longitude": 0, "AddressLabel": address_label}
            coords.append(geocoded_address_coords)
            continue
        address_label = resp.json()["Response"]["View"][0]["Result"][0]["Location"]["Address"]["Label"]
        geocoded_address_coords = resp.json()["Response"]["View"][0]["Result"][0]["Location"]["DisplayPosition"]
        geocoded_address_coords["AddressLabel"] = address_label
        coords.append(geocoded_address_coords)
    return coords


def get_json_fields_names(file_name):
    with open(file_name) as json_file:
        data = json.load(json_file)
    return list(data[0].keys())


def gather_adresses_by_field(file_name, field_name):
    adresses = []
    with open(file_name, encoding="utf-8") as json_file:
        data = json.load(json_file)

    for key in data:
        adresses.append(key[field_name])
    return adresses


# here(KEY, gather_adresses_by_field("partners.json", "address"))
a = {"Response":{"MetaInfo":{"Timestamp":"2020-01-11T19:14:02.459+0000"},"View":[{"_type":"SearchResultsViewType","ViewId":0,"Result":[{"Relevance":0.8,"MatchLevel":"houseNumber","MatchQuality":{"City":1.0,"District":1.0,"Street":[1.0],"HouseNumber":1.0},"MatchType":"pointAddress","Location":{"LocationId":"NT_245xJ3eqDVRQWHyoZMmxzA_5AC06CtvRDI0-CSM","LocationType":"point","DisplayPosition":{"Latitude":55.70236,"Longitude":37.94025},"NavigationPosition":[{"Latitude":55.70226,"Longitude":37.94093}],"MapView":{"TopLeft":{"Latitude":55.7034842,"Longitude":37.938255},"BottomRight":{"Latitude":55.7012358,"Longitude":37.942245}},"Address":{"Label":"улица Вертолётчиков 9 корп 1, Москва, Россия, 111674","Country":"RUS","State":"Центральный федеральный округ","County":"Москва","City":"Москва","District":"Некрасовка","Street":"улица Вертолётчиков","HouseNumber":"9 корп 1","PostalCode":"111674","AdditionalData":[{"value":"Россия","key":"CountryName"},{"value":"Центральный федеральный округ","key":"StateName"},{"value":"Москва","key":"CountyName"}]}}}]}]}}

print(a["Response"]["View"][0]["Result"][0]["Location"]["DisplayPosition"])

# def batch_here(api_key):
#     print(data)
#     params = {"apiKey": api_key}
#     resp = requests.get(url=URL, data=data, params=params, headers={'Content-Type': 'text/plain', 'charset':'UTF-8'}).text
#     print(resp)
