# letterboxd-fans
<h2><a href = "https://docs.google.com/spreadsheets/d/1uAvvD6t5Kl_w8uZs47fj9abIOpcKBO4aQhLUbP19inU/edit?usp=sharing">Current List</a></h2>

Ranks films on <a href = "http://letterboxd.com">Letterboxd</a> by percentage of fans out of total watched.

Being a fan of a film on Letterboxd means it is one of the four "Favorite Films" on a user's profile, as can be seen <a href = "http://letterboxd.com/alda/">here on my profile</a>.

Scrapes Letterboxd's pages for its <a href = "http://letterboxd.com/films/popular/">most popular films</a> and its <a href = "http://letterboxd.com/films/by/rating/">top rated films</a>, gathering all the URLs.
Then, scrapes each URL to find film info, number of fans, and number of people who watched each film.
Congregates all this information into a CSV file, then sorts the films by percent fans out of watched. The file only includes films with a percent at least 1%. 

The final file, uploaded <a href = "https://docs.google.com/spreadsheets/d/1uAvvD6t5Kl_w8uZs47fj9abIOpcKBO4aQhLUbP19inU/edit?usp=sharing">here</a> on Google Sheets, also includes a list of directors sorted by the number of times they appear on the list.

I used `requests` and `BeautifulSoup` to scrape.
