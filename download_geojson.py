import requests

url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-kabupaten.geojson"

response = requests.get(url)

with open("indonesia.geojson", "wb") as f:
    f.write(response.content)

print("GeoJSON berhasil didownload!")