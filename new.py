# BuildaBet.py
import streamlit as st
import pandas as pd
import requests

# --- Session state ---
for key in ['page','sport','game']:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state['page'] is None:
    st.session_state['page'] = 'home'

# --- API-Sports key ---
API_KEY = "30838192404ab22d79cbc4b13460279d"
HEADERS = {"x-apisports-key": API_KEY}

# --- Team logos ---
TEAM_LOGOS = {
    "KC":"https://a.espncdn.com/i/teamlogos/nfl/500/kc.png",
    "BUF":"https://a.espncdn.com/i/teamlogos/nfl/500/buf.png",
    "NE":"https://a.espncdn.com/i/teamlogos/nfl/500/ne.png",
    "MIA":"https://a.espncdn.com/i/teamlogos/nfl/500/mia.png",
    "LAL":"https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "GSW":"https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
    "BKN":"https://a.espncdn.com/i/teamlogos/nba/500/bkn.png",
    "MIL":"https://a.espncdn.com/i/teamlogos/nba/500/mil.png",
    "NYY":"https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png",
    "BOS":"https://a.espncdn.com/i/teamlogos/mlb/500/bos.png",
    "LAD":"https://a.espncdn.com/i/teamlogos/mlb/500/lad.png",
    "SF":"https://a.espncdn.com/i/teamlogos/mlb/500/sf.png"
}

# --- Navigation function ---
def go_to_page(page, sport=None, game=None):
    if sport:
        st.session_state['sport'] = sport
    if game:
        st.session_state['game'] = game
    st.session_state['page'] = page
    st.experimental_rerun()

# --- Fetch live pro games ---
def fetch_games(sport):
    league_ids = {"NFL":3,"NBA":12,"MLB":1,"CFB":None}
    league = league_ids.get(sport)
    if league is None:
        return []  # skip CFB for now
    url = f"https://v1.api-sports.io/fixtures?league={league}&season=2025"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        games = []
        if "response" in data and isinstance(data["response"], list):
            for g in data["response"]:
                home = g["teams"]["home"]["name"]
                away = g["teams"]["away"]["name"]
                fixture_time = g["fixture"].get("date","TBD").split("T")[1][:5] if "fixture" in g else "TBD"
                game_id = str(g["fixture"]["id"]) if "fixture" in g else "unknown"
                games.append({"home":home,"away":away,"time":fixture_time,"id":game_id})
        return games
    except Exception as e:
        st.error(f"Error fetching games: {e}")
        return []

# --- Fetch odds ---
def fetch_odds(game_id):
    url = f"https://v1.api-sports.io/odds?fixture={game_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        if "response" in data: return data["response"]
        return {"info":"No odds available"}
    except Exception as e:
        return {"error":f"Error fetching odds: {e}"}

# --- Style EV table ---
def style_ev(df):
    def color(val):
        if val>0: return 'background-color: lightgreen'
        elif val<0: return '#ff9999'
        else: return ''
    return df.style.applymap(lambda v: color(v) if isinstance(v,float) else '')

# --- Streamlit UI ---
st.set_page_config(page_title="Build a Bet", layout="wide")
st.title("🏆 Build a Bet 🏆")

# --- Home Page ---
if st.session_state['page']=='home':
    st.markdown("### Select a sport to build your bet:")
    col1,col2 = st.columns(2)
    col3,col4 = st.columns(2)
    with col1:
        if st.button("NFL 🏈"):
            go_to_page('games', sport='NFL')
    with col2:
        if st.button("NBA 🏀"):
            go_to_page('games', sport='NBA')
    with col3:
        if st.button("MLB ⚾️"):
            go_to_page('games', sport='MLB')
    with col4:
        if st.button("CFB 🏟"):
            go_to_page('games', sport='CFB')

# --- Games Page ---
elif st.session_state['page']=='games':
    sport = st.session_state['sport']
    st.header(f"{sport} Games Today")
    games = fetch_games(sport)
    if not games: st.info("No games found.")
    else:
        cols = st.columns(2)
        for idx, g in enumerate(games):
            col = cols[idx%2]
            home, away, time, game_id = g['home'], g['away'], g['time'], g['id']
            home_logo, away_logo = TEAM_LOGOS.get(home,""), TEAM_LOGOS.get(away,"")
            with col:
                st.markdown(f"""
                <div style='border:1px solid #ddd; padding:10px; border-radius:10px; text-align:center; margin-bottom:10px;'>
                <h3>{away} @ {home}</h3><p>{time}</p>
                <div style='display:flex; justify-content:space-around; align-items:center;'>
                <img src='{away_logo}' width='50'>
                <img src='{home_logo}' width='50'>
                </div></div>""", unsafe_allow_html=True)
                if st.button(f"See Bets for {away} @ {home}", key=game_id):
                    go_to_page('bets', game=game_id)
    if st.button("⬅ Back to Home"):
        go_to_page('home')

# --- Bets Page ---
elif st.session_state['page']=='bets':
    sport = st.session_state['sport']
    game_id = st.session_state['game']
    st.header(f"💰 Best Bets for Game ID: {game_id}")

    # Pro leagues odds
    if sport!="CFB":
        odds_data = fetch_odds(game_id)
        st.subheader("Live Odds")
        st.write(odds_data)

    if st.button("⬅ Back to Games"):
        go_to_page('games', sport=sport)
