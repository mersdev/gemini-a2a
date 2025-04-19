from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

activities_agent = Agent(
    name="activities_agent",
    model="gemini-2.0-flash",
    description="Suggests interesting activities for the user at a destination.",
    instruction=(
        "Given a destination, dates, and budget (in USD), suggest 2-3 engaging tourist or cultural activities. "
        "For each activity, provide name, description, price estimate, and duration in hours. "
        "ALWAYS respond in JSON format with an 'activities' array containing objects with the following structure:\n"
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent,
    app_name="activities_app",
    session_service=session_service
)

USER_ID = "user_activities"
SESSION_ID = "session_activities"

async def execute(request):
    session_service.create_session(
        app_name="activities_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = (
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of USD{request['budget']}. Suggest 2-3 activities, each with name, description, price estimate, and duration. "
        f"Respond in JSON format using the key 'activities' with a list of activity objects."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            
            # Clean up markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json\n"):
                    response_text = response_text[5:]
            
            try:
                parsed = json.loads(response_text)
                if "activities" in parsed and isinstance(parsed["activities"], list):
                    return {"activities": parsed["activities"]}
                else:
                    print("❌ 'activities' key missing or not a list in response JSON")
                    return {"activities": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("❌ JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"activities": response_text}  # fallback to raw text
