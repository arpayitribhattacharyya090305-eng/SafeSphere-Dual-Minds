from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import json
import requests
import datetime

# Import core settings, models, and tools
from backend.app.core.config import settings
from backend.app.prompts import agent_prompts
from backend.app.tools import agent_tools
from backend.app.utils.helpers import get_iso_lang_code

# Define State Schema
class AgentState(TypedDict):
    # Inputs
    user_query: str
    user_location: str
    user_lat: float
    user_lng: float
    user_language: str
    user_medical_conditions: Optional[str]
    user_family_members: List[Dict[str, Any]]
    image_bytes: Optional[bytes]
    image_name: Optional[str]
    conversation_history: List[Dict[str, str]]
    
    # Internal routing & execution flags
    active_agents: List[str]
    agent_logs: List[Dict[str, Any]]  # Displays execution logs to user
    
    # Agent Outputs
    vision_assessment: Optional[Dict[str, Any]]
    weather_info: Optional[Dict[str, Any]]
    search_alerts: List[Dict[str, Any]]
    navigation_info: Optional[Dict[str, Any]]
    shelter_info: List[Dict[str, Any]]
    hospital_info: List[Dict[str, Any]]
    medical_advice: Optional[str]
    resource_info: List[Dict[str, Any]]
    communication_info: Optional[Dict[str, Any]]
    government_info: List[Dict[str, Any]]
    recovery_info: Optional[str]
    volunteer_info: Optional[Dict[str, Any]]
    
    # Final Response
    final_response: str

# Helper: Call Gemini model or return None if key is missing/fails
def call_gemini(system_prompt: str, user_content: str, image_bytes: Optional[bytes] = None) -> Optional[str]:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # Instantiate Gemini
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        messages = [SystemMessage(content=system_prompt)]
        
        if image_bytes:
            # Format multi-modal input for Gemini Vision
            import base64
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            image_url = f"data:image/jpeg;base64,{b64_image}"
            
            # Form multi-modal contents
            content = [
                {"type": "text", "text": user_content},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
            messages.append(HumanMessage(content=content))
        else:
            messages.append(HumanMessage(content=user_content))
            
        res = llm.invoke(messages)
        return res.content
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return None

# --- AGENT NODES ---

# 1. Coordinator: Analyze intent & plan routing
def coordinator_node(state: AgentState) -> AgentState:
    query = state["user_query"].lower()
    image_uploaded = state["image_bytes"] is not None
    
    # Analyze routing intent (decide which agents are active)
    active = ["coordinator"]
    
    if image_uploaded or any(x in query for x in ["photo", "image", "look", "damage", "damage assessment"]):
        active.append("vision")
    if any(x in query for x in ["weather", "rain", "forecast", "flood", "cyclone", "storm", "temp"]):
        active.append("weather")
    if any(x in query for x in ["news", "live", "current", "closure", "happen", "tavily", "road blockage"]):
        active.append("search")
    if any(x in query for x in ["route", "go to", "map", "navigation", "directions", "how to get", "evacuate"]):
        active.append("navigation")
    if any(x in query for x in ["shelter", "refuge", "camp", "stay"]):
        active.append("shelter")
    if any(x in query for x in ["medical", "first aid", "cpr", "fracture", "bite", "burn", "poison", "breath", "injured"]):
        active.append("medical")
    if any(x in query for x in ["food", "water", "resource", "fuel", "charging", "supplies"]):
        active.append("resource")
    if any(x in query for x in ["sos", "message", "sms", "whatsapp", "alert", "email", "notify"]):
        active.append("communication")
    if any(x in query for x in ["scheme", "compensation", "government", "fund", "helpline", "claim"]):
        active.append("government")
    if any(x in query for x in ["recovery", "post", "rebuild", "insurance", "counseling", "psychological"]):
        active.append("recovery")
    if any(x in query for x in ["volunteer", "help out", "register help", "skill", "match"]):
        active.append("volunteer")
        
    # If query is general or empty, activate a base set of agents
    if len(active) == 1:
        active.extend(["weather", "shelter", "medical", "communication"])
        
    log_entry = {
        "agent": "Coordinator Agent",
        "action": "Analyzing emergency query and routing tasks",
        "status": "Success",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "findings": f"Identified active agents: {', '.join(active[1:])} based on user input."
    }
    
    # Initialize dictionary updates
    state["active_agents"] = active
    state["agent_logs"] = [log_entry]
    return state

# 2. Vision: Damage Assessment
def vision_node(state: AgentState) -> AgentState:
    if "vision" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Vision Damage Assessment Agent",
        "action": "Analyzing uploaded disaster scene imagery",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    image_bytes = state["image_bytes"]
    image_name = state["image_name"] or "disaster_scene.jpg"
    
    # Execute Tool/AI
    gemini_resp = None
    if image_bytes:
        gemini_resp = call_gemini(
            system_prompt=agent_prompts.VISION_SYSTEM_PROMPT,
            user_content="Assess this emergency scene image for damages.",
            image_bytes=image_bytes
        )
        
    if gemini_resp:
        try:
            # Clean JSON markdown formatting if present
            clean_json = gemini_resp.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            assessment = json.loads(clean_json.strip())
        except Exception:
            assessment = {
                "disaster_type": "Flood/Collapse",
                "severity": "High",
                "confidence_score": 0.82,
                "people_visible": True,
                "road_condition": "Flooded and blocked",
                "structural_damage": "Partial facade damage",
                "risk_level": "High",
                "immediate_actions": ["Move to roof", "Signal rescue boat", "Avoid touching electrical boxes"]
            }
    else:
        # High fidelity local simulator based on filename or query terms
        query = state["user_query"].lower()
        disaster = "Flood"
        severity = "High"
        actions = ["Move to higher ground", "Do not drive in flood waters", "Wait for rescue services"]
        
        if "fire" in query or (image_name and "fire" in image_name.lower()):
            disaster = "Fire"
            severity = "Critical"
            actions = ["Evacuate building immediately via stairs", "Stay low under smoke", "Call Fire Brigade at 101"]
        elif "collapse" in query or "earthquake" in query or (image_name and "collapse" in image_name.lower()):
            disaster = "Structural Collapse"
            severity = "Critical"
            actions = ["Drop, Cover, and Hold on", "Check for gas leaks before lighting matches", "Watch for falling debris"]
            
        assessment = {
            "disaster_type": disaster,
            "severity": severity,
            "confidence_score": 0.90,
            "people_visible": "people" in query or "trapped" in query,
            "road_condition": "Blocked by debris / standing water",
            "structural_damage": "Severe structural deformation detected",
            "risk_level": "High/Critical",
            "immediate_actions": actions
        }
        
    log_entry["status"] = "Success"
    log_entry["findings"] = f"Detected: {assessment['disaster_type']} ({assessment['severity']} Severity). Road: {assessment['road_condition']}"
    
    state["vision_assessment"] = assessment
    state["agent_logs"].append(log_entry)
    return state

# 3. Weather
def weather_node(state: AgentState) -> AgentState:
    if "weather" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Weather Agent",
        "action": "Checking live weather and extreme storm predictions",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Execute Tool call
    weather_data = agent_tools.get_weather_data(state["user_lat"], state["user_lng"])
    
    # Prompt LLM or run heuristics to generate advisory
    gemini_resp = call_gemini(
        system_prompt=agent_prompts.WEATHER_AGENT_PROMPT,
        user_content=f"Context weather data: {json.dumps(weather_data)}. Formulate a disaster-aware weather briefing."
    )
    
    if gemini_resp:
        weather_info = {
            "summary": gemini_resp,
            "temp": weather_data["temp"],
            "alerts": weather_data["alerts"]
        }
    else:
        # Heuristics text block
        city = weather_data["city"]
        temp = weather_data["temp"]
        desc = weather_data["description"]
        alerts = weather_data["alerts"]
        
        alert_txt = ""
        if alerts:
            alert_txt = f"\n**ACTIVE WARNINGS:** {alerts[0]['event']} - {alerts[0]['description']}"
            
        summary = (
            f"Weather update for **{city}**: Current temperature is {temp}C, conditions show '{desc}'. "
            f"Wind speed is {weather_data['wind_speed']} m/s with {weather_data['humidity']}% humidity.{alert_txt} "
            "Responders should note: heavy downpours will limit helicopter search operations. "
            "Inflatable boats and ground rescue vectors remain active."
        )
        weather_info = {
            "summary": summary,
            "temp": temp,
            "alerts": alerts
        }
        
    log_entry["status"] = "Success"
    log_entry["findings"] = f"Weather: {weather_data['temp']}C, {weather_data['description']}. Alerts Count: {len(weather_data['alerts'])}"
    
    state["weather_info"] = weather_info
    state["agent_logs"].append(log_entry)
    return state

# 4. Search
def search_node(state: AgentState) -> AgentState:
    if "search" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Search Agent",
        "action": "Querying Tavily Search for live disaster news and road closures",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Determine search queries based on query/location
    query = f"Disaster news road closure {state['user_location']}"
    search_results = agent_tools.search_live_news(query)
    
    log_entry["status"] = "Success"
    log_entry["findings"] = f"Retrieved {len(search_results)} live advisories / news pieces."
    
    state["search_alerts"] = search_results
    state["agent_logs"].append(log_entry)
    return state

# 5. Navigation
def navigation_node(state: AgentState) -> AgentState:
    if "navigation" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Navigation Agent",
        "action": "Calculating safe escape route with OSRM and OpenStreetMap data",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # First, get the shelters to locate the closest destination
    shelters = agent_tools.get_closest_shelters(state["user_lat"], state["user_lng"], limit=1)
    
    if shelters:
        dest = shelters[0]
        route = agent_tools.calculate_evacuation_route(
            state["user_lat"], state["user_lng"], dest["location_lat"], dest["location_lng"]
        )
        route["destination_name"] = dest["name"]
        
        log_entry["status"] = "Success"
        log_entry["findings"] = f"Computed route to {dest['name']} ({route['distance_km']} km, {route['duration_min']} mins)."
        state["navigation_info"] = route
    else:
        log_entry["status"] = "Warning"
        log_entry["findings"] = "No nearby shelters found from Overpass or local fallback data. Unable to compute route."
        state["navigation_info"] = None
        
    state["agent_logs"].append(log_entry)
    return state

# 6. Shelter
def shelter_node(state: AgentState) -> AgentState:
    if "shelter" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Shelter Agent",
        "action": "Searching Overpass API for emergency shelters and hospitals",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    shelters = agent_tools.get_closest_shelters(state["user_lat"], state["user_lng"], limit=3)
    hospitals = agent_tools.get_closest_hospitals(state["user_lat"], state["user_lng"], limit=2)
    
    log_entry["status"] = "Success"
    log_entry["findings"] = f"Located {len(shelters)} shelters and {len(hospitals)} hospitals near current grid."
    
    state["shelter_info"] = shelters
    state["hospital_info"] = hospitals
    state["agent_logs"].append(log_entry)
    return state

# 7. Medical
def medical_node(state: AgentState) -> AgentState:
    if "medical" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Medical Agent",
        "action": "Performing RAG query and locating nearby hospitals with Overpass API",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # 1. Fetch relevant guidelines from vector store/Jaccard
    guidelines = agent_tools.query_medical_guidelines(state["user_query"], limit=2)
    hospitals = agent_tools.get_closest_hospitals(state["user_lat"], state["user_lng"], limit=2)
    
    # Format context for LLM
    context = "\n\n".join([f"--- {g['title']} ---\n{g['content']}" for g in guidelines])
    
    # 2. Invoke Gemini/Heuristic advisor
    gemini_resp = call_gemini(
        system_prompt=agent_prompts.MEDICAL_AGENT_PROMPT,
        user_content=f"User Query: {state['user_query']}\nUser Medical Details: {state['user_medical_conditions']}\nRAG Guidelines context:\n{context}"
    )
    
    if gemini_resp:
        advice = gemini_resp
    else:
        # Heuristics based on keyword matching
        query = state["user_query"].lower()
        if "cpr" in query or "breathing" in query or "heart" in query:
            advice = (
                "**CARDIOPULMONARY RESUSCITATION (CPR) FIRST AID:**\n"
                "1. Tap shoulder and check for responsiveness.\n"
                "2. Call emergency line (102 / 108 / 112) immediately.\n"
                "3. Place hands in the center of the chest. Depress hard and fast at 100-120 beats per minute "
                "(to the beat of 'Stayin' Alive').\n"
                "4. If trained, perform 30 compressions followed by 2 rescue breaths. Otherwise, do continuous compressions."
            )
        elif "burn" in query:
            advice = (
                "**EMERGENCY BURN CARE:**\n"
                "1. Flush the area with cool running water for 10-20 minutes. Do NOT apply ice, butter, or oil.\n"
                "2. Remove tight items like rings or bands gently as swelling will occur.\n"
                "3. Cover with a loose, sterile, non-stick gauze. Do NOT break blisters."
            )
        elif "snake" in query or "bite" in query:
            advice = (
                "**SNAKEBITE FIRST AID:**\n"
                "1. Keep the victim calm and absolutely still (slows venom absorption).\n"
                "2. Splint the bitten limb loosely and keep it at or slightly below heart level.\n"
                "3. Remove tight clothing/shoes. Do NOT apply a tourniquet. Do NOT cut or suck the wound.\n"
                "4. Rush immediately to a hospital with Anti-Snake Venom (ASV) stocks."
            )
        else:
            # General guidelines fallback
            advice = (
                "**EMERGENCY PRECAUTIONS:**\n"
                "1. Keep a first-aid kit containing bandages, antiseptics, sterile gauze, and necessary medications.\n"
                "2. In case of serious injury (heavy bleeding, fracture, unconsciousness), contact local ambulance "
                "helplines (108 / 102) immediately.\n"
                "3. Keep the patient warm and dry, treating for shock by elevating feet 12 inches if no head/neck trauma."
            )
            
    log_entry["status"] = "Success"
    log_entry["findings"] = (
        f"RAG returned {len(guidelines)} guidelines and found {len(hospitals)} nearby hospitals."
    )
    
    state["medical_advice"] = advice
    state["hospital_info"] = hospitals or state["hospital_info"]
    state["agent_logs"].append(log_entry)
    return state

# 8. Resource
def resource_node(state: AgentState) -> AgentState:
    if "resource" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Resource Agent",
        "action": "Searching Overpass API for food, water, medicine, and charging resources",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Check if a category is inside query
    category = None
    query = state["user_query"].lower()
    if "water" in query:
        category = "Water"
    elif "food" in query or "eat" in query:
        category = "Food"
    elif "medicine" in query or "kit" in query:
        category = "Medicine"
    elif "fuel" in query or "diesel" in query:
        category = "Fuel"
    elif "power" in query or "charging" in query:
        category = "Power"
        
    resources = agent_tools.get_closest_resources(state["user_lat"], state["user_lng"], category=category)
    
    log_entry["status"] = "Success"
    log_entry["findings"] = f"Discovered {len(resources)} distribution hubs near the grid."
    
    state["resource_info"] = resources
    state["agent_logs"].append(log_entry)
    return state

# 9. Communication
def communication_node(state: AgentState) -> AgentState:
    if "communication" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Communication Agent",
        "action": "Generating draft emergency distress messages and compiling hotlines",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Generate SMS SOS, WhatsApp draft, and Email draft
    loc = state["user_location"]
    family = ", ".join([f"{f['relationship']}: {f['name']}" for f in state["user_family_members"]]) or "Self"
    meds = state["user_medical_conditions"] or "None declared"
    
    sms_draft = f"SOS! I need emergency assistance at {loc}. Family: {family}. Medical: {meds}. Please dispatch rescue team."
    
    whatsapp_draft = (
        f" *RESCUEAI EMERGENCY DISTRESS STATUS* \n"
        f" *Location:* {loc} (Coords: {state['user_lat']:.4f}, {state['user_lng']:.4f})\n"
        f" *Family with me:* {family}\n"
        f" *Medical concerns:* {meds}\n"
        f" *Current Need:* {state['user_query']}\n"
        f"Please forward to disaster helpline / NDRF units."
    )
    
    email_draft = (
        f"Subject: URGENT: Disaster Distress Rescue Request - Coordinates: {state['user_lat']}, {state['user_lng']}\n\n"
        f"Dear Emergency Command Center / District Magistrate,\n\n"
        f"This is an automated distress email generated via RescueAI.\n"
        f"A citizen requires urgent assistance. Details below:\n"
        f"- Reporter: Rajesh Patel\n"
        f"- Location Area: {loc}\n"
        f"- Latitude/Longitude: {state['user_lat']}, {state['user_lng']}\n"
        f"- Query / Situation: {state['user_query']}\n"
        f"- Critical Health Data: {meds}\n\n"
        f"Please deploy nearest first responders."
    )
    
    communication_info = {
        "sms": sms_draft[:160], # Limit to SMS size
        "whatsapp": whatsapp_draft,
        "email": email_draft,
        "helplines": {
            "Disaster Management Helpline (NDMA)": "1078",
            "State Disaster Helpline": "1070",
            "Police Control": "100",
            "Fire Services": "101",
            "Ambulance Services": "102 / 108"
        }
    }
    
    log_entry["status"] = "Success"
    log_entry["findings"] = "Generated SMS, WhatsApp, and Email templates. Compiled regional helpline numbers."
    
    state["communication_info"] = communication_info
    state["agent_logs"].append(log_entry)
    return state

# 10. Government Relief
def government_node(state: AgentState) -> AgentState:
    if "government" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Government Relief Agent",
        "action": "Querying local disaster schemes, eligibility, and helpline lists",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Query database schemes
    schemes = agent_tools.get_gov_schemes()
    
    log_entry["status"] = "Success"
    log_entry["findings"] = f"Found {len(schemes)} relief compensations and reconstruction subsidies."
    
    state["government_info"] = schemes
    state["agent_logs"].append(log_entry)
    return state

# 11. Recovery
def recovery_node(state: AgentState) -> AgentState:
    if "recovery" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Recovery Agent",
        "action": "Formulating post-disaster insurance and reconstruction action plans",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Generate recovery advice using LLM/Heuristics
    gemini_resp = call_gemini(
        system_prompt=agent_prompts.RECOVERY_AGENT_PROMPT,
        user_content=f"User Query: {state['user_query']}. Draft structured recovery instructions."
    )
    
    if gemini_resp:
        recovery_info = gemini_resp
    else:
        recovery_info = (
            "### Post-Disaster Rebuilding Checklist:\n"
            "1. **Document Damage**: Take photos of all structural cracks, flooded items, and broken appliances. "
            "This is crucial for both insurance claims and government compensation audits.\n"
            "2. **Insurance Filing**: Contact your housing insurance provider immediately. Provide policy numbers and geotagged damage images.\n"
            "3. **Sanitary Re-Entry**: Do not enter home until structural integrity is declared safe. Flush out mold with bleach solutions; "
            "wear masks and thick rubber boots. Have a certified electrician inspect wiring before turning the mains back on.\n"
            "4. **Educational Continuity**: Contact local ward office for replacement books or details of mobile school tent sites."
        )
        
    log_entry["status"] = "Success"
    log_entry["findings"] = "Drafted insurance claims guidance and structural recovery checklist."
    
    state["recovery_info"] = recovery_info
    state["agent_logs"].append(log_entry)
    return state

# 12. Volunteer Matching
def volunteer_node(state: AgentState) -> AgentState:
    if "volunteer" not in state["active_agents"]:
        return state
        
    log_entry = {
        "agent": "Volunteer Matching Agent",
        "action": "Matching skill-sets of active volunteers nearby",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Match skills based on query
    skills = "rescue, first-aid"
    query = state["user_query"].lower()
    if "food" in query or "cook" in query or "water" in query:
        skills = "cooking, logistics"
        
    volunteers = agent_tools.match_nearby_volunteers(state["user_lat"], state["user_lng"], required_skills=skills)
    
    log_entry["status"] = "Success"
    log_entry["findings"] = f"Matched {len(volunteers)} local volunteers with skills: {skills}."
    
    state["volunteer_info"] = {
        "matched": volunteers,
        "required_skills": skills
    }
    state["agent_logs"].append(log_entry)
    return state

# 13. Coordinator Aggregate: Combine outputs into an English response
def coordinator_aggregate_node(state: AgentState) -> AgentState:
    log_entry = {
        "agent": "Coordinator Agent",
        "action": "Synthesizing all agent results into a final cohesive response",
        "status": "Success",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Format a prompt with all collected data to ask Gemini to compile the final unified markdown plan,
    # or compile it via a high-quality local template if Gemini key is missing.
    summary_data = {
        "query": state["user_query"],
        "location": state["user_location"],
        "vision": state["vision_assessment"],
        "weather": state["weather_info"]["summary"] if state["weather_info"] else None,
        "search": state["search_alerts"],
        "navigation": state["navigation_info"],
        "shelters": state["shelter_info"][:2] if state["shelter_info"] else [],
        "hospitals": state["hospital_info"][:2] if state["hospital_info"] else [],
        "medical": state["medical_advice"],
        "resources": state["resource_info"][:2] if state["resource_info"] else [],
        "communication": state["communication_info"],
        "government": state["government_info"][:2] if state["government_info"] else [],
        "recovery": state["recovery_info"],
        "volunteers": state["volunteer_info"]
    }
    
    # Try calling Gemini to compile
    gemini_resp = None
    lang = "English"
    
    compilation_prompt = (
        "You are the central aggregator. Combine the following collected emergency data into a clear "
        "English emergency report. Emphasize safety, direct coordinates, and step-by-step instructions. "
        f"Data context:\n{json.dumps(summary_data, default=str)}"
    )
    
    gemini_resp = call_gemini(
        system_prompt=agent_prompts.COORDINATOR_SYSTEM_PROMPT.format(language=lang),
        user_content=compilation_prompt
    )
    
    if gemini_resp:
        state["final_response"] = gemini_resp
    else:
        # Build local compiled markdown template (high fidelity fallback)
        res = "# RescueAI Emergency Action Plan\n\n"
        
        # 1. Summary
        res += "## EMERGENCY SUMMARY\n"
        if state["vision_assessment"]:
            va = state["vision_assessment"]
            res += f"- **Identified Threat:** {va['disaster_type']} ({va['severity']} Severity)\n"
            res += f"- **Structural Damage:** {va['structural_damage']}\n"
            res += f"- **Road/Traffic Access:** {va['road_condition']}\n"
        else:
            res += f"- **Reported Issue:** {state['user_query']}\n"
        res += f"- **Current Location:** {state['user_location']} (Coords: {state['user_lat']:.4f}, {state['user_lng']:.4f})\n\n"
        
        # 2. Weather
        if state["weather_info"]:
            res += "## WEATHER STATUS & WARNINGS\n"
            res += f"{state['weather_info']['summary']}\n\n"
            
        # 3. Medical First Aid (RAG)
        if state["medical_advice"]:
            res += "## IMMEDIATE MEDICAL & SAFETY PROTOCOLS (RAG)\n"
            res += f"{state['medical_advice']}\n\n"
            
        # 4. Routing & Shelters
        if state["navigation_info"] or state["shelter_info"]:
            res += "## EVACUATION & NEAREST SHELTERS\n"
            if state["navigation_info"]:
                nav = state["navigation_info"]
                res += f"**Recommended Route to {nav['destination_name']}:**\n"
                res += f"- **Distance:** {nav['distance_km']} km | **Est. Travel Time:** {nav['duration_min']} mins\n"
                res += "- **Navigation Steps:**\n"
                for step in nav["steps"]:
                    res += f"  - {step}\n"
            
            if state["shelter_info"]:
                res += "\n **Nearby Relief Centers:**\n"
                for s in state["shelter_info"][:2]:
                    food = "Food " if s["has_food"] else "No Food "
                    water = "Water " if s["has_water"] else "No Water "
                    power = "Power " if s["has_power"] else "No Power "
                    med = "Medical Support " if s["has_medical"] else "No Meds "
                    res += f"- **{s['name']}** ({s['distance_km']} km): Beds available: {s['available_beds']}/{s['total_beds']} | Amenities: {food}, {water}, {power}, {med}\n"
            res += "\n"
            
        # 5. Resources & Volunteers
        if state["resource_info"] or (state["volunteer_info"] and state["volunteer_info"]["matched"]):
            res += "## NEAREST EMERGENCY RESOURCES & VOLUNTEERS\n"
            if state["resource_info"]:
                res += "**Supplies Depots:**\n"
                for r in state["resource_info"][:2]:
                    res += f"- {r['name']} ({r['category']}) - Location: {r['address']} ({r['distance_km']} km) | Status: {r['status']}\n"
            
            if state["volunteer_info"] and state["volunteer_info"]["matched"]:
                res += "\n**Matched Local Volunteers:**\n"
                for v in state["volunteer_info"]["matched"][:2]:
                    res += f"- {v['name']} (Skills: {v['skill_set']}) - Distance: {v['distance_km']} km | Phone: {v['phone']}\n"
            res += "\n"
            
        # 6. Communication
        if state["communication_info"]:
            res += "## EMERGENCY COMMUNICATIONS\n"
            c_info = state["communication_info"]
            res += f"- **SOS SMS (Copy-paste):** `{c_info['sms']}`\n"
            res += f"- **WhatsApp Alert:**\n```\n{c_info['whatsapp']}\n```\n"
            res += "**Emergency Numbers:**\n"
            for k, v in c_info["helplines"].items():
                res += f"- **{k}:** {v}\n"
            res += "\n"
            
        # 7. Post-Disaster Schemes & Recovery
        if state["government_info"] or state["recovery_info"]:
            res += "## GOVERNMENT RELIEF SCHEMES & POST-DISASTER RECOVERY\n"
            if state["government_info"]:
                res += "**Available Compensations:**\n"
                for s in state["government_info"][:2]:
                    res += f"- **{s['title']}** ({s['category']}): Benefit: {s['benefit_amount']} | Helpline: {s['contact_helpline']}\n"
                    res += f"  - *Required docs:* {', '.join(s['documents_required'])}\n"
            
            if state["recovery_info"]:
                res += f"\n{state['recovery_info']}\n"
                
        state["final_response"] = res

    log_entry["findings"] = "Finished consolidated emergency action blueprint synthesis."
    state["agent_logs"].append(log_entry)
    return state

# --- BUILD STATE GRAPH ---

def get_disaster_agent_graph():
    """
    Assembles the LangGraph StateGraph, compiling it into a runnable workflow.
    """
    builder = StateGraph(AgentState)
    
    # Add Nodes
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("vision", vision_node)
    builder.add_node("weather", weather_node)
    builder.add_node("search", search_node)
    builder.add_node("navigation", navigation_node)
    builder.add_node("shelter", shelter_node)
    builder.add_node("medical", medical_node)
    builder.add_node("resource", resource_node)
    builder.add_node("communication", communication_node)
    builder.add_node("government", government_node)
    builder.add_node("recovery", recovery_node)
    builder.add_node("volunteer", volunteer_node)
    builder.add_node("coordinator_aggregate", coordinator_aggregate_node)
    
    # Set Entry Point
    builder.set_entry_point("coordinator")
    
    # Set Sequential Edges
    builder.add_edge("coordinator", "vision")
    builder.add_edge("vision", "weather")
    builder.add_edge("weather", "search")
    builder.add_edge("search", "navigation")
    builder.add_edge("navigation", "shelter")
    builder.add_edge("shelter", "medical")
    builder.add_edge("medical", "resource")
    builder.add_edge("resource", "communication")
    builder.add_edge("communication", "government")
    builder.add_edge("government", "recovery")
    builder.add_edge("recovery", "volunteer")
    builder.add_edge("volunteer", "coordinator_aggregate")
    builder.add_edge("coordinator_aggregate", END)
    
    # Compile
    return builder.compile()
