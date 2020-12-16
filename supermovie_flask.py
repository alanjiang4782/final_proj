from flask import Flask, render_template, request
import sqlite3 
import plotly.graph_objs as go
import re

def convert_month(date):
    '''Convert the input date into the format of yyyy/mm/dd
    
    Parameters
    ----------
    date: string
        date in the format of <dd> <month in text> <yyyy>
    
    Returns
    -------
    date_int: string
        input date converted to the format of yyyy/mm/dd
    '''
    date_int = '0000/00/00'
    if date != None and date != '-':
        first_seg = re.search('\s{1}\d{4}$',date).group().strip()
        second_seg = re.search('[a-zA-Z]+',date).group().strip()
        if second_seg == 'January':
            second_seg = '01'
        if second_seg == 'February':
            second_seg = '02'
        if second_seg == 'March':
            second_seg = '03'
        if second_seg == 'April':
            second_seg = '04'
        if second_seg == 'May':
            second_seg = '05'
        if second_seg == 'June':
            second_seg = '06'
        if second_seg == 'July':
            second_seg = '07'
        if second_seg == 'August':
            second_seg = '08'
        if second_seg == 'September':
            second_seg = '09'
        if second_seg == 'October':
            second_seg = '10'
        if second_seg == 'November':
            second_seg = '11'
        if second_seg == 'December':
            second_seg = '12' 
        third_seg = re.search('^\d+\s{1}',date).group().strip()
        date_int = first_seg+'/'+second_seg+'/'+third_seg
    return date_int

app = Flask(__name__)

@app.route('/')
def home():
    '''Home page of the flask app
    
    Parameters
    ----------
    none
    
    Returns
    -------
    none
    '''
    name = 'supermovie'
    return render_template('home.html',name=name)

@app.route('/movie_list', methods=['POST'])
def movies():
    '''the movie list page of the flask app
    
    Parameters
    ----------
    none
    
    Returns
    -------
    none
    '''
    conn = sqlite3.connect('super_movie.sqlite')
    cur = conn.cursor()
    get_movie_by_date = '''
        SELECT name, classification, releasing_date FROM movies
    '''
    get_movie_by_score = '''
        SELECT name, classification, score FROM movies ORDER BY score DESC
    '''
    sort = request.form['sort']
    classification = request.form['classification']
    if sort == 'date':
        pre_result = cur.execute(get_movie_by_date).fetchall()
        conn.close()
        result = []
        if classification == 'All':
            result = pre_result
        else:
            for movie in pre_result:
                if movie[1] == classification:
                    result.append(movie)
    elif sort == 'score':
        pre_result = cur.execute(get_movie_by_score).fetchall()
        conn.close()
        result = []
        if classification == 'All':
            result = pre_result
        else:
            for movie in pre_result:
                if movie[1] == classification:
                    result.append(movie)

    return render_template('movie_lists.html', sort=sort, result=result)

@app.route('/movie_info', methods=['POST'])
def movie_info():
    '''the detailed information of a single movie of the flask app
    
    Parameters
    ----------
    none
    
    Returns
    -------
    none
    '''
    name = request.form['name'].strip()
    conn = sqlite3.connect('super_movie.sqlite')
    cur = conn.cursor()
    get_movie_info = '''
        SELECT * FROM movies
    '''
    movies = cur.execute(get_movie_info).fetchall()
    for movie in movies:
        if movie[1] == name:
            result = movie
    conn.close()

    return render_template('movie_info.html', result=result)

@app.route('/cast_info', methods=['POST'])
def cast_info():
    '''the detailed information of a single cast of the flask app
    
    Parameters
    ----------
    none
    
    Returns
    -------
    none
    '''
    name = request.form['name'].strip()
    conn = sqlite3.connect('super_movie.sqlite')
    cur = conn.cursor()
    get_cast_info = '''
        SELECT * FROM casts
    '''
    casts = cur.execute(get_cast_info).fetchall()
    result = None
    for cast in casts:
        if cast[1] == name:
            result = cast
    conn.close()
    score_dict = {}
    score_dict[convert_month(result[6])] = result[5]
    score_dict[convert_month(result[9])] = result[8]
    score_dict[convert_month(result[12])] = result[11]
    score_dict[convert_month(result[15])] = result[14]
    x_vals = []
    if convert_month(result[6]) != '00000000':
        x_vals.append(convert_month(result[6]))
    if convert_month(result[9]) != '00000000':
        x_vals.append(convert_month(result[9]))
    if convert_month(result[12]) != '00000000':
        x_vals.append(convert_month(result[12]))
    if convert_month(result[15]) != '00000000':
        x_vals.append(convert_month(result[15]))
    x_vals.sort()
    print (x_vals)
    y_vals = []
    for x in x_vals:
        if (x == '0000/00/00'):
            y_vals.append(0)
        else:
            y_vals.append(score_dict[x])
    bars_data = go.Scatter(
        x=x_vals,
        y=y_vals
    )
    fig = go.Figure(data=bars_data)
    div = fig.to_html(full_html=False)
    return render_template('cast_info.html', result=result, plot_div = div)

if __name__ == '__main__':
    print ('starting Flask app', app.name)
    app.run(debug=True)

