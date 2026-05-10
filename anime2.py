
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
import gdown
import os

# =====================================
# CONFIG
# =====================================
st.set_page_config(
    page_title="Anime Dashboard",
    layout="wide"
)

st.title("🎌 Anime Analytics Dashboard")
st.markdown("Dashboard Analisis Anime 2023")

# =====================================
# LOAD DATA
# =====================================
# USERS DETAILS
if not os.path.exists("users-details-2023.csv"):

    url = "https://drive.google.com/uc?id=1XQ_m3aZ34ogv5CjOA3UFLPHJ9S_RtQvc"

    gdown.download(
        url,
        "users-details-2023.csv",
        quiet=False
    )

@st.cache_data
def load_data():
    df_anime = pd.read_csv('anime-dataset-2023-clean.csv')
    df_user = pd.read_csv('users-details-2023.csv')
    df_score = pd.read_csv('users-score-small.csv')
    return df_anime, df_user, df_score


df_anime, df_user, df_score = load_data()

# =====================================
# SIDEBAR
# =====================================
st.sidebar.title("Menu")
menu = st.sidebar.selectbox(
    "Pilih Halaman",
    [
        "Overview",
        "Anime Analysis",
        "User Analysis",
        "Recommendation System"
    ]
)

# =====================================
# OVERVIEW
# =====================================
if menu == "Overview":

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Jumlah Anime", len(df_anime))
    col2.metric("Jumlah User", len(df_user))
    col3.metric("Jumlah Rating", len(df_score))

    st.write("### Dataset Anime")
    st.dataframe(df_anime.head())

# =====================================
# ANIME ANALYSIS
# =====================================
elif menu == "Anime Analysis":

    st.subheader("Anime Analysis")

    # CLEANING SCORE
    scores = df_anime['Score'][df_anime['Score'] != 'UNKNOWN']
    scores = scores.astype('float')
    score_mean = round(scores.mean(), 2)

    df_anime['Score'] = df_anime['Score'].replace('UNKNOWN', score_mean)
    df_anime['Score'] = df_anime['Score'].astype('float64')

    # =====================================
    # TYPE DISTRIBUTION
    # =====================================
    st.write("## Distribusi Tipe Anime")

    type_counts = df_anime['Type'].value_counts()

    fig = px.bar(
        type_counts,
        x=type_counts.index,
        y=type_counts.values,
        color=type_counts.index,
        labels={
            'x': 'Anime Type',
            'y': 'Count'
        },
        title='Count of Anime Titles by Type'
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================
    # TOP POPULAR ANIME
    # =====================================
    st.write("## Top 15 Most Popular Anime")

    df_valid_popularity = df_anime[df_anime['Popularity'] > 0]

    top_10_popular = df_valid_popularity.sort_values(
        by='Popularity',
        ascending=True
    ).head(15)

    fig = px.bar(
        top_10_popular,
        x='Name',
        y='Popularity',
        color='Name',
        title='Top 15 Most Popular Animes'
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================
    # SCORE VS MEMBERS
    # =====================================
    st.write("## Score vs Members")

    fig = px.scatter(
        df_anime,
        x='Score',
        y='Members',
        color='Type',
        title='Anime Score vs Members'
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================
    # GENRE DISTRIBUTION
    # =====================================
    st.write("## Genre Distribution")

    genre_counts = df_anime[
        df_anime['Genres'] != 'UNKNOWN'
    ]['Genres'].apply(lambda x: x.split(', ')).explode().value_counts()

    top_20_genres = genre_counts.head(20)

    fig = px.bar(
        top_20_genres,
        x=top_20_genres.index,
        y=top_20_genres.values,
        color=top_20_genres.index,
        title='Top 20 Genres'
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================
    # WORDCLOUD
    # =====================================
    st.write("## Genre WordCloud")

    genre_text = ' '.join(
        df_anime[
            df_anime['Genres'] != 'UNKNOWN'
        ]['Genres'].dropna()
    )

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white'
    ).generate(genre_text)

    fig_wc, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud)
    ax.axis('off')

    st.pyplot(fig_wc)

# =====================================
# USER ANALYSIS
# =====================================
elif menu == "User Analysis":

    st.subheader("User Analysis")

    # =====================================
    # GENDER DISTRIBUTION
    # =====================================
    gender_counts = df_user['Gender'].value_counts(dropna=True)

    fig = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title='Gender Distribution'
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================
    # LOCATION ANALYSIS
    # =====================================
    st.write("## Top 20 User Locations")

    location_counts = df_user['Location'].value_counts().head(20)

    fig = px.bar(
        location_counts,
        x=location_counts.index,
        y=location_counts.values,
        color=location_counts.index
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================
    # AGE DISTRIBUTION
    # =====================================
    st.write("## Age Distribution")

    def calculate_age(birth_date):
        if birth_date != 'NaN':
            try:
                birth_year = int(birth_date.split('-')[0])
                today_year = datetime.utcnow().year
                age = today_year - birth_year
                if age >= 10 and age < 60:
                    return age
            except:
                return None
        return None

    Age = df_user['Birthday'].dropna().apply(calculate_age)

    fig = px.histogram(
        Age,
        nbins=20,
        title='Age Distribution'
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================
# RECOMMENDATION SYSTEM
# =====================================
elif menu == "Recommendation System":

    st.subheader("Anime Recommendation")

    anime_list = sorted(df_anime['Name'].dropna().unique())

    selected_anime = st.selectbox(
        "Pilih Anime",
        anime_list
    )

    st.write("Anime yang dipilih:")
    st.success(selected_anime)

    recommendations = df_anime[
        df_anime['Genres'] == df_anime[
            df_anime['Name'] == selected_anime
        ]['Genres'].values[0]
    ][['Name', 'Genres', 'Score']].head(10)

    st.write("## Rekomendasi Anime")
    st.dataframe(recommendations)
