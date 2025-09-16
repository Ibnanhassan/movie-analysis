import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

st.title("MovieLens Data Analysis!!")
st.subheader("Breakdown of Movie Genres by Number of Ratings: ")

# Load dataset
df = pd.read_csv("movie_ratings.csv")

# Explode genres into rows
df_exploded = df.assign(genre=df['genres'].str.split('|')).explode('genre')

# Count ratings per genre
genre_counts = df_exploded['genre'].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

# --- Dropdown with "Select All" ---
all_genres = sorted(genre_counts['genre'].unique().tolist())
options_with_all = ["Select All"] + all_genres

selected_genres = st.multiselect(
    "Select Genre(s)",
    options=options_with_all,
    default=[]
)

# Handle "Select All"
if "Select All" in selected_genres:
    selected_genres = all_genres

# Dropdown to choose Y-axis type
y_axis_choice = st.selectbox("Show data as:", ["Counts", "Percentages"])

# Apply button
if st.button("Apply", key="apply_q1"):
    if not selected_genres:
        st.warning("Please select at least one genre (or 'Select All').")
    else:
        # Filter data by selection
        filtered_counts = genre_counts[genre_counts['genre'].isin(selected_genres)].copy()

        if filtered_counts.empty:
            st.info("No data available for the selected genres.")
        else:
            # Decide whether to plot counts or percentages
            if y_axis_choice == "Percentages":
                total = filtered_counts["count"].sum()
                filtered_counts["percent"] = (filtered_counts["count"] / total * 100).round(2)
                y_col = "percent"
                y_label = "Percentage of Ratings (%)"
            else:
                y_col = "count"
                y_label = "Number of Ratings"

            # Plot
            fig = sns.catplot(
                data=filtered_counts,
                x="genre",
                y=y_col,   # 👈 now dynamic
                kind="bar",
                height=6,
                aspect=2,
                order=selected_genres
            )

            fig.set_axis_labels("Genre", y_label)
            fig.set_titles(f"Breakdown of Selected Genres by {y_label}")
            fig.set_xticklabels(rotation=45, ha="right")

            st.pyplot(fig)
            st.write("We can imply from the data that there is a strong correlation between the popularity of a genre and how many ratings it receives.") 

st.subheader("Highest Viewer Satisfaction (By Genres): ")

# Age/decade pickers
ages = ["<18", "18–24", "25–34", "35–44", "45–49", "50–55", "56–65", "66+"]
all_ages = ["Select All"] + ages
selected_age_groups = st.multiselect(
    "Select age group(s):",
    options=all_ages,
    default=[]
)

decades = ["1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s"]
all_decades = ["Select All"] + decades
selected_decades = st.multiselect(
    "Select decade(s):",
    options=all_decades,
    default=[]
)

# Apply button for Q2 (unique key)
if st.button("Apply", key="apply_q2"):
    # Resolve "Select All" choices into real lists
    selected_age_groups_eff = ages if "Select All" in selected_age_groups else selected_age_groups
    selected_decades_eff = decades if "Select All" in selected_decades else selected_decades

    # Guard: if both empty, prompt user
    if not selected_age_groups_eff and not selected_decades_eff:
        st.warning("Please select at least one age group and/or decade.")
    else:
        dfx = df_exploded.copy()

        age_bins   = [-1, 17, 24, 34, 44, 49, 55, 65, np.inf]
        age_labels = ["<18", "18–24", "25–34", "35–44", "45–49", "50–55", "56–65", "66+"]
        dfx["age_group"] = pd.cut(dfx["age"], bins=age_bins, labels=age_labels)

        if selected_age_groups_eff:
            dfx = dfx[dfx["age_group"].isin(selected_age_groups_eff)]

        if selected_decades_eff:
            decade_nums = [int(d[:-1]) for d in selected_decades_eff]
            dfx = dfx[dfx["decade"].isin(decade_nums)]

        if dfx.empty:
            st.info("No data after applying these filters. Try widening your selections.")
        else:
            gstats = (
                dfx.groupby("genre")
                   .agg(avg_rating=("rating", "mean"),
                        num_ratings=("rating", "count"))
                   .reset_index()
            )

            if gstats.empty:
                st.info("No genres available after filtering.")
            else:
                plot_df = gstats.sort_values("avg_rating", ascending=True)
                fig2 = sns.catplot(
                    data=plot_df,
                    x="avg_rating",
                    y="genre",
                    kind="bar",
                    height=5,
                    aspect=1.6,
                )
                fig2.set_axis_labels("Average Rating (1–5)", "Genre")
                fig2.set_titles("Highest Viewer Satisfaction by Genre (after filters)")
                st.pyplot(fig2)

st.subheader("Mean Rating Across Movie Release Years")

decades2 = ["1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s"]
all_decades2 = ["Select All"] + decades2

selected_decades2 = st.multiselect(
    "Select decade(s):",
    options=all_decades2,
    default=[],
    key="q3_decades",          # 👈 unique key to avoid collisions
)

# Convert labels -> numeric decades
if "Select All" in selected_decades2:
    decade_nums = [int(d[:-1]) for d in decades2]
else:
    decade_nums = [int(d[:-1]) for d in selected_decades2]

# Filter
df_q3 = df.copy()
if decade_nums:
    df_q3 = df_q3[df_q3["decade"].isin(decade_nums)]

# Aggregate
yearly_ratings = (
    df_q3.groupby("year")["rating"]
         .mean()
         .reset_index()
         .sort_values("year")
)

# Plot
if st.button("Apply", key="apply_q3"):
    if yearly_ratings.empty:
        st.info("No data available for the selected decades.")
    else:
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=yearly_ratings, x="year", y="rating", marker="o")
        plt.title("Average Movie Rating by Release Year")
        plt.xlabel("Release Year")
        plt.ylabel("Average Rating (1–5)")
        plt.ylim(1, 5)
        st.pyplot(plt)

st.subheader("Top 5 Best-Rated Movies")

movie_stats = (
    df.groupby("title")
      .agg(avg_rating=("rating", "mean"),
           num_ratings=("rating", "count"))
      .reset_index()
)

st.write("**At least 50 ratings:**")
top50 = (
    movie_stats[movie_stats["num_ratings"] >= 50]
    .sort_values(by="avg_rating", ascending=False)
    .head(5)
)
st.write(top50)

st.write("**At least 150 ratings:**")
top150 = (
    movie_stats[movie_stats["num_ratings"] >= 150]
    .sort_values(by="avg_rating", ascending=False)
    .head(5)
)
st.write(top150)
