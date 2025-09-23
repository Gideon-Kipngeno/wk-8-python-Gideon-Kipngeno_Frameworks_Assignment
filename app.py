"""
CORD-19 Data Explorer - Streamlit Application
A simple web app for exploring COVID-19 research papers
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_analysis import CORD19Analyzer
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import re
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="CORD-19 Data Explorer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 48px;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 32px;
    }
    .section-header {
        font-size: 32px;
        color: #2e86ab;
        margin-top: 32px;
        margin-bottom: 16px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 16px;
        border-radius: 10px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">CORD-19 Research Data Explorer</h1>', 
                unsafe_allow_html=True)
    
    st.write("""
    This application provides an interactive exploration of the CORD-19 dataset, 
    which contains metadata about COVID-19 research papers. Analyze publication trends, 
    journal distributions, and research topics through interactive visualizations.
    """)
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = CORD19Analyzer('metadata.csv')
    
    # Sidebar
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose a section",
        ["Data Overview", "Publication Trends", "Journal Analysis", 
         "Content Analysis", "Source Analysis", "Interactive Explorer"]
    )
    
    # Load data
    if st.sidebar.button("Load Data") or 'data_loaded' in st.session_state:
        with st.spinner("Loading data..."):
            if st.session_state.analyzer.load_data():
                st.session_state.analyzer.clean_data()
                st.session_state.data_loaded = True
                st.sidebar.success("Data loaded successfully!")
            else:
                st.sidebar.error("Error loading data. Please check if metadata.csv exists.")
    
    if 'data_loaded' not in st.session_state:
        st.info("Please click 'Load Data' in the sidebar to begin analysis")
        return
    
    # Get cleaned data
    df_cleaned = st.session_state.analyzer.df_cleaned
    analyzer = st.session_state.analyzer
    
    # Data Overview Section
    if app_mode == "Data Overview":
        st.markdown('<h2 class="section-header">Dataset Overview</h2>', 
                    unsafe_allow_html=True)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        summary = analyzer.get_summary_statistics()
        
        with col1:
            st.metric("Total Papers", f"{summary['total_papers']:,}")
        with col2:
            st.metric("Papers with Abstracts", f"{summary['papers_with_abstract']:,}")
        with col3:
            st.metric("Unique Journals", f"{summary['unique_journals']:,}")
        with col4:
            st.metric("Publication Range", f"{summary['earliest_publication']}-{summary['latest_publication']}")
        
        # Data preview
        st.subheader("Data Preview")
        st.dataframe(df_cleaned.head(10))
        
        # Missing values analysis
        st.subheader("Missing Values Analysis")
        missing_data = df_cleaned.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        
        if len(missing_data) > 0:
            fig_missing = px.bar(
                x=missing_data.index, 
                y=missing_data.values,
                title="Missing Values by Column",
                labels={'x': 'Column', 'y': 'Missing Count'}
            )
            st.plotly_chart(fig_missing, use_container_width=True)
        else:
            st.success("No missing values in the cleaned dataset!")
    
    # Publication Trends Section
    elif app_mode == "Publication Trends":
        st.markdown('<h2 class="section-header">Publication Trends</h2>', 
                    unsafe_allow_html=True)
        
        # Year range selector
        min_year = int(df_cleaned['publication_year'].min())
        max_year = int(df_cleaned['publication_year'].max())
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Filters")
            year_range = st.slider(
                "Select Year Range",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year)
            )
            
            chart_type = st.selectbox(
                "Chart Type",
                ["Bar Chart", "Line Chart", "Area Chart"]
            )
        
        with col2:
            # Filter data by year range
            filtered_data = df_cleaned[
                (df_cleaned['publication_year'] >= year_range[0]) & 
                (df_cleaned['publication_year'] <= year_range[1])
            ]
            
            yearly_counts = filtered_data['publication_year'].value_counts().sort_index()
            
            if chart_type == "Bar Chart":
                fig = px.bar(
                    x=yearly_counts.index, 
                    y=yearly_counts.values,
                    title=f"Publications by Year ({year_range[0]}-{year_range[1]})",
                    labels={'x': 'Year', 'y': 'Number of Publications'}
                )
            elif chart_type == "Line Chart":
                fig = px.line(
                    x=yearly_counts.index, 
                    y=yearly_counts.values,
                    title=f"Publications by Year ({year_range[0]}-{year_range[1]})",
                    labels={'x': 'Year', 'y': 'Number of Publications'}
                )
            else:  # Area Chart
                fig = px.area(
                    x=yearly_counts.index, 
                    y=yearly_counts.values,
                    title=f"Publications by Year ({year_range[0]}-{year_range[1]})",
                    labels={'x': 'Year', 'y': 'Number of Publications'}
                )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Journal Analysis Section
    elif app_mode == "Journal Analysis":
        st.markdown('<h2 class="section-header">Journal Analysis</h2>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Settings")
            top_n = st.slider("Number of Top Journals to Show", 5, 25, 15)
            min_papers = st.slider("Minimum Papers per Journal", 1, 100, 10)
        
        with col2:
            # Get journal counts
            journal_counts = df_cleaned['journal_clean'].value_counts()
            journal_counts = journal_counts[journal_counts >= min_papers].head(top_n)
            
            fig = px.bar(
                x=journal_counts.values,
                y=journal_counts.index,
                orientation='h',
                title=f"Top {len(journal_counts)} Journals by Publication Count",
                labels={'x': 'Number of Publications', 'y': 'Journal'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Content Analysis Section
    elif app_mode == "Content Analysis":
        st.markdown('<h2 class="section-header">Content Analysis</h2>', 
                    unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Word Cloud", "Word Frequency", "Abstract Analysis"])
        
        with tab1:
            st.subheader("Word Cloud of Paper Titles")
            
            # Generate word cloud
            titles = ' '.join(df_cleaned['title'].dropna().astype(str))
            titles_clean = re.sub(r'[^\w\s]', '', titles.lower())
            
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(titles_clean)
            
            # Display word cloud
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        
        with tab2:
            st.subheader("Word Frequency Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                analysis_type = st.selectbox(
                    "Analyze",
                    ["Titles", "Abstracts"]
                )
                
                top_words = st.slider("Number of Top Words", 10, 50, 20)
                
                stop_words = st.text_area(
                    "Additional Stop Words (comma-separated)",
                    "covid, coronavirus, sars, cov, pandemic"
                )
            
            with col2:
                # Prepare text
                if analysis_type == "Titles":
                    text = ' '.join(df_cleaned['title'].dropna().astype(str))
                else:
                    text = ' '.join(df_cleaned['abstract'].dropna().astype(str))
                
                # Clean and count words
                words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                
                # Standard stop words
                standard_stop_words = {'the', 'and', 'of', 'in', 'to', 'a', 'for', 'with', 'on', 'by', 
                                     'as', 'an', 'from', 'that', 'this', 'is', 'are', 'was', 'were', 
                                     'be', 'been', 'have', 'has', 'had', 'but', 'not', 'at', 'which'}
                
                # Additional stop words from user
                additional_stop_words = set([word.strip().lower() for word in stop_words.split(',')])
                all_stop_words = standard_stop_words.union(additional_stop_words)
                
                filtered_words = [word for word in words if word not in all_stop_words]
                word_freq = Counter(filtered_words)
                top_words_list = word_freq.most_common(top_words)
                
                # Create visualization
                words, counts = zip(*top_words_list)
                
                fig = px.bar(
                    x=counts,
                    y=words,
                    orientation='h',
                    title=f"Top {top_words} Words in {analysis_type}",
                    labels={'x': 'Frequency', 'y': 'Word'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Abstract Length Analysis")
            
            # Abstract length distribution
            fig = px.histogram(
                df_cleaned[df_cleaned['abstract_word_count'] > 0],
                x='abstract_word_count',
                nbins=50,
                title="Distribution of Abstract Lengths",
                labels={'abstract_word_count': 'Word Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            abstract_stats = df_cleaned['abstract_word_count'].describe()
            
            with col1:
                st.metric("Mean Length", f"{abstract_stats['mean']:.1f} words")
            with col2:
                st.metric("Median Length", f"{abstract_stats['50%']:.1f} words")
            with col3:
                st.metric("Max Length", f"{abstract_stats['max']:.0f} words")
    
    # Source Analysis Section
    elif app_mode == "Source Analysis":
        st.markdown('<h2 class="section-header">Source Analysis</h2>', 
                    unsafe_allow_html=True)
        
        if 'source_x' in df_cleaned.columns:
            source_counts = df_cleaned['source_x'].value_counts().head(10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                fig_pie = px.pie(
                    values=source_counts.values,
                    names=source_counts.index,
                    title="Paper Distribution by Source"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart
                fig_bar = px.bar(
                    x=source_counts.values,
                    y=source_counts.index,
                    orientation='h',
                    title="Top Sources by Paper Count",
                    labels={'x': 'Number of Papers', 'y': 'Source'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Source information not available in this dataset.")
    
    # Interactive Explorer Section
    elif app_mode == "Interactive Explorer":
        st.markdown('<h2 class="section-header">Interactive Data Explorer</h2>', 
                    unsafe_allow_html=True)
        
        st.subheader("Filter and Explore Papers")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            year_filter = st.multiselect(
                "Filter by Year",
                options=sorted(df_cleaned['publication_year'].unique()),
                default=[]
            )
        
        with col2:
            # Journal filter (top journals only for performance)
            top_journals = df_cleaned['journal_clean'].value_counts().head(20).index.tolist()
            journal_filter = st.multiselect(
                "Filter by Journal",
                options=top_journals,
                default=[]
            )
        
        with col3:
            keyword_filter = st.text_input("Search in Titles/Abstracts")
        
        # Apply filters
        filtered_df = df_cleaned.copy()
        
        if year_filter:
            filtered_df = filtered_df[filtered_df['publication_year'].isin(year_filter)]
        
        if journal_filter:
            filtered_df = filtered_df[filtered_df['journal_clean'].isin(journal_filter)]
        
        if keyword_filter:
            mask = (
                filtered_df['title'].str.contains(keyword_filter, case=False, na=False) |
                filtered_df['abstract'].str.contains(keyword_filter, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Display results
        st.write(f"Found {len(filtered_df)} papers matching your criteria")
        
        if len(filtered_df) > 0:
            # Show sample of results
            display_columns = ['title', 'journal_clean', 'publication_year', 'abstract_word_count']
            st.dataframe(
                filtered_df[display_columns].head(100),
                use_container_width=True
            )
            
            # Download option
            csv = filtered_df[display_columns].to_csv(index=False)
            st.download_button(
                label="Download Filtered Results as CSV",
                data=csv,
                file_name="cord19_filtered_results.csv",
                mime="text/csv"
            )
        else:
            st.info("No papers match your current filters. Try adjusting your criteria.")

if __name__ == "__main__":
    main()