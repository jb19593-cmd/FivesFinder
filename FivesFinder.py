import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Fives Finder", page_icon="⚽", layout="wide")

st.title("⚽ Fives Finder")
st.caption("Find & organise 5-a-side games across Scotland")

# Session state
if "profile" not in st.session_state:
    st.session_state.profile = None
if "matches" not in st.session_state:
    st.session_state.matches = []
if "joined_matches" not in st.session_state:
    st.session_state.joined_matches = {}

# Sidebar Profile
with st.sidebar:
    st.header("Your Player Profile")
    if st.session_state.profile is None:
        name = st.text_input("Full Name")
        position = st.selectbox("Preferred Position", ["GK", "Defender", "Midfielder", "Striker", "Any"])
        level = st.slider("Skill Level (1-5)", 1, 5, 3)
        area = st.selectbox("Main Area", ["Glasgow", "Edinburgh", "Aberdeen", "Dundee", "Inverness", "Other"])
        bio = st.text_area("Short Bio", "Looking for regular games and good banter")
        
        if st.button("Create Profile", type="primary"):
            st.session_state.profile = {
                "name": name or "Anonymous Player",
                "position": position,
                "level": level,
                "area": area,
                "bio": bio
            }
            st.success("Profile created!")
    else:
        st.success(f"✅ {st.session_state.profile['name']}")
        st.write(f"Position: {st.session_state.profile['position']} • Level: {st.session_state.profile['level']}/5")
        if st.button("Edit Profile"):
            st.session_state.profile = None

# Main Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Browse Matches", "➕ Create Match", "💬 My Matches"])

with tab1:  # Browse Matches with Filters
    st.subheader("Available Matches")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        selected_city = st.selectbox("Filter by City", 
            ["All Cities", "Glasgow", "Edinburgh", "Aberdeen", "Dundee", "Inverness"])
    with col2:
        selected_day = st.selectbox("Filter by Day", 
            ["Any Day", "Today", "Tomorrow", "This Weekend", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    
    # Filter matches
    filtered_matches = st.session_state.matches
    if selected_city != "All Cities":
        filtered_matches = [m for m in filtered_matches if selected_city in m.get('location', '')]
    
    if selected_day != "Any Day":
        today = datetime.today()
        if selected_day == "Today":
            filtered_matches = [m for m in filtered_matches if m['date'] == today.strftime("%d %b %Y")]
        elif selected_day == "Tomorrow":
            tomorrow = today + timedelta(days=1)
            filtered_matches = [m for m in filtered_matches if m['date'] == tomorrow.strftime("%d %b %Y")]
        # You can expand weekend logic if needed

    if not filtered_matches:
        st.info("No matches found with current filters. Create one or change filters!")
    else:
        for match in filtered_matches:
            with st.container(border=True):
                col1, col2 = st.columns([4, 2])
                with col1:
                    st.write(f"**{match['title']}**")
                    st.write(f"🕒 {match['date']} at {match['time']}")
                    st.write(f"📍 {match['location']}")
                    st.write(f"💰 £{match['price']} pp • {match['spots_left']} spots left")
                with col2:
                    if st.button("Join Match", key=f"join_{match['id']}"):
                        if match['id'] not in st.session_state.joined_matches:
                            st.session_state.joined_matches[match['id']] = []
                        match['spots_left'] -= 1
                        st.success(f"Joined {match['title']}!")

with tab2:  # Create Match
    st.subheader("Create a New Match")
    with st.form("create_match_form"):
        title = st.text_input("Match Title", "Casual 5-a-side")
        date = st.date_input("Date", datetime.today() + timedelta(days=1))
        time = st.time_input("Kick-off Time", datetime.strptime("19:30", "%H:%M").time())
        location = st.text_input("Pitch / Location", "Powerleague Glasgow")
        price = st.number_input("Price per player (£)", min_value=0, value=8)
        spots_needed = st.number_input("How many players needed?", min_value=1, max_value=12, value=6)
        
        if st.form_submit_button("Create Match", type="primary"):
            new_match = {
                "id": len(st.session_state.matches) + 1,
                "title": title,
                "date": date.strftime("%d %b %Y"),
                "time": time.strftime("%H:%M"),
                "location": location,
                "price": price,
                "spots_left": spots_needed,
                "creator": st.session_state.profile["name"] if st.session_state.profile else "Anonymous"
            }
            st.session_state.matches.append(new_match)
            st.success("Match created successfully! 🎉")

with tab3:  # My Matches + Chat
    st.subheader("My Joined Matches")
    if not st.session_state.joined_matches:
        st.info("You haven't joined any matches yet.")
    else:
        for match_id, messages in list(st.session_state.joined_matches.items()):
            match = next((m for m in st.session_state.matches if m['id'] == match_id), None)
            if match:
                st.write(f"**{match['title']}** — {match['date']} at {match['time']}")
                for msg in messages[-8:]:
                    st.write(f"**{msg['user']}**: {msg['text']}")
                
                new_msg = st.text_input("Send message...", key=f"input_{match_id}")
                if st.button("Send", key=f"send_{match_id}"):
                    if new_msg.strip():
                        messages.append({
                            "user": st.session_state.profile["name"] if st.session_state.profile else "You",
                            "text": new_msg
                        })
                        st.rerun()

st.sidebar.caption("Fives Finder Scotland • Pure 5-a-side football")
