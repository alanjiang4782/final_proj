#################################
##### Name: Shenghao Jiang ######
##### Uniqname: shhjiang   ###### 
#################################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import re

url = "https://www.imdb.com/calendar/?ref_=nv_mv_cal"
base_url = "https://www.imdb.com"

CACHE_URL_FILENAME = "movie_url.json"
CACHE_MOVIE_FILENAME = "movie.json"
CACHE_CAST_FILENAME = "cast.json"
CACHE_CAST_MOVIE_URL_FILENAME = 'cast_movie.json'

conn = sqlite3.connect("super_movie.sqlite")
cur = conn.cursor()

create_movies = '''
    CREATE TABLE "movies" (
        "Id"                    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "name"                  TEXT,
        "director"              TEXT,
        "star1"                 TEXT,
        "star2"                 TEXT,
        "star3"                 TEXT,
        "releasing_date"        TEXT,
        "score"                 TEXT,
        "classification"        TEXT,
        "description"           TEXT,
        "poster_url"            TEXT
    );
'''

drop_movies = '''
    DROP TABLE IF EXISTS "movies";
'''

insert_movies = '''
    INSERT INTO movies 
    ("name","director","star1","star2","star3","releasing_date","score","classification","description","poster_url")
    VALUES (?,?,?,?,?,?,?,?,?,?)
'''

drop_casts = '''
    DROP TABLE IF EXISTS "casts";
'''

create_casts = '''
    CREATE TABLE "casts" (
        "Id"                    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "name"                  TEXT,
        "position"              TEXT,
        "bio"                   TEXT,
        "film1"                 TEXT,
        "score1"                TEXT,
        "date1"                 TEXT,
        "film2"                 TEXT,
        "score2"                TEXT,
        "date2"                 TEXT,
        "film3"                 TEXT,
        "score3"                TEXT,
        "date3"                 TEXT,
        "film4"                 TEXT,
        "score4"                TEXT,
        "date4"                 TEXT,
        "photo"                 TEXT
    );
'''

insert_casts = '''
    INSERT INTO casts 
    ("name","position","bio","film1","score1","date1","film2","score2","date2","film3","score3","date3","film4","score4","date4","photo")
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)  
'''

class Movies:
    '''instance is a movie object

    Instance Attributes
    -------------------
    name: str
        name of the movie
    director: str
        name of the director
    director_url: str
        web link to the director's homepage
    stars: list
        a list of actors/actresses name
    stars_url_dict: dict
        in the format of {'actor_name': actor_homepage}
    releasing_date: str
        releasing date of the movie
    score: str
        score of the movie
    classification: str
        type of the movie, eg: action, drama, documentary etc.
    description: str
        story line of the movie
    '''
    def __init__(self, name, director, director_url, stars, stars_url_dict, releasing_date, score, classification, description, poster_url):
        self.name = name
        self.director = director
        self.director_url = director_url
        self.stars = stars
        self.stars_url_dict = stars_url_dict
        self.releasing_date = releasing_date
        self.score = score
        self.classification = classification
        self.description = description
        self.poster_url = poster_url


    def info(self):
        '''displays the information of the instance

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        print (self.name)
        print ('score:',self.score)
        print ('type:',self.classification)
        print ('director: '+ self.director)
        star_string = ''
        for star in self.stars:
            star_string += star+', '
        print ('stars: '+ star_string[0:-2])
        print ('storyline:')
        print (self.description)
        print ('\n')

class Cast:
    '''instance is a director or an actor/actress in the movie
    
    Instance Attributes
    -------------------
    position: str
        whether it is a director or an actor/actress
    name: str
        name of the cast (either director or one of the stars in this project)
    bio: str
        bio of the cast
    films: dict
        in the form of {'film_name': film_url}
    score: dict 
        in the form of {'film_name': score of the film}
    '''

    def __init__(self,position,name,bio,films,score,photo):
        self.position = position
        self.name = name
        self.bio = bio
        self.films = films
        self.score = score
        self.photo = photo

    def info (self):
        '''Displays the information of the instance

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        print (self.name)
        print (self.position)
        print (self.bio)
        print (self.films)
        print (self.score)
   

def build_movie_url_dict():
    ''' Make a dictionary that maps movie name to movie page url, properly cached

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a movie name and value is the movie url
        e.g. {'Nomadland':'https://www.imdb.com/title/tt9770150/?ref_=rlm', ...}
    '''
    movie_url_dict = open_cache(CACHE_URL_FILENAME)
    if bool(movie_url_dict) is True:
        # dict not empty, cache exists
        print ("Using cache")
        return movie_url_dict
    else:
        # dict empty, need to fetch
        print ("Fetching")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        main_block = soup.find('div', id='main')
        parent_list = main_block.find_all('ul')
        for item in parent_list:
            movie_list = item.find_all('li')
            for movie in movie_list:
                movie_name = movie.find('a').text
                movie_url = movie.find('a')['href']
                movie_url_dict[movie_name.lower()] = base_url + movie_url

        save_cache(movie_url_dict, CACHE_URL_FILENAME)
        return movie_url_dict
       

def get_movie_instance(movie_url):
    '''Make a 'Movies' instance from a movie URL.
    
    Parameters
    ----------
    movie_url: string
        The URL for a movie page
    
    Returns
    -------
    instance
        a movie instance
    '''
    movie_dict = open_cache(CACHE_MOVIE_FILENAME)
    if movie_url in movie_dict:
        print ("Using cache")
        name = movie_dict[movie_url]['name']
        director = movie_dict[movie_url]['director']
        director_url = movie_dict[movie_url]['director_url']
        stars = movie_dict[movie_url]['stars']
        stars_url_dict = movie_dict[movie_url]['stars_url_dict']
        releasing_date = movie_dict[movie_url]['releasing_date']
        score = movie_dict[movie_url]['score']
        classification = movie_dict[movie_url]['classification']
        description = movie_dict[movie_url]['description']
        poster_url = movie_dict[movie_url]['poster_url']

    else:
        print ("Fetching")
        response = requests.get(movie_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_wrapper = soup.find('div', class_='title_wrapper')
        if title_wrapper is None:
            name = None
            releasing_date = None
            classification = None
        else:
            name = title_wrapper.find('h1').text.strip()
            index = name.find('(')
            name = name[0:index-1]
            classification = title_wrapper.find('div', class_='subtext').find_all('a')[0].text.strip()
            releasing_date = title_wrapper.find('div', class_='subtext').find_all('a')[-1].text.strip()
            index = releasing_date.find('(')
            releasing_date = releasing_date[0:index-1]
        
        score_wrapper = soup.find('div', class_='ratingValue')
        if score_wrapper is None:
            score = 0
        else:
            score = score_wrapper.text.strip()[:-3]
        
        director_wrapper = soup.find_all('div', class_='credit_summary_item')[0].find('a')
        if director_wrapper is None:
            director = None
            director_url = None
        else:
            director = director_wrapper.text.strip()
            director_url = base_url + director_wrapper['href']
        if len(soup.find_all('div', class_='credit_summary_item')) == 3:
            stars_wrapper = soup.find_all('div', class_='credit_summary_item')[2].find_all('a')
        else:
            stars_wrapper = soup.find_all('div', class_='credit_summary_item')[1].find_all('a')
        if stars_wrapper is None:
            stars = None
            stars_url_dict = None
        else:
            stars = []
            stars_url_dict = {}
            for star in stars_wrapper[0:-1]:
                stars.append(star.text)
                stars_url_dict[star.text] = base_url + star['href']
        
        description_wrapper = soup.find('div', class_='inline canwrap').find('p').find('span')
        if description_wrapper is None:
            description = None
        else:
            description = description_wrapper.text.strip()
        
        poster_wrapper = soup.find('div', class_='poster')
        if poster_wrapper is None:
            poster_url = None
        else:
            poster_url = poster_wrapper.find('img')['src']
        
        
        movie_dict[movie_url] = {}
        movie_dict[movie_url]['name'] = name
        movie_dict[movie_url]['director'] = director
        movie_dict[movie_url]['director_url'] =  director_url
        movie_dict[movie_url]['stars'] = stars
        movie_dict[movie_url]['stars_url_dict'] = stars_url_dict
        movie_dict[movie_url]['releasing_date'] = releasing_date
        movie_dict[movie_url]['score'] = score
        movie_dict[movie_url]['classification'] = classification
        movie_dict[movie_url]['description'] = description
        movie_dict[movie_url]['poster_url'] = poster_url
        save_cache(movie_dict, CACHE_MOVIE_FILENAME)
        
    movie_instance = Movies(name, director, director_url, stars, stars_url_dict, releasing_date, score, classification, description, poster_url)

    return movie_instance
    
def get_cast_instance(position, cast_url):
    '''Make a 'Casts' instance from a cast URL.
    
    Parameters
    ----------
    position: string
        position of the person, director/star
    cast_url: string
        The URL for a director/star page
    
    Returns
    -------
    instance
        a cast instance
    '''
    cast_dict = open_cache(CACHE_CAST_FILENAME)
    if cast_url in cast_dict:
        print ("Using cache")
        name = cast_dict[cast_url]['name']
        bio = cast_dict[cast_url]['bio']
        films = cast_dict[cast_url]['films']
        photo = cast_dict[cast_url]['photo']

    else:
        print ("Fetching")
        response = requests.get(cast_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        name_bio_wrapper = soup.find('div', id='name-overview-widget', class_='name-overview-widget')
        if name_bio_wrapper is None:
            name_wrapper = soup.find('div', id='name-overview-widget')
            if name_wrapper is None:
                name = None
            else:
                name =  name_wrapper.find('table').find('tbody').find('h1', recursive=True).find('span').text.strip()
        else:
            name = name_bio_wrapper.find('table').find('tbody').find('tr').find('td').find('h1').find('span').text
        bio_wrapper = soup.find('div',class_='inline')
        if bio_wrapper is None:
            bio = None
        else:
            bio = bio_wrapper.text.strip()[0:-15]
        if name_bio_wrapper is None:
            photo = None
        else:
            photo_1 = name_bio_wrapper.find('div', class_='poster-hero-container')
            if photo_1 is None:
                photo = None
            else:
                photo_2 = photo_1.find('div',class_='image')
                if photo_2 is None:
                    photo = None
                else:
                    photo = photo_2.find('img')['src']

        film_wrapper = soup.find_all('div', class_ = 'knownfor-title-role')
        if film_wrapper is None:
            films = None
        else:
            films = {}
            for film in film_wrapper:
                key = film.find('a').text.strip()
                value = base_url + film.find('a')['href']
                films[key] = value
        cast_dict[cast_url] = {}
        cast_dict[cast_url]['name'] = name
        cast_dict[cast_url]['bio'] = bio
        cast_dict[cast_url]['films'] = films
        cast_dict[cast_url]['photo'] = photo
        save_cache(cast_dict, CACHE_CAST_FILENAME)
    
    score = {} 

        
    cast_instance = Cast(position, name, bio, films, score, photo)

    return cast_instance

def get_score_attribute(cast_instance):
    '''Get the score attribute of the cast_instance

    Parameters
    ----------
    cast_instance:
        a instance of the class 'Casts'

    Returns
    -------
    cast_instance:
        a instance of the class 'Casts', with the score attribute given

    '''
    movie_url_dict = open_cache(CACHE_CAST_MOVIE_URL_FILENAME)
    movie_url_input_dict = cast_instance.films
    scores = {}
    for movie_name in movie_url_input_dict.keys():
        if movie_url_input_dict[movie_name] in movie_url_dict:
            print ("Using cache")
            scores[movie_name] = movie_url_dict[movie_url_input_dict[movie_name]]
        else:
            print ("Fetching")
            response = requests.get(movie_url_input_dict[movie_name])
            soup = BeautifulSoup(response.text, 'html.parser')
            score_wrapper = soup.find('div', class_='ratingValue')
            if score_wrapper is None:
                score = 0
            else:
                score = score_wrapper.text.strip()[0:-3]
            title_wrapper = soup.find('div', class_='title_wrapper')
            if title_wrapper is None:
                releasing_date = None
            else:
                releasing_date = title_wrapper.find('div', class_='subtext').find_all('a')[-1].text.strip()
                index = releasing_date.find('(')
                releasing_date = releasing_date[0:index-1]
                
                if (re.fullmatch('\d{2}\s{1}[a-zA-Z]+\s{1}\d{4}',releasing_date)) is None:
                    releasing_date = None
   
            scores[movie_name] = []
            scores[movie_name] = [score,releasing_date]
            movie_url_dict[movie_url_input_dict[movie_name]] = []
            movie_url_dict[movie_url_input_dict[movie_name]] = [score,releasing_date]

    cast_instance.score = scores
    save_cache(movie_url_dict, CACHE_CAST_MOVIE_URL_FILENAME)

    return cast_instance

def open_cache(cache_filename):
    ''' Opens the cache file if it exists and loads the JSON into dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    cache_filename: string
        the json file name for the dictionary we are generating

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(cache_filename, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict, cache_filename):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    cache_filename: string
        The file the dictionary is going to save to
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(cache_filename,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def scrape_info ():
    '''This is the function that is used to scrape all the information needed for this project

    Parameters
    ----------
    None

    Returns
    -------
    movie_list: list
        a list of 'Movies' instance
    cast_list: list
        a list of 'Casts' instance
    '''
    movie_list = []
    cast_list = []
    movie_url_dict = build_movie_url_dict()
    for key in movie_url_dict.keys():
        movie_url = movie_url_dict[key]
        movie_instance = get_movie_instance(movie_url)
        movie_list.append(movie_instance)
        print (movie_instance.name)
        cast_director = get_cast_instance('director',movie_instance.director_url)
        cast_director = get_score_attribute(cast_director)
        cast_list.append(cast_director)
        stars_url = movie_instance.stars_url_dict
        for star_url in stars_url.values():
            cast_star = get_cast_instance('star',star_url)
            cast_star = get_score_attribute(cast_star)
            cast_list.append(cast_star)
        

    return movie_list, cast_list

def build_movies_table(movie_list):
    '''Accept a list of movie instance and generate the movies table in the super_movie.sqlite

    Parameters
    ----------
    movie_list: list
        a list of movie instances

    Returns
    -------
    None
    '''
    cur.execute(drop_movies)
    cur.execute(create_movies)
    for movie in movie_list:
        value_list = []
        value_list.append(movie.name)
        value_list.append(movie.director)
        num_of_stars = len(movie.stars)
        if num_of_stars == 0:
            for i in range(3):
                value_list.append('-')
        elif num_of_stars == 1:
            value_list.append(movie.stars[0])
            for i in range(2):
                value_list.append('-')
        elif num_of_stars == 2:
            for i in range (2):
                value_list.append(movie.stars[i])
            value_list.append('-')
        elif num_of_stars == 3:
            for i in range(3):
                value_list.append(movie.stars[i])
        value_list.append(movie.releasing_date)
        value_list.append(movie.score)
        value_list.append(movie.classification)
        value_list.append(movie.description)
        value_list.append(movie.poster_url)
        cur.execute(insert_movies, value_list)
    conn.commit()

def build_casts_table(cast_list):
    '''Accept a list of cast instance and generate the casts table in the super_movie.sqlite

    Parameters
    ----------
    cast_list: list
        a list of cast instances

    Returns
    -------
    None
    '''
    cur.execute(drop_casts)
    cur.execute(create_casts)
    for cast in cast_list:
        value_list = []
        value_list.append(cast.name)
        value_list.append(cast.position)
        value_list.append(cast.bio)

        num_of_films = len(cast.score.keys())
        key_list = cast.score.keys()
        for key in key_list:
            value_list.append(key)
            value_list.append(cast.score[key][0]) 
            value_list.append(cast.score[key][1]) 
        
        if num_of_films == 0:
            for i in range(12):
                value_list.append('-')
        elif num_of_films == 1:
            for i in range(9):
                value_list.append('-')
        elif num_of_films == 2:             
            for i in range (6):
                value_list.append('-')
        elif num_of_films == 3:
            for i in range(3):
                value_list.append('-')
        value_list.append(cast.photo)
        cur.execute(insert_casts, value_list)

    conn.commit()

if __name__ == "__main__":
    movie_list, cast_list = scrape_info()
    build_movies_table(movie_list)
    build_casts_table(cast_list)



