## Week 8: Python Frameworks Assignment

# CORD-19 Metadata Analysis with Streamlit

This repository contains a Python-based data analysis and visualization project using the metadata from the CORD-19 research dataset. The goal is to explore COVID-19 research trends and present insights through an interactive Streamlit dashboard.

---

## Project Overview

- **Dataset**: `metadata.csv` from the [CORD-19 Kaggle dataset](https://www.kaggle.com/datasets/allen-institute-for-ai/CORD-19-research-challenge)

- **Tools Used**:
  - `pandas` – data loading and manipulation
  - `matplotlib` / `seaborn` – visualizations
  - `Streamlit` – interactive web app
  - `wordcloud` – text visualization
  - `plotly` – interactive charts
  - `numpy` – numerical computations

- **Objectives**:
  - Load and clean real-world research data
  - Perform basic analysis and extract insights
  - Visualize trends in publication dates, journals, and title keywords
  - Build a simple dashboard to present findings interactively

---

# Project Structure

```bash
Frameworks_Assignment/
│
├── app.py                 # Main Streamlit application
├── data_analysis.py       # Data analysis and visualization module
├── requirements.txt       # Python dependencies list
├── metadata.csv           # Dataset used for analysis (download separately)
├── README.md              # Project documentation

```
## File Descriptions

- **app.py**: Main Streamlit application containing the web interface
- **data_analysis.py**: Contains data processing, analysis, and visualization functions
- **requirements.txt**: Lists all Python packages required to run the project
- **metadata.csv**: Dataset file (not included in repo due to size)

---

## Visualizations Included

- Bar chart of publications by year  
- Top journals publishing COVID-19 research  
- Word cloud of frequent title keywords  
- Distribution of papers by source  

---

## How to Run

### Prerequisites
- Python 3.7+ installed
- Git for cloning the repository

### Installation Steps

1. **Clone the repository**:
```bash
git clone https://github.com/Gideon-Kipngeno/wk-8-python-Gideon-Kipngeno_Frameworks_Assignment.git
cd wk-8-python-Gideon-Kipngeno_Frameworks_Assignment
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. **Download the dataset** (separately due to size)
   - Place `metadata.csv` in the project root

4. **Run the application**
```bash
streamlit run app.py 
```
5. Access the application:

Open your web browser to http://localhost:8501

The dashboard will load automatically

--- 

## Learning Outcomes
1. Hands-on experience with real-world datasets

2. Data cleaning and preprocessing techniques

3. Visual storytelling with Python

4. Building and deploying interactive apps with Streamlit


## 👨‍💻 Author

Gideon Kipngeno - PLP Academy Assignment

---

## Contact

For questions or collaboration:

GitHub: @Gideon-Kipngeno

LinkedIn: Gideon-K-Ngetich

Email:giddykipngeno5@gmail.com


## Acknowledgments

- CORD-19 Dataset: Allen Institute for AI for providing the comprehensive research dataset

- Streamlit Community: For the excellent documentation and support

- Python Data Ecosystem: pandas, matplotlib, seaborn, plotly, and wordcloud developers