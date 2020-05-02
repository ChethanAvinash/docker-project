from locationiq.geocoder import LocationIQ
from distance import Haversine
import geocoder
from flask import Flask,render_template,request,send_from_directory
import folium
from newsapi import NewsApiClient
import pandas as p
import os
import json
import requests 
from bs4 import BeautifulSoup 
import numpy as np 

g=LocationIQ("0e7221f9c35daf")
session={}

app=Flask(__name__,"")

@app.route("/")
@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/news")
def home():
	
	n=NewsApiClient(api_key="af7efd1b69c8489fa159bfdc8da6d05a")
	top=n.get_top_headlines(q="corona",page_size=100)
	a=top["articles"]
	title=[]
	description=[]
	url=[]
	for i in a:
		title.append(i["title"])
		description.append(i["description"])
		url.append(i["url"])
	list_=zip(title,description,url)
	return render_template("home.html",context=list_)

@app.route("/check",methods=["GET","POST"])
def check():
	if request.method=='POST':
		session["name"]=request.form['name']
		session["email"]=request.form['mail']
		session["phone"]=request.form['num']
		session["street"]=request.form['street']
		session["district"]=request.form['district']
		session["state"]=request.form['state']

	return render_template("check.html")

@app.route("/safe")
def safe():
	d=p.read_csv("File.csv")
	k=g.geocode(" ".join([session.get("street",""),session.get("district",""),session.get("state","")]))
	if len(k)>0:
		lat=k[0]['lat']
		lon=k[0]['lon']
	distances=[]
	session["Latitude"]=lat
	session["Longitude"]=lon
	for i in range(len(d)):
		distances.append(Haversine([d['Latitude'][i],d['Longitude'][i]],[float(lat),float(lon)]).km)
	nearest=min(distances)
	nearest_hotspot=d['Places'][distances.index(nearest)]
	if nearest<=2:
		alert=True
	else:
		alert=False
	session["alert"]=alert
	return render_template("result.html",d=[round(nearest,1),nearest_hotspot,alert])

@app.route("/map")
def get_map():
	r = requests.get(url='https://api.covid19india.org/data.json')
	statewise_covid_data = json.loads(r.content)['statewise']

	with open('capital_data.json', 'r') as f:
	    json_text = f.read()
	    
	city_data = json.loads(json_text)


	for i in range(1,len(statewise_covid_data)):
	    for j in range(len(city_data)):
	        if statewise_covid_data[i]['statecode'] == city_data[j]['statecode']:
	            city_data[j]['confirmed'] = statewise_covid_data[i]['confirmed']
	            city_data[j]['deaths'] = statewise_covid_data[i]['deaths']
	            break


	mp = folium.Map(location = [city_data[1]['lat'],city_data[1]['lng']],zoom_start= 5)

	for i in range(len(city_data)):
	    if float(city_data[i]['deaths']) > 50:
	        folium.Marker(location = [city_data[i]['lat'],city_data[i]['lng']],
	                      popup = city_data[i]['state'],
	                      icon=folium.Icon(color='darkred',icon_color='white',icon='remove-sign',),
	                      tooltip = 'deaths: ' + city_data[i]['deaths'] + ' confirmed: ' + city_data[i]['confirmed']
	                     ).add_to(mp)
	    elif float(city_data[i]['deaths']) > 20:
	        folium.Marker(location = [city_data[i]['lat'],city_data[i]['lng']],
	                      popup = city_data[i]['state'],
	                      icon=folium.Icon(color='red',icon_color='white',icon='ban-circle',),
	                      tooltip = 'deaths: ' + city_data[i]['deaths'] + ' confirmed: ' + city_data[i]['confirmed']
	                     ).add_to(mp)
	    elif float(city_data[i]['deaths']) > 0:
	        folium.Marker(location = [city_data[i]['lat'],city_data[i]['lng']],
	                      popup = city_data[i]['state'],
	                      icon=folium.Icon(color='orange',icon_color='white',icon='warning-sign',),
	                      tooltip = 'deaths: ' + city_data[i]['deaths'] + ' confirmed: ' + city_data[i]['confirmed']
	                     ).add_to(mp)
	        
	    elif float(city_data[i]['deaths']) == 0:
	        folium.Marker(location = [city_data[i]['lat'],city_data[i]['lng']],
	                      popup = city_data[i]['state'],
	                      icon=folium.Icon(color='green',icon_color='white',icon='ok-circle',),
	                      tooltip = 'deaths: ' + city_data[i]['deaths'] + ' confirmed: ' + city_data[i]['confirmed']
	                     ).add_to(mp)

	mp.save('templates/mymap.html')
	return render_template("mymap.html")

@app.route("/checkmap")
def checkmap():
	d=p.read_csv("File.csv")
	mp=folium.Map(location=[d["Latitude"][0],d["Longitude"][0]],zoom_start=8)
	folium.CircleMarker(location=[d["Latitude"][0],d["Longitude"][0]],radius=20,popup=d["Places"][0],color='#8B0000',fill=True,fill_color='#8B0000').add_to(mp)
	place = d[ ['Latitude', 'Longitude'] ]
	place = place.values.tolist()[1:]	
	for i,point in enumerate(place):
	    if d["Type"][i]=="Red":
	        folium.CircleMarker(location=point,radius=20,popup=d["Places"][i],color='#8B0000',fill=True,fill_color='#8B0000').add_to(mp)    
	    elif d["Type"][i]=="Orange":
	        folium.CircleMarker(location=point,radius=20,popup=d["Places"][i],color='#FFA500',fill=True,fill_color='#FFA500').add_to(mp)  
	if session["alert"]:
		folium.Marker(location=[session["Latitude"],session["Longitude"]], 
              popup='Your Location' , 
              icon=folium.Icon(color='darkred',icon_color='white',icon='remove-sign') 
             ).add_to(mp)
	else:
		folium.Marker(location=[session["Latitude"],session["Longitude"]], 
              popup='Your Location' , 
              icon=folium.Icon(color='darkblue',icon_color='white',icon='warning-sign') 
             ).add_to(mp)
	mp.save('templates/yourloc.html')
	return render_template("yourloc.html")

@app.route("/cases")
def allcases():
	extract_contents = lambda row: [x.text.replace('\n', '') for x in row] 
	URL = 'https://www.mohfw.gov.in/'
	response = requests.get(URL).content 
	soup = BeautifulSoup(response, 'html.parser') 
	header = extract_contents(soup.tr.find_all('th'))   
	stats = [] 
	all_rows = soup.find_all('tr') 
	  
	for row in all_rows:
		stat = extract_contents(row.find_all('td'))
		if stat:
			if len(stat)==5:
				stats.append(['',*stat])
	objects=[]
	Total_cases=[]
	Total_cured=[]
	Total_deaths=[]
	for r in stats:
		if "#" in r[5]:
			r[5]=r[5][:-1]
		objects.append(r[2])
		Total_cases.append(r[3])
		Total_cured.append(r[4])
		Total_deaths.append(r[5])
	c_sum=sum([int(i) for i in Total_cases])
	cu_sum=sum([int(i) for i in Total_cured])
	d_sum=sum([int(i) for i in Total_deaths])
	index=list(range(0,len(objects)))
	return render_template("case.html",d=[objects,Total_cases,Total_deaths,Total_cured,index,c_sum,cu_sum,d_sum])

	
if __name__=="__main__":
	app.run(port=4030,debug=True)


