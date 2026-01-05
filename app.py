import streamlit as st
import pickle
import pandas as pd
import requests

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="Movie Recommender System",
    layout="wide"
)

# TMDB API key from Streamlit Secrets
API_KEY = st.secrets["5134a9b9250f780f7aeaa30b9e52c78a"]

POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500/"
PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750?text=No+Image"


# -------------------- FUNCTIONS --------------------
def fetch_poster(movie_id):
    try:
        url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}"
            f"?api_key={API_KEY}&language=en-US"
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("poster_path"):
            return POSTER_BASE_URL + data["poster_path"]
        else:
            return PLACEHOLDER_POSTER
    except Exception:
        return PLACEHOLDER_POSTER


def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    movies_dict = pickle.load(open("movies.pkl", "rb"))
    movies_df = pd.DataFrame(movies_dict)
    similarity_matrix = pickle.load(open("similarity.pkl", "rb"))
    return movies_df, similarity_matrix


movies, similarity = load_data()


# -------------------- UI --------------------
st.title("🎬 Movie Recommender System")
st.write("Select a movie and get similar movie recommendations")

selected_movie_name = st.selectbox(
    "Choose a movie",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
