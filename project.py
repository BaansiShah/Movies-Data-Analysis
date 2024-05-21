#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import plotly.express as px
import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
from PIL import Image
avatar = Image.open('Avatar.jpeg')

st.title(" The Movie database project")


@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)

    # Obtain data
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df

col1, col2 = st.columns([2,1])

with col1:
    "#### - Whats the hype around the upcoming movie Avatar?"
    "#### - Do you have any good movie recommendations for me?"
    "#### - Will the popularity of a genre be dependent on the movie duration?"

    st.markdown(' We have used our movie database to generate insightful findings about and around movies to asnwer such questions, Lets dive right in')
with col2:
    st.image(avatar, caption='Avatar the way of water')


"### Let's look at all the tables we have to get a fair idea of the data we are dealing with"


sql_all_table_names = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
try:
    all_table_names = query_db(sql_all_table_names)["table_name"].tolist()
    table_name = st.selectbox("Choose a table", all_table_names)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if table_name:
    f"Display the table"

    sql_table = f"SELECT * FROM {table_name};"
    try:
        df = query_db(sql_table)
        st.dataframe(df.style.format({'popularity': '{:.2f}'}))
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )


"## Top 10 most popular movies filtered by Genre, Original Language and Status"

st.markdown("- **About the query** : We can find out the most popular movies for a particular genre and then filter further for language it was made in and its Release status")

sql_genre = "SELECT DISTINCT name FROM genre;"
sql_org_lang = "SELECT DISTINCT language_name FROM spoken_languages;"
sql_status = "SELECT DISTINCT movie_status FROM movies;"

try:
    genre_names = query_db(sql_genre)["name"].tolist()
    genre_name = st.selectbox("Pick a Genre", genre_names, key = "1", index = 17)
    org_lang_names = query_db(sql_org_lang)["language_name"].tolist()
    org_lang_name = st.selectbox("Pick a Language", org_lang_names, index = 43)
    sql_status_names = query_db(sql_status)["movie_status"].tolist()
    sql_status_name = st.selectbox("Pick a Status", sql_status_names)
except:
    st.write("Sorry! There is no data for your selection, please try other filters.")

if (genre_name or org_lang_name or sql_status_name):
    
    sql_top_movies = f"""select m.title, m.release_date, p.country_name, m.popularity 
    from movies m, production_countries p, genre g, spoken_languages s
    where m.genre_id = g.genre_id and m.production_id = p.production_id and m.original_language = s.spoken_id
    and g.name = '{genre_name}' and s.language_name = '{org_lang_name}'
    and m.movie_status = '{sql_status_name}' order by m.popularity desc limit 10;"""
    
    try:
        movie_info = query_db(sql_top_movies)
        st.write(movie_info.style.format({'m.popularity': '{:.2f}'}))
        st.markdown("- **Insight** : We learned that amongst the popular movies Avatar 4 (genre : Action, language: English) is already in production and set to release in the year 2026")
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
         )

"# Upcoming movies that are Trending based on Genre Selected"

st.markdown("- **About the query** : Based on genre selected we display the unreleased movies which are trending. Trending is decided by movies which have a higher trailer view count, comments and likes on the trailer than an average trailer in the trailer table.")

try:
    genre_names1 = query_db(sql_genre)["name"].tolist()
    genre_name1 = st.selectbox("Pick a Genre", genre_names1, key = "2", index = 17)

except:
    st.write("Sorry! There is no data for your selection, please try other filters.")

if (genre_name1):
    sql_upcoming_trending = f"""select m.title, m.release_date, max(t.views) num_views, max(t.likes) num_likes, max(t.comments) num_comments
                            from movies m, genre g, trailer t
                            where m.genre_id = g.genre_id
                            and m.movie_id = t.movie_id 
                            and m.movie_status in ('Post Production', 'In Production')
                            and g.name = '{genre_name1}' 
                            and (t.views, t.likes, t.comments) >
                            (select avg(views), avg(likes), avg(comments)
                             from movies m, genre g, trailer t
                             where m.genre_id = g.genre_id
                             and m.movie_id = t.movie_id and g.name = '{genre_name1}')
                             group by m.movie_id
                             order by ((max(t.views) + max(t.likes) + max(t.comments))/3) desc;"""
    try:
        movie_info = query_db(sql_upcoming_trending)
        st.write(movie_info.style.format({'m.popularity': '{:.2f}'}))
        st.markdown("- **Insight** : We see that John Wick 4 is trending right now. So we if we haven't already, we can go watch it's trailer and decide if we want to watch the movie.")
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
         )


"# Recommended movies based on Genre"

st.markdown("- **About the query** : Lets say you're the user on our app and have been posting reviews and making lists, this query will recommend movies based on the genre selected by you i.e the user and recommend the most popular movies that might be of interest to you for that genre.")

sql_user_names = "SELECT username FROM users;"

try:
    user_names = query_db(sql_user_names)["username"].tolist()
    user_name = st.selectbox("Select your Username", user_names)
    genre_names2 = query_db(sql_genre)["name"].tolist()
    genre_name2 = st.selectbox("Pick a Genre", genre_names2, key = "3", index = 17)

except:
    st.write("Sorry! There is no data for your selection, please try other filters.")

if (genre_name2 and user_name):
    
    sql_recommendation = f"""select m.title, m.movie_status, m.popularity, m.original_language, m.release_date
                            from movies m, reviews r, list l, genre g
                            where g.name='{genre_name2}'
                            and r.username!='{user_name}'
                            and l.created_by!='{user_name}'
                            and m.movie_id = r.movie_id
                            and l.movie_id=m.movie_id
                            and m.genre_id = g.genre_id
                            group by m.movie_id
                            order by m.popularity desc;"""
    try:
        movie_info = query_db(sql_recommendation)
        st.write(movie_info.style.format({'m.popularity': '{:.2f}'}))
        st.markdown("- **Insight** : We get to know about movies that we haven't watched but are liked by other users.")
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
         )

"# Find most active user based on review statistics"

st.markdown("- **About the query** : Lets say you want to see all the cinephiles who are very active posting reviews, using this query we will display the user who have been posting the most reviews for a particular genre")

try:
    genre_names3 = query_db(sql_genre)["name"].tolist()
    genre_name3 = st.selectbox("Pick a Genre", genre_names3, key = "4", index = 17)

except:
    st.write("Sorry! There is no data for your selection, please try other filters.")

if (genre_name3):
    sql_upcoming_trending = f"""select u.username, count(r.review_id) Num_Reviews, avg(length(r.review)) Avg_Review_Length 
                            from users u, reviews r, movies m, genre g
                            where g.name = '{genre_name3}'
                            and u.username = r.username
                            and m.movie_id = r.movie_id
                            and g.genre_id = m.genre_id
                            group by u.username
                            order by count(r.review_id) desc;"""
    try:
        movie_info = query_db(sql_upcoming_trending)
        st.write(movie_info.style.format({'avg(length(r.review))': '{:.2f}'}))
        st.markdown("- **Insight** : This might help us decide which lists and reviews are more credible.")
    except:
        st.write(
           "Sorry! Something went wrong with your query, please try again."
        )

"# Popularity of movies based on runtime in every genre"

st.markdown("- **About the query** : Let's say you want to know if a 3 hours long movie would really be worth your time? Using this query, based on the runtime selected by the user, we show which genres are more popular.")

runtime = st.radio("Select Length of the movie", ('Short (<40 min)', 'Regular (40-140 min)', 'Long (>140 min)'))


if (runtime):
    if runtime == 'Short (<40 min)':
        low = 0
        high = 40
    elif runtime == 'Regular (40-140 min)':
        low = 40
        high = 140
    else:
        low = 140
        high = 1000

    sql_runtime = f"""select g.name, avg(m.popularity) avg_popularity
                from genre g, movies m
                where g.genre_id = m.genre_id
                and m.runtime >= '{low}' and m.runtime < '{high}' group by g.name order by avg(m.popularity) desc;"""

    try:
        movie_info = query_db(sql_runtime)
        
        col1, col2 = st.columns([1,3])
        with col1:
            st.dataframe(movie_info.style.format({'avg_popularity': '{:.2f}'}))
        with col2:
            # NOTE: Plotly must be installed on the system for this code to work and import plotly.express as px 
            fig = px.bar(movie_info,x = "name",y = "avg_popularity")
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            st.markdown("- **Insight** : If we follow the trend og Mystery movies over the runtimes, we see that people don't want a mystery to be uncovered very quickly and neither do they have the patience to wait more than 2 hours for the revelation.")
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
         )
        

        
"# Is this country more open to culturally diverse movies?"

st.markdown("- **About the query** : Based on the country selected by the user, we display the popularity of movies with some language spoken in them other than the language it is made in.")

sql_country = "Select Distinct country_name from production_countries;"

try:
    country_names = query_db(sql_country)["country_name"].tolist()
    country_name = st.selectbox("Pick a Country", country_names, key = 1)

except:
    st.write("Sorry! There is no data for your selection, please try other filters.")


if (country_name):
    
    sql_diversity_stats = f"""select m.title, m.original_language, s.language_name spoken_language, g.name genre, m.popularity
                        from movies m, spoken_languages s, genre g, production_countries p
                        where m.genre_id = g.genre_id
                        and m.spoken_id = s.spoken_id                                                                           
                        and m.production_id = p.production_id
                        and p.country_name = '{country_name}'
                        and m.original_language != m.spoken_id
                        order by m.popularity desc;"""

    try:
        movie_info = query_db(sql_diversity_stats)
        st.dataframe(movie_info.style.format({'m.popularity': '{:.2f}'}))
        st.markdown("- **Insight** : We find out if the country makes culturaly diverse movies and also show their popularity.")
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
         )



"# Movie Release Trend of Various Genres in a specific time frame for a particular country for the year 2022"  

st.markdown("- **About the query** : Based on the country and the time frame selected by the user, we display the number of movies released for different genres for the months that fall into that time frame.")

mon_dict = {'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4, 'May' : 5, 'Jun' : 6, 'Jul' : 7, 'Aug' : 8, 'Sep' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12}


#try:
country_names1 = query_db(sql_country)["country_name"].tolist()
country_name1 = st.selectbox("Pick a Country", country_names1, key = 2)

first_mon, last_mon = st.select_slider(
'Select a range of Month',
options=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
value=('Jan', 'Apr'))

low = mon_dict[first_mon]
high = mon_dict[last_mon]

# except:
#     st.write("Sorry! There is no data for your selection, please try other filters.")

if (country_name1 and first_mon and last_mon):
    
    sql_release_trend = f"""select to_char(release_date, 'Mon') as Month, g.name, count(m.movie_id) Num_of_movies_released
                                from movies m, genre g, production_countries p
                                where m.genre_id = g.genre_id
                                and m.production_id = p.production_id
                                and p.country_name = '{country_name1}'
                                and extract(year from release_date) = 2022
                                and m.movie_status = 'Released'
                                and extract(month from release_date) >= '{low}' and extract(month from release_date) <= '{high}'
                                group by to_char(release_date, 'Mon'), g.name
                                order by to_char(release_date, 'Mon') asc, count(m.movie_id) desc;"""

    #try:
    movie_info = query_db(sql_release_trend)
    st.dataframe(movie_info)
    st.markdown("- **Insight** : We see that the highest number of movies released in October are horror. this could be because of Halloween right around the corner.")
#     except:
#         st.write("Sorry! There is no data for your selection, please try other filters.")
        
        

"# Movies that weren't hyped as much but surprisingly gained traction later"

st.markdown("- **About the query** : Based on user's selected genre we display the movies whose trailers weren't highly viewed but users still wrote many reviews about it.")

try:
    genre_names4 = query_db(sql_genre)["name"].tolist()
    genre_name4 = st.selectbox("Pick a Genre", genre_names4, key = "5")

except:
    st.write("Sorry! There is no data for your selection, please try other filters.")


if (genre_name4):
    
    sql_hype_sustained = f"""select tt1.title, tt1.num_reviews ,tt2.views2 trailer_view_count
                        from 
                        (select count(r.review) num_reviews, m.title,m.movie_id
                        from movies m, reviews r,genre g
                        where m.movie_id = r.movie_id
                        and 
                        g.genre_id = m.genre_id
                        and g.name = '{genre_name4}'
                        group by m.movie_id
                        having  count(r.review)>(select
                         avg(num_reviews) from (select r2.movie_id,count(r2.review_id) 
                        num_reviews from reviews r2 group by r2.movie_id order by count(r2.review_id)) as temp1)) as tt1,
                        (select t1.movie_id ,max(t1.views) as views2
                        from trailer t1
                        group by t1.movie_id
                        having  avg(t1.views)<(
                         select avg(view_count) from (select t2.movie_id,avg(t2.views) 
                        view_count from trailer t2 group by t2.movie_id) as temp2)) as tt2
                        where tt1.movie_id = tt2.movie_id order by tt1.num_reviews desc;"""
        
        

    movie_info = query_db(sql_hype_sustained)
    st.dataframe(movie_info)
    st.markdown("- **Insight** : We see for Horror movies the trailer is not viewed many times but the movie has many reviews.")

