"""
CORD-19 Data Analysis Module
Performs data loading, cleaning, analysis and visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime
import re
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

class CORD19Analyzer:
    def __init__(self, file_path='metadata.csv'):
        """
        Initialize the analyzer with the dataset path
        """
        self.file_path = file_path
        self.df = None
        self.df_cleaned = None
        
    def load_data(self):
        """
        Load the metadata.csv file into a pandas DataFrame
        """
        try:
            self.df = pd.read_csv(self.file_path)
            print(f"Dataset loaded successfully: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return True
        except FileNotFoundError:
            print(f"Error: File {self.file_path} not found.")
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def basic_exploration(self):
        """
        Perform basic data exploration
        """
        if self.df is None:
            print("Please load data first using load_data()")
            return
        
        print("=== BASIC DATA EXPLORATION ===")
        print(f"Dataset shape: {self.df.shape}")
        print("\nFirst 5 rows:")
        print(self.df.head())
        
        print("\nData types:")
        print(self.df.dtypes)
        
        print("\nMissing values by column:")
        missing_data = self.df.isnull().sum()
        print(missing_data[missing_data > 0])
        
        print("\nBasic statistics for numerical columns:")
        print(self.df.describe())
    
    def clean_data(self):
        """
        Clean and prepare the data for analysis
        """
        if self.df is None:
            print("Please load data first using load_data()")
            return
        
        print("=== DATA CLEANING ===")
        self.df_cleaned = self.df.copy()
        
        # Handle publication date
        print("Processing publication dates...")
        self.df_cleaned['publish_time'] = pd.to_datetime(
            self.df_cleaned['publish_time'], errors='coerce'
        )
        
        # Extract year from publication date
        self.df_cleaned['publication_year'] = self.df_cleaned['publish_time'].dt.year
        
        # Fill missing years with 2020 (most common year for COVID research)
        self.df_cleaned['publication_year'] = self.df_cleaned['publication_year'].fillna(2020)
        
        # Create abstract word count
        self.df_cleaned['abstract_word_count'] = self.df_cleaned['abstract'].apply(
            lambda x: len(str(x).split()) if pd.notnull(x) else 0
        )
        
        # Create title word count
        self.df_cleaned['title_word_count'] = self.df_cleaned['title'].apply(
            lambda x: len(str(x).split()) if pd.notnull(x) else 0
        )
        
        # Clean journal names
        self.df_cleaned['journal_clean'] = self.df_cleaned['journal'].fillna('Unknown')
        self.df_cleaned['journal_clean'] = self.df_cleaned['journal_clean'].str.title()
        
        print(f"Data cleaning completed. Cleaned dataset shape: {self.df_cleaned.shape}")
        
        return self.df_cleaned
    
    def analyze_publications_over_time(self):
        """
        Analyze publication trends over time
        """
        if self.df_cleaned is None:
            print("Please clean data first using clean_data()")
            return
        
        # Publications by year
        yearly_counts = self.df_cleaned['publication_year'].value_counts().sort_index()
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        yearly_counts.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Number of COVID-19 Publications by Year', fontsize=16, fontweight='bold')
        ax.set_xlabel('Publication Year', fontsize=12)
        ax.set_ylabel('Number of Publications', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        
        return fig, yearly_counts
    
    def analyze_top_journals(self, top_n=15):
        """
        Analyze top journals publishing COVID-19 research
        """
        if self.df_cleaned is None:
            print("Please clean data first using clean_data()")
            return
        
        # Get top journals
        journal_counts = self.df_cleaned['journal_clean'].value_counts().head(top_n)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        journal_counts.plot(kind='barh', ax=ax, color='lightcoral')
        ax.set_title(f'Top {top_n} Journals Publishing COVID-19 Research', fontsize=16, fontweight='bold')
        ax.set_xlabel('Number of Publications', fontsize=12)
        ax.set_ylabel('Journal', fontsize=12)
        plt.tight_layout()
        
        return fig, journal_counts
    
    def create_title_wordcloud(self):
        """
        Create a word cloud from paper titles
        """
        if self.df_cleaned is None:
            print("Please clean data first using clean_data()")
            return
        
        # Combine all titles
        titles = ' '.join(self.df_cleaned['title'].dropna().astype(str))
        
        # Clean the text
        titles_clean = re.sub(r'[^\w\s]', '', titles.lower())
        
        # Create word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate(titles_clean)
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Most Frequent Words in Paper Titles', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def analyze_word_frequency(self, column='title', top_n=20):
        """
        Analyze word frequency in titles or abstracts
        """
        if self.df_cleaned is None:
            print("Please clean data first using clean_data()")
            return
        
        # Combine text from specified column
        text = ' '.join(self.df_cleaned[column].dropna().astype(str))
        
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'of', 'in', 'to', 'a', 'for', 'with', 'on', 'by', 
                     'as', 'an', 'from', 'that', 'this', 'is', 'are', 'was', 'were', 
                     'be', 'been', 'have', 'has', 'had', 'but', 'not', 'at', 'which'}
        
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        top_words = word_freq.most_common(top_n)
        
        # Create visualization
        words, counts = zip(*top_words)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.barh(words, counts, color='lightgreen')
        ax.set_title(f'Top {top_n} Most Frequent Words in {column.capitalize()}', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('Frequency', fontsize=12)
        plt.tight_layout()
        
        return fig, top_words
    
    def analyze_sources(self):
        """
        Analyze paper distribution by source
        """
        if self.df_cleaned is None:
            print("Please clean data first using clean_data()")
            return
        
        # Count papers by source
        source_counts = self.df_cleaned['source_x'].value_counts().head(10)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(source_counts.values, labels=source_counts.index, autopct='%1.1f%%', 
               startangle=90, colors=plt.cm.Set3(np.linspace(0, 1, len(source_counts))))
        ax.set_title('Distribution of Papers by Source', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return fig, source_counts
    
    def get_summary_statistics(self):
        """
        Generate summary statistics for the dataset
        """
        if self.df_cleaned is None:
            print("Please clean data first using clean_data()")
            return
        
        summary = {
            'total_papers': len(self.df_cleaned),
            'papers_with_abstract': self.df_cleaned['abstract'].notna().sum(),
            'papers_with_full_text': self.df_cleaned['has_full_text'].sum() if 'has_full_text' in self.df_cleaned.columns else 'N/A',
            'earliest_publication': self.df_cleaned['publication_year'].min(),
            'latest_publication': self.df_cleaned['publication_year'].max(),
            'avg_abstract_length': self.df_cleaned['abstract_word_count'].mean(),
            'unique_journals': self.df_cleaned['journal_clean'].nunique(),
            'unique_sources': self.df_cleaned['source_x'].nunique() if 'source_x' in self.df_cleaned.columns else 'N/A'
        }
        
        return summary

# Example usage
if __name__ == "__main__":
    analyzer = CORD19Analyzer('metadata.csv')
    
    if analyzer.load_data():
        analyzer.basic_exploration()
        analyzer.clean_data()
        
        # Generate visualizations
        analyzer.analyze_publications_over_time()
        analyzer.analyze_top_journals()
        analyzer.create_title_wordcloud()
        analyzer.analyze_word_frequency()
        analyzer.analyze_sources()
        
        # Print summary
        summary = analyzer.get_summary_statistics()
        print("\n=== SUMMARY STATISTICS ===")
        for key, value in summary.items():
            print(f"{key}: {value}")