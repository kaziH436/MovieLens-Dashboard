from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "movie_ratings.csv"

st.set_page_config(
    page_title="MovieLens Dashboard",
    page_icon="🎥",
    layout="wide",
)


@st.cache_data
def load_ratings() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["rating", "movie_id", "title"])
    return df


@st.cache_data
def explode_genres(ratings: pd.DataFrame) -> pd.DataFrame:
    exploded = ratings.copy()
    exploded["genre"] = exploded["genres"].fillna("unknown").str.split("|")
    exploded = exploded.explode("genre")
    exploded["genre"] = exploded["genre"].str.strip()
    exploded = exploded[exploded["genre"].ne("")]
    return exploded


@st.cache_data
def unique_movies(ratings: pd.DataFrame) -> pd.DataFrame:
    return ratings.drop_duplicates(subset=["movie_id"]).copy()


def movie_has_selected_genre(genres: str, selected: list[str]) -> bool:
    tags = {g.strip() for g in str(genres).split("|")}
    return bool(tags.intersection(selected))


ratings = load_ratings()
ratings_by_genre = explode_genres(ratings)
movies = unique_movies(ratings)
movies_by_genre = explode_genres(movies)

all_genres = sorted(ratings_by_genre["genre"].dropna().unique().tolist())
year_min = int(ratings["year"].min())
year_max = int(ratings["year"].max())

st.title("MovieLens Ratings Dashboard")
st.caption(
    "GroupLens MovieLens 100K — 100,000 ratings of 1,682 movies by 943 users. "
    "Charts use movie **release year**, not the year a rating was submitted."
)

with st.sidebar:
    st.header("Filters")
    selected_genres = st.multiselect(
        "Genres",
        options=all_genres,
        default=all_genres,
        help="Movies with multiple genres count in each selected genre.",
    )
    year_range = st.slider(
        "Release year range (Q3)",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
    )
    min_ratings = st.slider(
        "Minimum ratings floor (Q4)",
        min_value=10,
        max_value=200,
        value=50,
        step=5,
        help="Try 50, then raise to 150 to see how the top 5 changes.",
    )
    st.caption("Compare floors: 50 vs 150 ratings.")

if not selected_genres:
    st.warning("Select at least one genre in the sidebar to see the charts.")
    st.stop()

genre_movies = movies_by_genre[movies_by_genre["genre"].isin(selected_genres)]
genre_ratings = ratings_by_genre[ratings_by_genre["genre"].isin(selected_genres)]
year_ratings = ratings[
    ratings["year"].notna()
    & (ratings["year"] >= year_range[0])
    & (ratings["year"] <= year_range[1])
]
movies_q4 = movies[
    movies["genres"].apply(lambda g: movie_has_selected_genre(g, selected_genres))
]
q4_ids = set(movies_q4["movie_id"])
q4_ratings = ratings[ratings["movie_id"].isin(q4_ids)]

st.subheader("Question 1 — Genre breakdown")
st.markdown("What's the distribution of genres among the movies that were rated?")

genre_counts = (
    genre_movies.groupby("genre", as_index=False)["movie_id"]
    .nunique()
    .rename(columns={"movie_id": "n_movies"})
    .sort_values("n_movies", ascending=False)
)
q1 = (
    alt.Chart(genre_counts)
    .mark_bar()
    .encode(
        x=alt.X("n_movies:Q", title="Rated movies"),
        y=alt.Y("genre:N", sort="-x", title="Genre"),
        tooltip=["genre", "n_movies"],
    )
    .properties(height=max(280, 18 * len(genre_counts)))
)
st.altair_chart(q1, width="stretch")
st.caption(
    "Counts unique movies, not rating events. A movie listed as Drama|Romance "
    "is counted once under Drama and once under Romance, so totals exceed 1,682."
)

st.subheader("Question 2 — Genre satisfaction")
st.markdown("Which genres have the highest average rating? Which have the lowest?")

genre_means = (
    genre_ratings.groupby("genre", as_index=False)
    .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
    .sort_values("mean_rating", ascending=False)
)
genre_means["mean_rating"] = genre_means["mean_rating"].round(3)
highest = genre_means.iloc[0]
lowest = genre_means.iloc[-1]
st.markdown(
    f"**Highest:** {highest['genre']} ({highest['mean_rating']:.3f}). "
    f"**Lowest:** {lowest['genre']} ({lowest['mean_rating']:.3f})."
)
q2 = (
    alt.Chart(genre_means)
    .mark_bar()
    .encode(
        x=alt.X("mean_rating:Q", title="Average rating", scale=alt.Scale(domain=[1, 5])),
        y=alt.Y("genre:N", sort="-x", title="Genre"),
        tooltip=["genre", "mean_rating", "n_ratings"],
    )
    .properties(height=max(280, 18 * len(genre_means)))
)
st.altair_chart(q2, width="stretch")

st.subheader("Question 3 — Ratings over time")
st.markdown("How has the mean rating changed across movie **release** years?")

yearly = (
    year_ratings.groupby("year", as_index=False)
    .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
)
yearly["year"] = yearly["year"].astype(int)
yearly["mean_rating"] = yearly["mean_rating"].round(3)
q3 = (
    alt.Chart(yearly)
    .mark_line(point=True)
    .encode(
        x=alt.X("year:Q", title="Movie release year"),
        y=alt.Y("mean_rating:Q", title="Mean rating", scale=alt.Scale(zero=False)),
        tooltip=["year", "mean_rating", "n_ratings"],
    )
    .properties(height=360)
)
st.altair_chart(q3, width="stretch")
st.caption(
    "X-axis is `year` (release), not `rating_year` (when someone rated it). "
    "Hover a point to see how many ratings sit under that year — early years are sparse."
)

st.subheader("Question 4 — Best movies, with a floor")
st.markdown(
    "What are the top 5 best-rated movies, once you only count movies with at least "
    f"**{min_ratings}** ratings?"
)

movie_stats = (
    q4_ratings.groupby(["movie_id", "title"], as_index=False)
    .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
)
eligible = movie_stats[movie_stats["n_ratings"] >= min_ratings].copy()
eligible = eligible.sort_values(
    ["mean_rating", "n_ratings"], ascending=[False, False]
).head(5)
eligible["mean_rating"] = eligible["mean_rating"].round(3)

if eligible.empty:
    st.info("No movies meet this ratings floor with the current genre filter.")
else:
    q4 = (
        alt.Chart(eligible)
        .mark_bar()
        .encode(
            x=alt.X("mean_rating:Q", title="Average rating", scale=alt.Scale(domain=[1, 5])),
            y=alt.Y("title:N", sort="-x", title="Movie"),
            tooltip=["title", "mean_rating", "n_ratings"],
        )
        .properties(height=240)
    )
    st.altair_chart(q4, width="stretch")
    st.dataframe(
        eligible[["title", "mean_rating", "n_ratings"]].rename(
            columns={
                "title": "Title",
                "mean_rating": "Avg rating",
                "n_ratings": "N ratings",
            }
        ),
        hide_index=True,
        width="stretch",
    )

compare_50 = movie_stats[movie_stats["n_ratings"] >= 50].nlargest(5, "mean_rating")
compare_150 = movie_stats[movie_stats["n_ratings"] >= 150].nlargest(5, "mean_rating")
titles_50 = set(compare_50["title"])
titles_150 = set(compare_150["title"])
dropped = sorted(titles_50 - titles_150)
kept = sorted(titles_50 & titles_150)
st.caption(
    f"At a floor of 50 vs 150 (same genre filter): {len(kept)} title(s) stay in the top 5"
    + (f" ({', '.join(kept)})" if kept else "")
    + ". "
    + (
        f"Drop off when the floor rises: {', '.join(dropped)}."
        if dropped
        else "The top 5 set does not change."
    )
)
