import base64
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.agents.workflow import get_disaster_agent_graph, AgentState
from backend.app.schemas.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Multi-Agent Chat Engine"])

# Load LangGraph once
workflow_graph = get_disaster_agent_graph()

@router.post("/execute", response_model=ChatResponse)
def execute_chat_flow(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Triggers the multi-agent cooperative workflow inside LangGraph.
    Uses request location details and returns English-only responses.
    """
    # 1. Decode base64 image data if sent
    image_bytes = None
    if request.image_data_b64:
        try:
            raw_b64 = request.image_data_b64
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",")[1]
            image_bytes = base64.b64decode(raw_b64)
        except Exception as e:
            print(f"Error decoding request image base64: {e}")

    # 2. Use anonymous request context
    family = []
    medical = ""
    lang = "English"

    # 3. Form initial LangGraph state dict
    initial_state = AgentState(
        user_query=request.user_query,
        user_location=request.user_location,
        user_lat=request.user_lat,
        user_lng=request.user_lng,
        user_language=lang,
        user_medical_conditions=medical,
        user_family_members=family,
        image_bytes=image_bytes,
        image_name=request.image_name,
        conversation_history=[],
        active_agents=[],
        agent_logs=[],
        vision_assessment=None,
        weather_info=None,
        search_alerts=[],
        navigation_info=None,
        shelter_info=[],
        hospital_info=[],
        medical_advice=None,
        resource_info=[],
        communication_info=None,
        government_info=[],
        recovery_info=None,
        volunteer_info=None,
        final_response=""
    )

    # 4. Invoke graph
    try:
        final_state = workflow_graph.invoke(initial_state)
    except Exception as e:
        print(f"LangGraph execution exception: {e}")
        # Manual fallback aggregation if workflow fails
        from backend.app.agents.workflow import coordinator_aggregate_node, coordinator_node
        # Run coordinator node manually to build logs and fallback responses
        state = coordinator_node(initial_state)
        final_state = coordinator_aggregate_node(state)

    # 5. Extract results
    return ChatResponse(
        final_response=final_state.get("final_response", "Failed to compile response. Please try again."),
        agent_logs=final_state.get("agent_logs", []),
        vision_assessment=final_state.get("vision_assessment"),
        weather_info=final_state.get("weather_info"),
        search_alerts=final_state.get("search_alerts", []),
        navigation_info=final_state.get("navigation_info"),
        shelter_info=final_state.get("shelter_info", []),
        hospital_info=final_state.get("hospital_info", []),
        medical_advice=final_state.get("medical_advice"),
        resource_info=final_state.get("resource_info", []),
        communication_info=final_state.get("communication_info"),
        government_info=final_state.get("government_info", []),
        recovery_info=final_state.get("recovery_info"),
        volunteer_info=final_state.get("volunteer_info")
    )
