import geocoder
import pandas as pd

d=pd.read_csv("data.csv")
lati=[]
longi=[]
for i in range(len(d)):
    district=d.loc[i]["Districts"]
    place=d.loc[i]["Places"]
    if district!=place:
        add=",".join([place,district])
    else:
        add=place
    g=geocoder.osm(add)
    lati.append(g.lat)
    longi.append(g.lng)

d["Latitude"]=lati
d["Longitude"]=longi    
d.to_csv("File.csv")
