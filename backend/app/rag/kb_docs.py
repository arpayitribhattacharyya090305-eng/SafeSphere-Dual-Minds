# Knowledge Base Documents for RAG
# Source: WHO, Red Cross, and Indian NDMA Guidelines

DOCUMENTS = [
    # --- MEDICAL FIRST AID GUIDELINES ---
    {
        "id": "med_cpr",
        "title": "Cardiopulmonary Resuscitation (CPR) First Aid Protocol",
        "category": "Medical",
        "content": (
            "Cardiopulmonary Resuscitation (CPR) is a life-saving procedure performed when a person's breathing "
            "or heartbeat has stopped. Follow these steps:\n"
            "1. Verify safety of the scene. Tap the person's shoulder and ask loudly: 'Are you okay?'\n"
            "2. Shout for nearby help and dial the local emergency line (e.g., 102 or 112 in India).\n"
            "3. Check for breathing: Look at the chest for 5-10 seconds to see if it rises.\n"
            "4. Start Chest Compressions: Place the heel of one hand in the center of the chest (lower half of sternum), "
            "and the other hand on top. Push hard and fast at a rate of 100-120 compressions per minute, "
            "depressing the chest at least 2 inches (5 cm). Allow chest to recoil completely between compressions.\n"
            "5. Rescue Breaths: If trained, tilt the head back, lift the chin, pinch the nose, and give 2 rescue breaths "
            "after every 30 compressions (30:2 ratio). If untrained, perform Hands-Only CPR (continuous compressions)."
        )
    },
    {
        "id": "med_burns",
        "title": "Emergency Burn Care and Management",
        "category": "Medical",
        "content": (
            "Thermal, electrical, or chemical burns require immediate classification and care:\n"
            "1. First-Degree (Superficial): Red, dry, and painful. Cool immediately under cold running water for "
            "at least 10-20 minutes. Do NOT apply ice directly, butter, oil, or toothpastes.\n"
            "2. Second-Degree (Partial Thickness): Blisters, redness, intense swelling, and severe pain. Clean "
            "gently, do NOT pop blisters. Cover loosely with a sterile, non-stick bandage.\n"
            "3. Third-Degree (Full Thickness): Charred, white or leathery skin, often painless due to destroyed nerves. "
            "Call emergency services immediately. Ensure the victim is breathing. Cover the burned area with a clean, "
            "damp sterile sheet. Do not immerse in cold water. Elevate burned limbs above heart level.\n"
            "4. Chemical Burns: Flush with running water for 20+ minutes and remove contaminated clothing."
        )
    },
    {
        "id": "med_fractures",
        "title": "First Aid for Bone Fractures and Joint Dislocations",
        "category": "Medical",
        "content": (
            "Suspect a fracture if a limb is deformed, swollen, bruised, or extremely painful to move:\n"
            "1. Do NOT try to realign or push back a bone that is sticking out (compound fracture).\n"
            "2. Control Bleeding: Apply pressure around the wound with a clean cloth. Do not apply pressure directly "
            "on the protruding bone.\n"
            "3. Immobilize the Injured Area: Apply a splint using rigid materials (boards, rolled newspapers) placed "
            "above and below the joint. Secure with bandages without cutting off blood circulation.\n"
            "4. Apply Cold Packs: Wrap ice in a towel and apply to the swollen area for 15-20 minutes to reduce pain.\n"
            "5. Prevent Shock: Lay the person flat, elevate feet 12 inches if no spine injury is suspected, and cover "
            "with a blanket. Keep them still."
        )
    },
    {
        "id": "med_snakebites",
        "title": "NDMA Snakebite and Venom Treatment Protocol",
        "category": "Medical",
        "content": (
            "Snakebites require urgent care. Symptoms include puncture marks, swelling, pain, difficulty breathing, "
            "and weakness. Follow these rules:\n"
            "1. Keep the victim calm and still. Movement spreads the venom faster in the bloodstream.\n"
            "2. Immobilize the bitten limb using a splint or bandage. Keep the limb at or slightly below heart level.\n"
            "3. Remove tight clothing, rings, or shoes from the limb as swelling will occur.\n"
            "4. Do NOT use a tourniquet or tight band. Do NOT cut the wound or try to suck out the venom.\n"
            "5. Do NOT apply ice or chemicals. Do NOT give alcohol, caffeinated drinks, or pain relief medications "
            "like aspirin.\n"
            "6. Transport the victim immediately to the nearest hospital stocking Anti-Snake Venom (ASV). Note the "
            "snake's color or pattern if possible without danger."
        )
    },
    {
        "id": "med_poisoning",
        "title": "Emergency Poisoning and Chemical Ingestion First Aid",
        "category": "Medical",
        "content": (
            "If a person has ingested, inhaled, or touched a toxic substance:\n"
            "1. Swallowed Poison: If the person is conscious, ask what was swallowed. Do NOT induce vomiting "
            "unless explicitly instructed by a doctor or poison control center, especially if it was a corrosive "
            "substance (bleach, acid, petrol) which will burn the throat again upon vomiting.\n"
            "2. Inhaled Poison: Move the person into fresh air immediately. If breathing stops, start CPR.\n"
            "3. Poison on Skin/Eyes: Remove contaminated clothing. Flush skin or eyes with clean running water "
            "for at least 15-20 minutes.\n"
            "4. Keep the container or label of the ingested substance to show medical personnel.\n"
            "5. Contact the National Poison Information Centre (India helpline: 011-26593677 or 1800-116-117)."
        )
    },
    {
        "id": "med_mentalhealth",
        "title": "Psychological First Aid (PFA) and Mental Health Support",
        "category": "Medical",
        "content": (
            "Disasters cause intense trauma and anxiety. Use Psychological First Aid (PFA) to support survivors:\n"
            "1. Look: Check for safety, check for people with obvious urgent basic needs, and check for people "
            "showing severe distress reactions.\n"
            "2. Listen: Approach people who may need support. Ask about their needs and concerns. Listen "
            "attentively, do NOT pressure them to talk, and validate their feelings.\n"
            "3. Link: Help people address basic needs (food, water, shelter, medical). Link them with loved ones "
            "and emergency services. Provide clear, accurate information on relief schemes.\n"
            "4. Breathing Exercise for Panic: Instruct the survivor to breathe in slowly through the nose "
            "for 4 seconds, hold for 4 seconds, and exhale slowly through the mouth for 6 seconds."
        )
    },

    # --- DISASTER SAFETY PROTOCOLS ---
    {
        "id": "dis_flood",
        "title": "NDMA Flood Emergency Safety and Evacuation Guidelines",
        "category": "Flood",
        "content": (
            "Before and during floods, follow these NDMA safety guidelines:\n"
            "1. Monitor local news, weather radio, and emergency cell alerts for flash flood warnings.\n"
            "2. Turn off the main electrical switch and gas valve before evacuating. Do not touch electrical "
            "equipment if you are wet or standing in water.\n"
            "3. Pack an Emergency Go-Bag: include dry food, water, flashlight, batteries, first-aid kit, medication, "
            "Aadhaar card, and cash.\n"
            "4. Evacuation: Move to higher ground immediately. Do NOT drive or walk through flood waters. "
            "Just 6 inches of moving water can knock you down, and 2 feet of water can sweep a car away ('Turn Around, Don't Drown').\n"
            "5. Post-Flood Safety: Do not drink tap water until declared safe. Watch out for snakes or electrical wires in standing water."
        )
    },
    {
        "id": "dis_fire",
        "title": "Fire Hazard Emergency Safety Protocols",
        "category": "Fire",
        "content": (
            "If caught in a building fire, act quickly:\n"
            "1. Sound the alarm and shout 'Fire!'. Call the local fire brigade (101 in India).\n"
            "2. Escape Route: If the room fills with smoke, stay low to the floor. Crawl on hands and knees "
            "where air is cleaner. Test door handles with the back of your hand before opening. If hot, do NOT open; "
            "use an alternative exit.\n"
            "3. If trapped, close all doors between you and the fire. Stuff wet sheets or towels in cracks "
            "around the door to block smoke. Wave a bright cloth at windows to signal rescuers.\n"
            "4. If clothes catch fire: STOP, DROP to the ground, cover your face with hands, and ROLL back and "
            "forth until the flames are smothered.\n"
            "5. Do NOT use elevators under any circumstances. Always use stairwells."
        )
    },
    {
        "id": "dis_earthquake",
        "title": "NDMA Earthquake Survival Guidelines",
        "category": "Earthquake",
        "content": (
            "Earthquakes occur without warning. Follow these guidelines during tremors:\n"
            "1. Indoors: Practice DROP, COVER, and HOLD ON. Drop to your hands and knees. Cover your head "
            "and neck under a sturdy table or desk. Hold onto the table leg until shaking stops. Keep away from "
            "windows, glass, brick walls, and heavy hanging objects.\n"
            "2. Outdoors: Move to an open area away from buildings, streetlights, utility wires, and trees. "
            "Drop to the ground and cover your head.\n"
            "3. Inside a vehicle: Pull over safely to an open area. Stop, set the parking brake, and remain "
            "inside the vehicle. Avoid bridges, overpasses, and power cables.\n"
            "4. Post-Shaking: Check for gas leaks or electrical short circuits before using matches. Expect aftershocks."
        )
    },
    {
        "id": "dis_cyclone",
        "title": "NDMA Cyclone and Severe Storm Preparedness",
        "category": "Cyclone",
        "content": (
            "When a cyclone alert is issued for your area:\n"
            "1. Secure your home: Close shutters, board up glass windows, trim dead branches from trees, and "
            "bring loose outdoor items indoors.\n"
            "2. Evacuate if ordered by local officials, or if living in a low-lying coastal area, thatched house, "
            "or temporary structure. Head to designated high-ground concrete cyclone shelters.\n"
            "3. Keep all windows and doors closed on the side facing the wind, and open slightly on the opposite side "
            "to balance air pressure.\n"
            "4. Do NOT go outdoors even during the calm 'eye' of the storm, as winds will restart violently from "
            "the opposite direction.\n"
            "5. Avoid contact with downed power lines. Boil all drinking water to prevent waterborne disease outbreaks."
        )
    }
]
