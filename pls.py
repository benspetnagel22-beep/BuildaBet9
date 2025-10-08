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

# --- Team logos (partial, add more if you want) ---
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

# --- Fetch live pro games ---
def fetch_games(sport):
    league_ids = {"NFL":3,"NBA":12,"MLB":1,"CFB":None}
    league = league_ids.get(sport)
    if league is None:
        # Placeholder CFB games
        return [
            {"home": "Alabama", "away": "Georgia", "time": "7:00 PM", "id": "AL_GA"},
            {"home": "Ohio State", "away": "Michigan", "time": "8:00 PM", "id": "OSU_MICH"}
        ]
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

# --- Streamlit UI ---
st.set_page_config(page_title="Build a Bet", layout="wide")
st.title("🏆 Build a Bet 🏆")

# --- Home Page ---
if st.session_state['page']=='home':
    st.markdown("### What sport would you like to bet on?")
    col1,col2 = st.columns(2)
    col3,col4 = st.columns(2)
    with col1:
        if st.button("NFL 🏈"): st.session_state.update({'sport':'NFL','page':'games'}); st.experimental_rerun()
    with col2:
        if st.button("NBA 🏀"): st.session_state.update({'sport':'NBA','page':'games'}); st.experimental_rerun()
    with col3:
        if st.button("MLB ⚾️"): st.session_state.update({'sport':'MLB','page':'games'}); st.experimental_rerun()
    with col4:
        if st.button("CFB 🏟"): st.session_state.update({'sport':'CFB','page':'games'}); st.experimental_rerun()

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
                    st.session_state.update({'game':game_id,'page':'bets'})
                    st.experimental_rerun()
    if st.button("⬅ Back to Home"): st.session_state['page']='home'; st.experimental_rerun()

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

    st.markdown("### Player/Game Props (Simulated Example)")
    # Example simulated props
    props = pd.DataFrame([
        {"player":"QB1","prop":"Passing Yards","line":280,"odds":1.9,"reason":"Based on season performance"},
        {"player":"RB1","prop":"Rushing Yards","line":100,"odds":1.85,"reason":"Expected workload"},
        {"player":"WR1","prop":"Receiving Yards","line":70,"odds":1.85,"reason":"Expected target share"}
    ])
    st.table(props)

    if st.button("⬅ Back to Games"): st.session_state['page']='games'; st.experimental_rerun()
