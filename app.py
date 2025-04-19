import streamlit as st
import requests

st.set_page_config(page_title="ADK-Powered Travel Planner", page_icon="✈️")

st.title("🌍 ADK-Powered Travel Planner")

# ✨ Add start location here
origin = st.text_input("Where are you flying from?", placeholder="e.g., New York")

destination = st.text_input("Destination", placeholder="e.g., Paris")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
budget = st.number_input("Budget (in USD)", min_value=100, step=50)

if st.button("Plan My Trip ✨"):
    if not all([origin, destination, start_date, end_date, budget]):
        st.warning("Please fill in all the details.")
    else:
        payload = {
            "origin": origin,
            "destination": destination,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "budget": budget
        }
        response = requests.post("http://localhost:10000/run", json=payload)

        if response.ok:
            data = response.json()
            st.subheader("✈️ Flights")
            st.markdown(data["flights"])
            st.subheader("🏨 Stays")
            st.markdown(data["stay"])
            st.subheader("🗺️ Activities")
            activities_md = ""
            for activity in data["activities"]:
                with st.container():
                    st.write(f"🎯 **{activity['name']}**")
                    st.write(activity['description'])
        else:
            st.error("Failed to fetch travel plan. Please try again.")


# uvicorn agents.host.__main__:app --port 10000 &
# uvicorn agents.flight.__main__:app --port 10001 &
# uvicorn agents.stay.__main__:app --port 10002 &
# uvicorn agents.activities.__main__:app --port 10003 &
# streamlit run /Users/BAORLIM/playground/gemini-a2a/app.py