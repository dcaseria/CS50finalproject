# CS50finalproject
A web app that takes a starting location, search query, and search radius as inputs and returns a list of results ranked by average google rating, with links to google maps driving directions.

## Intro to Project
I wanted to build something map-based and useful to me.  I always find it a little tedious when I'm somewhere new and need to figure out where to eat, for example. 

I typically use google maps to search, but if I search for, say, mexican food, and I'm in a big city, pins pop up all over the map and I have to sift through them all to find out which ones are good and which ones aren't.
I often times find myself wondering which mexican food place is most highly rated near here...well...that's exactly what this web app can be used for.

## Initial Concept
Initially, I wanted to involve many more search parameters.  I wanted to give users the option to choose a mode of transportation, and choose either a max distance or max time based on that mode of transportation.
As I got into the project, I realized that I would need to simplify for version 1 of this app for the sake of time.  Perhaps in a later version.

## New Skills
#### SVG
At the very beginning, I wanted to create a basic logo.  It was fun to learn SVG basics to design a little logo that also doubles as a link back to the homepage.

#### API
I used an API during the CS50 Finance Project.  It was pretty neat to see all the information that APIs make available, but the entire function that communicated with the API in that project had been pre-written.  All I had to do was correctly implement the function call.  

For this project, I wanted to dig into APIs a bit more and figure out how to use them.  Luckily, Google has some great documentation and videos showing how to format URLs for calls to their APIs, and also how the response will be formatted.
It was fun learning how to harness the power of such a large database as Google's.

#### Query Parameters
The biggest unexpected skill I learned was query parameters.  While testing my app I found that refreshing a particular page didn't always yield the same result.  Specifically, if I had 2 tabs open, if I submitted form data in one tab, and refreshed the other, it would use the new form data submitted from the other tab to render it's page.
This was becase initially, I had python store user submitted data in variables...effectively making it so that only one person could use the app at a time.
I learned how to instead use query parameters to pass the form data around, so it is never stored in the python app for longer than the time it takes to render the next flask route.  
Using query parameters to pass user input around makes it so that multiple people can be using my app at the same time, searching for different things, and not impacting other peoples' results.

## How it all works
#### File Structure
I have an app.py file that contains all the backend code defining all flask routes, making API calls, and rendering templates.  
The layout.html contains basic page layout and used a basic bootstrap template for the overall page design.
The home.html, location.html, search.html, and results.html all extend layout.html and use jinja to render the page display with parameters passed in from app.py.

#### Walkthrough
home.html is rendered first.  Clicking **Get Started** renders location.html (get request) which renders a page with a single text box asking for a starting location.
The javascript in location.html has an eventListener that is making calls to Google Places API as the user types, and generating a drop down list below the text box with suggested location based on what the user has typed so far.
Once the user enters an address and clicks **Let's Go!**, the form is submitted (via post) to the location route, which takes the user input, creates a customized URL using the user input as query parameters, and redirects to the **/search** route via the custom URL.

The **/search** route collects all the query parameters from the unique URL that was used to call it, and uses those parameters to render search.html.
Here, the user is prompted to enter a search query, and a maximum distance they are willing to travel.  The previously entered start location data is pre-populated in hidden fields within the form, so it will get submitted along with the new data when the form is submitted.  Upon submitting this form (post to **/search**) all of the data the user has entered so far gets sent back to the **/search** route, which creates another unique URL with query parameters, and redirects to the **/results** route.

The **/results** route collects all query parameters, and makes a call to Google Places API for all places matching the start location, search radius, and search query parameters entered by the user.  Google Places API only returns a max of 20 results at a time, whichever 20 Google deems most relevant.  If there are more than 20 results, a **nextpagetoken** will be included in the response.  The **/results** route checks for the presence of a **nextpagetoken** and if there is one, it uses that token to make another call for the next (up to) 20 results.  It continues to check for **nextpagetoken** and asking for the next batch of results until it receives a batch of results with no **nextpagetoken** present.

Each result (formatted as a dictionary) is added to a result list.  The result list is then sorted by the average user rating for each result dictionary.  The sorted list is used to render results.html, which uses a jinja **for loop** to create a line for each result and a custom link to Google Maps for each result.  Clicking on any of these links will open a new tab with Google Maps directions from the startpoint to whichever destination was clicked.

## Conclusion
I had a great time working on this project.  It was a fun challenge to write all the code for communicating with Google APIs.  The unexpected query parameters challenge was exciting and seemed like a very applicable skill to learn. 
I'm looking forward to working on more projects like these in the future, and perhaps coming out with a new version of this app that has a broader feature-set more in line with my initial concept.
