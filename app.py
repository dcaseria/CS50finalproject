import os

import googlemaps
import pprint
import requests
import json
import time

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session


# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
# b = SQL("sqlite:///finance.db")

# Set API key
API_KEY = 'AIzaSyCR-g9qwyqVaMLTlp6_vMuUzk9ESgTDe4I'

gmaps = googlemaps.Client(key = API_KEY)

startpoint = None
destination = None

@app.route("/")
def index():

    return render_template("home.html")

@app.route("/location", methods=["GET", "POST"])
def location():

    if request.method == "POST":

        global startpoint
        global start_lat
        global start_lng
        
        # get google search results for user input startpoint
        startpoint = request.form.get("startpoint")
        
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + startpoint + "&inputtype=textquery&fields=place_id%2Cgeometry&key=" + API_KEY

        payload={}
        headers = {}

        # convert result from json to dict
        startjson = requests.request("GET", url, headers=headers, data=payload)
        startdict = json.loads(startjson.text)

        # access the lattitude and longitude information contained in the dict and save to global variables
        start_lat = startdict['candidates'][0]['geometry']['location']['lat']
        start_lng = startdict['candidates'][0]['geometry']['location']['lng']

        return render_template("search.html", startpoint=startpoint, start_lat=start_lat, start_lng=start_lng, API_KEY=API_KEY)

    else:

        return render_template("location.html", API_KEY=API_KEY)

@app.route("/search", methods=["GET", "POST"])
def search():

#    if startpoint == None:

#        return render_template("location.html", API_KEY=API_KEY)

    if request.method == "POST":

        destination = request.form.get("destination")
        travelmode = request.form.get("mode")
        distance = request.form.get("distance")
        distance_m = int(float(request.form.get("distance")) * 1609)
        
#        start_details = gmaps.places(start_id)

#        test_id = start_details['results']

        #Get first 20 results matching user input
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(start_lat) + "%2C" + str(start_lng) + "&radius=" + str(distance_m) + "&keyword=" + destination + "&maxResults=100&key=" + API_KEY

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        
        #Create dictionary of results
        responsedict = json.loads(response.text)

        

        topresultsdict = {}

        count = 0

        #Create new dictionary of only the important information
        for i in range(len(responsedict['results'])):

            if 'business_status' in responsedict['results'][i] and responsedict['results'][i]['business_status'] == 'OPERATIONAL':
            
                topresultsdict[count] = {}
                
                topresultsdict[count]['place_id'] = responsedict['results'][i]['place_id']
                topresultsdict[count]['name'] = responsedict['results'][i]['name']
                topresultsdict[count]['rating'] = responsedict['results'][i]['rating']
                topresultsdict[count]['user_ratings_total'] = responsedict['results'][i]['user_ratings_total']
                topresultsdict[count]['business_status'] = responsedict['results'][i]['business_status']

                count += 1
    
        if 'next_page_token' in responsedict:
        
            #Use next_page_token to get results 21-40 and then 41-60.  Google maps documentation specifies a max of 60 results

            next_page_token = responsedict['next_page_token']

            for i in range(3):
            
                time.sleep(2)
                
                responsedict = gmaps.places_nearby(page_token = next_page_token)
                #responsedict = json.loads(response)

                for i in range(len(responsedict['results'])):
                    
                    if 'business_status' in responsedict['results'][i] and responsedict['results'][i]['business_status'] == 'OPERATIONAL':
                    
                        topresultsdict[count] = {}
                        
                        topresultsdict[count]['place_id'] = responsedict['results'][i]['place_id']
                        topresultsdict[count]['name'] = responsedict['results'][i]['name']
                        topresultsdict[count]['rating'] = responsedict['results'][i]['rating']
                        topresultsdict[count]['user_ratings_total'] = responsedict['results'][i]['user_ratings_total']
                        topresultsdict[count]['business_status'] = responsedict['results'][i]['business_status']

                        count += 1
                
                if 'next_page_token' in responsedict:
                    next_page_token = responsedict['next_page_token']
                
                else:
                    break
        
        topresultslist = []

        for place in topresultsdict:

            topresultslist.append(topresultsdict[place])

        sortedresults = sorted(topresultslist, key=lambda d: d['rating'], reverse=True)

        return render_template("results.html", destination=destination, distance=distance, startpoint=startpoint, response=topresultsdict, sortedresults=json.dumps(sortedresults), API_KEY=API_KEY)

    else:

        return render_template("search.html")

