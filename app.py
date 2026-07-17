import streamlit as st
import pickle as pkl
import pandas as pd
import requests
import os
import gdown

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="CineMatch | Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top left, #1f1147 0%, #0d0d1a 45%, #000000 100%);
        color: #f5f5f7;
    }

    /* Hide default streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}

    /* Hero title */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #ff4e9c, #7f5af0, #2cb6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-top: 10px;
    }
    .hero-subtitle {
        text-align: center;
        color: #b8b8c8;
        font-size: 1.05rem;
        margin-top: 0px;
        margin-bottom: 30px;
    }

    div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.07) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #fff !important;
    }

    /* Recommend button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #ff4e9c, #7f5af0);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.2rem;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.5px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 18px rgba(127, 90, 240, 0.45);
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 8px 26px rgba(255, 78, 156, 0.5);
    }

    /* Section header */
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 22px;
        color: #fff;
        border-left: 5px solid #ff4e9c;
        padding-left: 14px;
    }

    /* Movie card */
    .movie-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 10px;
        text-align: center;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        height: 100%;
    }
    .movie-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(127, 90, 240, 0.35);
        border-color: rgba(255, 78, 156, 0.5);
    }
    .movie-card img {
        border-radius: 10px;
        width: 100%;
        margin-bottom: 10px;
    }
    .movie-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #f0f0f5;
        line-height: 1.3;
        min-height: 45px;
    }

    /* Footer */
    .footer-note {
        text-align: center;
        color: #6b6b7b;
        font-size: 0.85rem;
        margin-top: 50px;
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_resource
def load_data():
    # Download similarity matrix if missing
    if not os.path.exists("similarity.pkl"):
        sim_id = "1RmaypuYOnky6DSHP4Cr8XJ-6IAy7L3l2"
        gdown.download(f"https://drive.google.com/uc?id={sim_id}", "similarity.pkl", quiet=False, fuzzy=True)

    # Download movie dict if missing
    if not os.path.exists("movie_dict.pkl"):
        dict_id = "1v1bheC3lnWuuU25rdk6vX5w8Yz5hj3B-"
        gdown.download(f"https://drive.google.com/uc?id={dict_id}", "movie_dict.pkl", quiet=False, fuzzy=True)

    with open("movie_dict.pkl", "rb") as f:
        movies_dict = pkl.load(f)
    movies_df = pd.DataFrame(movies_dict)

    with open("similarity.pkl", "rb") as f:
        similarity_matrix = pkl.load(f)

    return movies_df, similarity_matrix

movies, similarity = load_data()

PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750/1a1a2e/ffffff?text=No+Poster"

# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    """Fetch a poster URL from TMDB for a given movie_id. Falls back gracefully."""
    try:
        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
        response = requests.get(url, timeout=6)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        return PLACEHOLDER_POSTER
    except Exception:
        return PLACEHOLDER_POSTER


def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        row = movies.iloc[i[0]]
        # Use the real TMDB movie_id column (not the dataframe row index)
        tmdb_id = row["movie_id"] if "movie_id" in movies.columns else row["id"]
        recommended_movies.append(row["title"])
        recommended_posters.append(fetch_poster(tmdb_id))

    return recommended_movies, recommended_posters


# ----------------------------------------------------------------------------
# UI — HERO
# ----------------------------------------------------------------------------
st.markdown('<div class="hero-title">🎬 CineMatch</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Discover your next favorite movie, powered by AI recommendations</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# UI — SEARCH CARD
# ----------------------------------------------------------------------------
option = st.selectbox("What would you like to watch?", movies["title"].values)
recommend_clicked = st.button("✨ Recommend Movies")

# ----------------------------------------------------------------------------
# UI — RESULTS
# ----------------------------------------------------------------------------
if recommend_clicked:
    with st.spinner("Finding movies you'll love..."):
        names, posters = recommend(option)

    st.markdown(f'<div class="section-header">Because you liked "{option}"</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.markdown(
                f"""
                <div class="movie-card">
                    <img src="{poster}" alt="{name}">
                    <div class="movie-title">{name}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown('<div class="footer-note">Built with Streamlit · Poster data via TMDB</div>', unsafe_allow_html=True)