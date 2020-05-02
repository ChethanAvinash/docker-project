from newsapi import NewsApiClient

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

	
