# ⚽ FPL Next Gameweek Analyzer

An interactive Fantasy Premier League (FPL) dashboard built using Python and Streamlit.

## Project Overview

This project analyzes Fantasy Premier League data to help FPL managers understand player performance and upcoming fixtures.

It retrieves live data from the public FPL API and displays useful statistics through an interactive dashboard.

## Features

- Live player data from the FPL API
- Total player and team statistics
- Top 10 players ranked by total season points
- Player filtering by position
- Upcoming Gameweek fixtures
- Home and away fixture difficulty
- Player performance bar chart

## Technologies Used

- Python
- Pandas
- Requests
- Streamlit
- Plotly

## Installation

1. Clone this repository:

   ```bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   ```

2. Open the project folder:

   ```bash
   cd fpl_gw12
   ```

3. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the dashboard:

   ```bash
   python -m streamlit run app.py
   ```

## Data Source

Fantasy Premier League Public API:

https://fantasy.premierleague.com/api/

## Future Improvements

- Predicted points for upcoming Gameweeks
- Captain and vice-captain recommendations
- Player comparison dashboard
- Budget-based team selection
- Machine learning-based player predictions

## Author

Created as a personal football analytics project while learning Python and data analysis.
