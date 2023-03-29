import googlemaps
import requests
import json
import time
from requests.models import PreparedRequest
from flask import Flask, redirect, render_template, request


# Configure application
app = Flask(__name__)

# Set API key
API_KEY = 'AIzaSyCR-g9qwyqVaMLTlp6_vMuUzk9ESgTDe4I'

gmaps = googlemaps.Client(key = API_KEY)

@app.route("/")
def index():

    return render_template("home.html")

@app.route("/location", methods=["GET", "POST"])
def location():

    if request.method == "POST":
        
        # get google search results for user input startpoint
        startpoint = request.form.get("startpoint")
        
        #URL to get info from Google Places API
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + startpoint + "&inputtype=textquery&fields=place_id%2Cgeometry&key=" + API_KEY

        payload={}
        headers = {}

        # convert result from json to dict
        startjson = requests.request("GET", url, headers=headers, data=payload)
        startdict = json.loads(startjson.text)

        # access the lattitude and longitude information contained in the dict
        start_lat = startdict['candidates'][0]['geometry']['location']['lat']
        start_lng = startdict['candidates'][0]['geometry']['location']['lng']

        #create URL to redirect to, containing startpoint, start_lat, and start_lng parameters
        req = PreparedRequest()

        url = "http://127.0.0.1:5000/search"
        params = {'startpoint':startpoint, 'start_lat':start_lat, 'start_lng':start_lng}
        req.prepare_url(url, params)

        #req.url takes the url above, and adds each item in params as query parameters to the url
        return redirect(req.url, code=301)

    else:

        return render_template("location.html", API_KEY=API_KEY)

@app.route("/search", methods=["GET", "POST"])
def search():

#    if startpoint == None:

#        return render_template("location.html", API_KEY=API_KEY)

    if request.method == "POST":

        #get input from user via html form
        destination = request.form.get("destination")

        #convert miles to meters (which is what google api uses)
        distance_m = int(float(request.form.get("distance")) * 1609)

        #hidden input fields with values generated from /location route
        startpoint = request.form.get("startpoint")
        start_lat = request.form.get("start_lat")
        start_lng = request.form.get("start_lng")

        #create URL to redirect to, containing startpoint, start_lat, and start_lng, destination, and distance parameters
        req = PreparedRequest()

        url = "http://127.0.0.1:5000/results"
        params = {'startpoint':startpoint, 'start_lat':start_lat, 'start_lng':start_lng, 'destination':destination, 'distance_m':distance_m}
        req.prepare_url(url, params)

        #req.url takes the url above, and adds each item in params as query parameters to the url
        return redirect(req.url, code=301)

    else:

        #get query parameters
        args = request.args

        #get query parameters from url
        startpoint = args.get("startpoint")
        start_lat = args.get("start_lat")
        start_lng = args.get("start_lng")

        return render_template("search.html", startpoint=startpoint, start_lat=start_lat, start_lng=start_lng)        


@app.route("/results")
def results():

    #get query parameters
    args = request.args

    #get query parameters from url
    startpoint = args.get("startpoint")
    start_lat = args.get("start_lat")
    start_lng = args.get("start_lng")
    destination = args.get("destination")
    distance = args.get("distance_m")

    #Get first 20 results matching user input
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(start_lat) + "%2C" + str(start_lng) + "&radius=" + str(distance) + "&keyword=" + destination + "&maxResults=100&key=" + API_KEY

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
        
    #Create dictionary of results
    responsedict = json.loads(response.text)

    topresultsdict = {}

    count = 0

    #infinite loop that keeps getting the next set of 20 results from google until there is no next page token
    while True:

        #Iterate through each result
        for i in range(len(responsedict['results'])):

            #check to make sure business is listed as operational
            if 'business_status' in responsedict['results'][i] and responsedict['results'][i]['business_status'] == 'OPERATIONAL':
                
                #create empty dictionary for the business
                topresultsdict[count] = {}
                    
                #copy over the keys/values we're interested in
                topresultsdict[count]['place_id'] = responsedict['results'][i]['place_id']
                topresultsdict[count]['name'] = responsedict['results'][i]['name']
                topresultsdict[count]['rating'] = responsedict['results'][i]['rating']
                topresultsdict[count]['user_ratings_total'] = responsedict['results'][i]['user_ratings_total']
                topresultsdict[count]['business_status'] = responsedict['results'][i]['business_status']
                topresultsdict[count]['lat'] = responsedict['results'][i]['geometry']['location']['lat']
                topresultsdict[count]['lng'] = responsedict['results'][i]['geometry']['location']['lng']

                #count only gets incremented if the business was operational and therefor copied into topresultsdict
                count += 1
        
        #if next_page_token exists, then there is at least 1 more result that wasn't included in the first group of 20 results   
        if 'next_page_token' in responsedict:
            
            next_page_token = responsedict['next_page_token']
                
            #THIS IS NECESSARY! Pause to let the next_page_token register on google's end of things, before making the call for the next 20 results.  I tried 1 second and it didn't work.  2 seconds seems to work every time.
            time.sleep(2)
                
            #overwrite responsedict with the next group of results
            responsedict = gmaps.places_nearby(page_token = next_page_token)
                
        #if there is no next_page_token in responsedict, then there are no more results to be gathered from google
        else:
            break

    topresultslist = []

    #add each place from topresultdict to a list that can be sorted
    for place in topresultsdict:

        topresultslist.append(topresultsdict[place])

    #sort by rating, descending order (highest to lowest rating)
    sortedresults = sorted(topresultslist, key=lambda d: d['rating'], reverse=True)

    return render_template("results.html", destination=destination, distance=distance, startpoint=startpoint, sortedresults=sortedresults)