
import requests
import pandas as pd
import streamlit as st

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# --------------------------------
# 1. DASHBOARD SETTINGS
# --------------------------------

st.set_page_config(
    page_title="FPL Gameweek Analyzer",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ FPL Next Gameweek Analyzer")
st.write("Analyze players and fixtures for the upcoming Gameweek.")

BASE_URL = "https://fantasy.premierleague.com/api/"


# --------------------------------
# 2. CONNECT TO FPL API
# --------------------------------

@st.cache_data(ttl=1800)
def get_fpl_data():

    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    retry_strategy = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("https://", adapter)

    # Get player and team data
    response = session.get(
        BASE_URL + "bootstrap-static/",
        timeout=(10, 45)
    )

    response.raise_for_status()

    data = response.json()

    players = pd.DataFrame(data["elements"])
    teams = pd.DataFrame(data["teams"])
    events = pd.DataFrame(data["events"])

    # Get fixture data
    fixture_response = session.get(
        BASE_URL + "fixtures/",
        timeout=(10, 45)
    )

    fixture_response.raise_for_status()

    fixtures = pd.DataFrame(fixture_response.json())

    session.close()

    return players, teams, events, fixtures


# --------------------------------
# 3. LOAD DATA
# --------------------------------

try:

    with st.spinner("Connecting to FPL API..."):

        players, teams, events, fixtures = get_fpl_data()

    st.success("FPL data loaded successfully!")

    # --------------------------------
    # 4. FIND NEXT GAMEWEEK
    # --------------------------------

    next_event = events[events["is_next"] == True]

    if next_event.empty:

        st.warning("The next Gameweek is not available yet.")

    else:

        gameweek_id = int(next_event.iloc[0]["id"])
        gameweek_name = next_event.iloc[0]["name"]
        deadline = next_event.iloc[0]["deadline_time"]

        st.header(gameweek_name)

        st.write("Deadline:", deadline)

        # --------------------------------
        # 5. PREPARE PLAYER DATA
        # --------------------------------

        team_names = dict(
            zip(teams["id"], teams["name"])
        )

        players["team_name"] = players["team"].map(team_names)

        positions = {
            1: "Goalkeeper",
            2: "Defender",
            3: "Midfielder",
            4: "Forward"
        }

        players["position"] = players["element_type"].map(positions)

        # --------------------------------
        # 6. DASHBOARD SUMMARY
        # --------------------------------

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Players", len(players))

        col2.metric("Gameweek", gameweek_id)

        col3.metric("Total Teams", len(teams))

        st.divider()

        # --------------------------------
        # 7. TOP 10 PLAYERS
        # --------------------------------

        st.subheader("🏆 Top 10 Players by Total Points")

        top_players = players.sort_values(
            by="total_points",
            ascending=False
        ).head(10)

        display_columns = [
            "web_name",
            "team_name",
            "position",
            "now_cost",
            "total_points",
            "form",
            "points_per_game"
        ]

        st.dataframe(
            top_players[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------
        # 8. PLAYER FILTER
        # --------------------------------

        st.subheader("🔍 Search Players")

        selected_position = st.selectbox(
            "Choose player position",
            ["All", "Goalkeeper", "Defender",
             "Midfielder", "Forward"]
        )

        if selected_position == "All":

            filtered_players = players

        else:

            filtered_players = players[
                players["position"] == selected_position
            ]

        st.dataframe(
            filtered_players[
                display_columns
            ].sort_values(
                by="total_points",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------
        # 9. FIXTURE ANALYSIS
        # --------------------------------

        st.subheader("📅 Next Gameweek Fixtures")

        gw_fixtures = fixtures[
            fixtures["event"] == gameweek_id
        ].copy()

        if gw_fixtures.empty:

            st.info("Fixtures are not available yet.")

        else:

            gw_fixtures["Home Team"] = (
                gw_fixtures["team_h"].map(team_names)
            )

            gw_fixtures["Away Team"] = (
                gw_fixtures["team_a"].map(team_names)
            )

            gw_fixtures["Home Difficulty"] = (
                gw_fixtures["team_h_difficulty"]
            )

            gw_fixtures["Away Difficulty"] = (
                gw_fixtures["team_a_difficulty"]
            )

            st.dataframe(
                gw_fixtures[
                    [
                        "Home Team",
                        "Away Team",
                        "Home Difficulty",
                        "Away Difficulty"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        # --------------------------------
        # 10. TOP 10 PLAYERS CHART
        # --------------------------------

        st.subheader("📊 Top Players Performance")

        chart_data = top_players.set_index(
            "web_name"
        )["total_points"]

        st.bar_chart(chart_data)

        st.caption(
            "Player rankings are based on total season points, "
            "not predicted next-Gameweek points."
        )


# --------------------------------
# 11. ERROR HANDLING
# --------------------------------

except requests.exceptions.Timeout:

    st.error("FPL API request timed out.")

    if st.button("Try Again"):
        st.cache_data.clear()
        st.rerun()


except requests.exceptions.RequestException as error:

    st.error("Unable to connect to the FPL API.")
    st.write(str(error))

    if st.button("Retry Connection"):
        st.cache_data.clear()
        st.rerun()


except Exception as error:

    st.error("Something went wrong.")
    st.write(str(error))
