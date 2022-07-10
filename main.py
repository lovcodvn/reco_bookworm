from typing import Any

import pandas as pd
from flask import Flask, render_template, request
from ast import literal_eval
from collections import OrderedDict

# Load Books and Recommended DataFrame
df = pd.read_csv("datasets/books_enriched_clean.csv", encoding='utf8')
most_pop = pd.read_csv("datasets/most_pop.csv")
df_recommend_by_user = pd.read_csv("datasets/recommend_by_user.csv", index_col="user_id",
                                   converters={"recommended_books": literal_eval})
df_recommend_by_book = pd.read_csv("datasets/recommend_by_book.csv", index_col="book_id",
                                   converters={"recommended_books": literal_eval})
rec_size = 50


def get_suggestions():
    return list(df["original_title"].str.capitalize())


def clean_str(my_string):
    return my_string.replace("[", "").replace("]", "").replace("'", "")


def escape_special_char(my_string):
    return my_string.replace("+", "\+").replace("^", "\^").replace("(", "\(").replace(")", "\)").replace("?", "\?") \
        .replace("[", "\[").replace("]", "\]").replace("*", "\*").replace("$", "\$")


def combine(lst1, lst2, lst3=False):
    """
    If 2 inputs given, return 3 lists
    1) Similar recommendation in both list
    2) recommendation based on input 1
    3) recommendation based on input 2

    Similar concept for 3 inputs
    """

    if lst3:
        similar = list(set(lst1) & set(lst2) & set(lst3))
        remain_count = (rec_size - len(similar)) // 3
        remain1 = [i for i in lst1 if i not in similar][:remain_count]
        remain2 = [i for i in lst2 if i not in similar][:remain_count]
        remain3 = [i for i in lst3 if i not in similar][:remain_count]
        return similar, remain1, remain2, remain3
    else:
        similar = list(set(lst1) & set(lst2))
        remain_count = (rec_size - len(similar)) // 2
        remain1 = [i for i in lst1 if i not in similar][:remain_count]
        remain2 = [i for i in lst2 if i not in similar][:remain_count]
        return similar, remain1, remain2


def get_recommended_list(lst):
    if not lst:
        return []
    df_rec = pd.DataFrame()
    for id in lst:
        df_rec = df_rec.append(df[df.book_id == id])
    rec_posters = list(df_rec["image_url"])
    rec_books = list(df_rec["original_title"])
    rec_vote = list(df_rec["average_rating"])
    rec_year = [int(i) for i in list(df_rec["original_publication_year"])]
    rec_books_org = rec_books

    return {rec_posters[i]: [rec_books[i], rec_books_org[i], rec_vote[i], rec_year[i]] for i in
            range(len(rec_posters))}


app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    suggestions = get_suggestions()
    return render_template('home.html', suggestions=suggestions)


@app.route("/recommend", methods=["POST"])
def recommend():
    # Get input from Web App FrontEnd
    
    title = escape_special_char(request.form['title'])
    user_id = request.form['user']
    genre = request.form['genre']
    book_lst = user_lst = genre_lst = combine_lst = pop_lst = []

    # If book chosen, display info on book
    ser = df[df["original_title"].str.contains(title, case=False)]
    release_date = int(ser["original_publication_year"].values[0])
    poster = ser["image_url"].values[0]
    vote_average = ser["average_rating"].values[0]
    vote_count = ser["ratings_count"].values[0]
    authors = clean_str(ser["authors"].values[0])
    overview = ser["description"].values[0]
    genres = clean_str(ser["genres"].values[0])

    # Recommended Items based on inputs
    if title != "" and user_id != "" and genre != "":
        # recommend based on title, user & genre
        book_id = df[df["original_title"].str.contains(title, case=False)].book_id.values[0]
        book_mask = df_recommend_by_book.loc[[book_id]].recommended_books.values[0]
        user_mask = df_recommend_by_user.loc[[int(user_id)]].recommended_books.values[0]
        genre_mask = list(most_pop[most_pop.genres.str.contains(genre)].book_id)[:rec_size]
        combine_lst, book_lst, user_lst, genre_lst = combine(book_mask, user_mask, genre_mask)

    elif title != "" and user_id != "":
        # recommend based on title & user
        book_id = df[df["original_title"].str.contains(title, case=False)].book_id.values[0]
        book_mask = df_recommend_by_book.loc[[book_id]].recommended_books.values[0]
        user_mask = df_recommend_by_user.loc[[int(user_id)]].recommended_books.values[0]
        combine_lst, book_lst, user_lst = combine(book_mask, user_mask)

    elif title != "" and genre != "":
        # recommend based on title & genre
        book_id = df[df["original_title"].str.contains(title, case=False)].book_id.values[0]
        book_mask = df_recommend_by_book.loc[[book_id]].recommended_books.values[0]
        genre_mask = list(most_pop[most_pop.genres.str.contains(genre)].book_id)[:rec_size]
        combine_lst, genre_lst, book_lst = combine(genre_mask, book_mask)

    elif user_id != "" and genre != "":
        # recommend based on user & genre
        user_mask = df_recommend_by_user.loc[[int(user_id)]].recommended_books.values[0]
        genre_mask = list(most_pop[most_pop.genres.str.contains(genre)].book_id)[:rec_size]
        combine_lst, genre_lst, user_lst = combine(genre_mask, user_mask)

    elif title != "":
        # recommend based on title
        book_id = df[df["original_title"].str.contains(title, case=False)].book_id.values[0]
        book_lst = df_recommend_by_book.loc[[book_id]].recommended_books.values[0]

    elif user_id != "":
        # recommend based on user
        user_lst = df_recommend_by_user.loc[[int(user_id)]].recommended_books.values[0]

    elif genre != "":
        # recommend based on genre
        genre_lst = list(most_pop[most_pop.genres.str.contains(genre)].head(rec_size).book_id)

    else:
        # recommend based on most popular
        pop_lst = list(most_pop.book_id)[:rec_size]

    book_cards = get_recommended_list(combine_lst)
    g_book_cards = get_recommended_list(genre_lst)
    b_book_cards = get_recommended_list(book_lst)
    u_book_cards = get_recommended_list(user_lst)
    p_book_cards = get_recommended_list(pop_lst)

    # passing all the data to the html file
    return render_template('recommend.html', title=title, vote_average=vote_average,
                           vote_count=vote_count, release_date=release_date, authors=authors, user_id=user_id,
                           poster=poster, book_cards=book_cards, overview=overview, genres=genres, genre=genre,
                           b_book_cards=b_book_cards, u_book_cards=u_book_cards, g_book_cards=g_book_cards,
                           p_book_cards=p_book_cards)


if __name__ == '__main__':
    app.run(debug=True)
