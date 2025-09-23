# Analysis.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# ===============================
# 1. DATA LOADING
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("metadata.csv", low_memory=False)

    # Convert publish_time to datetime safely
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")

    # Ensure publish_time is stored as string for Arrow compatibility
    df["publish_time_str"] = df["publish_time"].dt.strftime("%Y-%m-%d")

    # Add abstract word count
    df["abstract_word_count"] = df["abstract"].fillna("").apply(lambda x: len(str(x).split()))

    return df


df = load_data()

# ===============================
# Streamlit Layout
# ===============================
st.title("CORD-19 Data Explorer")
st.write("Simple exploration of COVID-19 research papers using the metadata.csv file.")

# Tabs for better organization
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Cleaning", "Analysis", "Visualizations", "Dataset"]
)

# ===============================
# Part 1: Data Loading & Exploration
# ===============================
with tab1:
    st.subheader("Dataset Overview")
    st.write("Preview of the dataset:")
    st.dataframe(df.head())

    st.write("**Shape (rows, cols):**", df.shape)
    st.write("**Data types:**")
    st.write(df.dtypes)

    st.write("**Missing values (top 10 columns):**")
    st.write(df.isnull().sum().sort_values(ascending=False).head(10))

    st.write("**Basic statistics (numerical columns):**")
    st.write(df.describe())


# ===============================
# Part 2: Data Cleaning
# ===============================
with tab2:
    st.subheader("Data Cleaning & Preparation")

    st.markdown(
        """
        - Missing values handled: abstracts filled with empty string, publish_time coerced to datetime.  
        - Added new column: `abstract_word_count`.  
        - Extracted publication year for time-based analysis.  
        """
    )

    df["year"] = df["publish_time"].dt.year
    st.write(df[["publish_time_str", "year", "abstract_word_count"]].head())


# ===============================
# Part 3: Data Analysis
# ===============================
with tab3:
    st.subheader("Basic Analysis")

    st.write("**Papers by Year**")
    st.write(df["year"].value_counts().sort_index())

    st.write("**Top Journals**")
    st.write(df["journal"].value_counts().head(10))

    st.write("**Most Frequent Words in Titles**")
    titles = " ".join(df["title"].dropna().astype(str).tolist()).lower().split()
    word_freq = pd.Series(titles).value_counts().head(10)
    st.write(word_freq)


# ===============================
# Part 4: Visualizations
# ===============================
with tab4:
    st.subheader("Visualizations")

    # Filter by year
    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    year_range = st.slider("Select year range:", min_year, max_year, (min_year, max_year))
    filtered_df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    # Publications over time
    st.write("**Publications Over Time**")
    pubs_per_year = filtered_df["year"].value_counts().sort_index()
    fig, ax = plt.subplots()
    pubs_per_year.plot(kind="line", marker="o", ax=ax)
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Publications")
    st.pyplot(fig)

    # Top Journals
    st.write("**Top Journals**")
    top_journals = filtered_df["journal"].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_journals.values, y=top_journals.index, ax=ax, palette="viridis")
    ax.set_xlabel("Count")
    st.pyplot(fig)

    # Word Cloud
    st.write("**Word Cloud of Titles**")
    text = " ".join(filtered_df["title"].dropna().astype(str))
    if text.strip():
        wc = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("No titles available for the selected filter.")

    # Source Distribution
    st.write("**Paper Counts by Source**")
    top_sources = filtered_df["source_x"].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_sources.values, y=top_sources.index, ax=ax, palette="coolwarm")
    ax.set_xlabel("Count")
    st.pyplot(fig)

    # Abstract Word Count Distribution
    st.write("**Abstract Word Count Distribution**")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["abstract_word_count"], bins=50, ax=ax, kde=False)
    ax.set_xlabel("Word Count")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)


# ===============================
# Part 5: Dataset
# ===============================
with tab5:
    st.subheader("Dataset Sample")
    st.dataframe(filtered_df.head(50))
