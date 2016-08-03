# letterboxd-fans
Ranks films on <a href = "http://letterboxd.com">Letterboxd</a> by percentage of fans out of total watched.

Being a fan of a film on Letterboxd means it is one of the four "Favorite Films" on a user's profile, as can be seen <a href = "http://letterboxd.com/alda/">here on my profile</a>.

Scrapes Letterboxd's first five pages of <a href = "http://letterboxd.com/films/popular/">most popular</a> and first five pages of <a href = "http://letterboxd.com/films/by/rating/">top rated</a> films, gathering all the URLs.
Then, scrapes each URL to find number of fans and number of people who watched each film.
Congregates all this information into an unsorted CSV file.

With the CSV file, I went into Excel and manually sorted the films by percent fans out of watched. That file can be viewed <a href = "https://docs.google.com/spreadsheets/d/1uAvvD6t5Kl_w8uZs47fj9abIOpcKBO4aQhLUbP19inU/edit?usp=sharing">here</a>. The list only includes films with a percent at least 1%.
I also sorted a list of directors by number of films on the list.

I used Selenium and PhantomJS to scrape the JavaScript-heavy pages of Letterboxd.
