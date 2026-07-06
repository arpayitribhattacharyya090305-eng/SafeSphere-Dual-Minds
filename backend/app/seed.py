from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.database_models import User, Shelter, Hospital, Resource, Volunteer, GovernmentScheme, WeatherAlert
from backend.app.core.security import get_password_hash
from datetime import datetime

def seed_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    db = SessionLocal()
    try:
        # Check if database is already seeded
        if db.query(User).first() is not None:
            print("Database already seeded. Skipping...")
            return

        print("Seeding database...")

        # 1. Seed Users
        admin_user = User(
            email="admin@safesphere.org",
            password_hash=get_password_hash("admin123"),
            full_name="SafeSphere Command Center Admin",
            role="admin",
            location_address="Bandra West, Mumbai, Maharashtra",
            location_lat=19.0596,
            location_lng=72.8295,
            preferred_language="English"
        )
        citizen_user = User(
            email="citizen@safesphere.org",
            password_hash=get_password_hash("citizen123"),
            full_name="Rajesh Patel",
            role="citizen",
            location_address="Dharavi, Mumbai, Maharashtra",
            location_lat=19.0380,
            location_lng=72.8538,
            preferred_language="English",
            family_members=[
                {"name": "Kiran Patel", "relationship": "Spouse", "age": 38},
                {"name": "Aarav Patel", "relationship": "Son", "age": 12}
            ],
            medical_conditions="Asthma, High Blood Pressure",
            emergency_contacts=[
                {"name": "Sanjay Patel", "relationship": "Brother", "phone": "+91 98765 43210"}
            ]
        )
        db.add(admin_user)
        db.add(citizen_user)

        # 2. Seed Shelters
        shelters = [
            Shelter(
                name="Dharavi Sports Complex Shelter",
                address="Dharavi Cross Road, Dharavi, Mumbai, Maharashtra",
                location_lat=19.0392,
                location_lng=72.8520,
                contact_number="+91 22 2407 1234",
                total_beds=200,
                available_beds=142,
                has_food=True,
                has_water=True,
                has_medical=True,
                has_power=True
            ),
            Shelter(
                name="Chembur Municipal School Relief Camp",
                address="Sion Trombay Road, Chembur, Mumbai, Maharashtra",
                location_lat=19.0618,
                location_lng=72.8988,
                contact_number="+91 22 2522 5678",
                total_beds=100,
                available_beds=85,
                has_food=True,
                has_water=True,
                has_medical=False,
                has_power=True
            ),
            Shelter(
                name="Chennai Central Community Hall",
                address="Sydenhams Road, Periamet, Chennai, Tamil Nadu",
                location_lat=13.0835,
                location_lng=80.2720,
                contact_number="+91 44 2538 4321",
                total_beds=300,
                available_beds=210,
                has_food=True,
                has_water=True,
                has_medical=True,
                has_power=False
            ),
            Shelter(
                name="Adyar Flood Relief Center",
                address="Adyar Bridge Road, Adyar, Chennai, Tamil Nadu",
                location_lat=13.0063,
                location_lng=80.2520,
                contact_number="+91 44 2445 8765",
                total_beds=150,
                available_beds=120,
                has_food=True,
                has_water=True,
                has_medical=True,
                has_power=True
            )
        ]
        db.add_all(shelters)

        # 3. Seed Hospitals
        hospitals = [
            Hospital(
                name="King Edward Memorial (KEM) Hospital",
                address="Acharya Donde Marg, Parel, Mumbai, Maharashtra",
                location_lat=19.0025,
                location_lng=72.8420,
                contact_number="+91 22 2410 7000",
                total_beds=1800,
                available_beds=340,
                emergency_services=True
            ),
            Hospital(
                name="Lokmanya Tilak Municipal General (Sion) Hospital",
                address="Sion Hospital Road, Sion, Mumbai, Maharashtra",
                location_lat=19.0360,
                location_lng=72.8600,
                contact_number="+91 22 2407 6381",
                total_beds=1400,
                available_beds=180,
                emergency_services=True
            ),
            Hospital(
                name="Apollo Hospital Greams Road",
                address="21, Greams Lane, Off Greams Road, Chennai, Tamil Nadu",
                location_lat=13.0602,
                location_lng=80.2515,
                contact_number="+91 44 2829 0200",
                total_beds=560,
                available_beds=95,
                emergency_services=True
            ),
            Hospital(
                name="Rajiv Gandhi Government General Hospital",
                address="Poonamallee High Road, Chennai, Tamil Nadu",
                location_lat=13.0815,
                location_lng=80.2745,
                contact_number="+91 44 2530 5000",
                total_beds=2700,
                available_beds=410,
                emergency_services=True
            )
        ]
        db.add_all(hospitals)

        # 4. Seed Resources
        resources = [
            # Mumbai Resources
            Resource(
                name="Mineral Water Boxes (24pk)",
                category="Water",
                quantity=450.0,
                unit="boxes",
                location_lat=19.0392,
                location_lng=72.8520,
                address="Dharavi Sports Complex, Mumbai",
                contact_number="+91 99999 11111",
                status="Available"
            ),
            Resource(
                name="First Aid Kits",
                category="Medicine",
                quantity=120.0,
                unit="kits",
                location_lat=19.0392,
                location_lng=72.8520,
                address="Dharavi Sports Complex, Mumbai",
                contact_number="+91 99999 11111",
                status="Available"
            ),
            Resource(
                name="Dry Food Packets (MTR)",
                category="Food",
                quantity=1200.0,
                unit="packets",
                location_lat=19.0618,
                location_lng=72.8988,
                address="Chembur Municipal School, Mumbai",
                contact_number="+91 99999 22222",
                status="Available"
            ),
            Resource(
                name="Diesel Fuel Generator Stock",
                category="Fuel",
                quantity=350.0,
                unit="liters",
                location_lat=19.0618,
                location_lng=72.8988,
                address="Chembur Municipal School, Mumbai",
                contact_number="+91 99999 22222",
                status="Available"
            ),
            # Chennai Resources
            Resource(
                name="Emergency Medicine Supplies",
                category="Medicine",
                quantity=80.0,
                unit="kits",
                location_lat=13.0835,
                location_lng=80.2720,
                address="Chennai Central Community Hall",
                contact_number="+91 99999 33333",
                status="Available"
            ),
            Resource(
                name="Solar Battery Power Bank",
                category="Power",
                quantity=40.0,
                unit="units",
                location_lat=13.0063,
                location_lng=80.2520,
                address="Adyar Flood Relief Center",
                contact_number="+91 99999 44444",
                status="Available"
            )
        ]
        db.add_all(resources)

        # 5. Seed Volunteers
        volunteers = [
            Volunteer(
                name="Amit Sharma",
                skill_set="first-aid, medical, CPR",
                phone="+91 98111 22222",
                email="amit.sharma@gmail.com",
                status="Available",
                location_lat=19.0410,
                location_lng=72.8620,
                address="Sion East, Mumbai"
            ),
            Volunteer(
                name="Priya Patel",
                skill_set="rescue, navigation, driving",
                phone="+91 98222 33333",
                email="priya.patel@yahoo.com",
                status="Available",
                location_lat=19.0520,
                location_lng=72.8340,
                address="Bandra East, Mumbai"
            ),
            Volunteer(
                name="Suresh Kumar",
                skill_set="cooking, logistics, supply-chain",
                phone="+91 98333 44444",
                email="suresh.k@gmail.com",
                status="Available",
                location_lat=13.0720,
                location_lng=80.2600,
                address="Egmore, Chennai"
            ),
            Volunteer(
                name="Rajesh Iyer",
                skill_set="translation, counseling, admin",
                phone="+91 98444 55555",
                email="rajesh.iyer@outlook.com",
                status="Available",
                location_lat=13.0110,
                location_lng=80.2440,
                address="Kotturpuram, Chennai"
            )
        ]
        db.add_all(volunteers)

        # 6. Seed Government Schemes
        schemes = [
            GovernmentScheme(
                title="NDRF Ex-Gratia Relief Compensation",
                description="Financial compensation provided by the National Disaster Response Fund to the families affected by natural disasters, including loss of life, injury, or severe crop/property damage.",
                category="Compensation",
                eligibility_criteria="Resident of a declared disaster-affected region who has suffered structural damage, injury, or loss of an immediate family member.",
                benefit_amount="Rs. 4,000,000 for loss of life; Rs. 250,000 for permanent disability; Rs. 95,100 for severe house damage.",
                contact_helpline="1070 / 1078 (NDMA Helpline)",
                documents_required=["Disaster Damage Certificate from Local Tehsildar", "Aadhaar Card", "Bank Account Details", "Death Certificate / Medical Report (if applicable)"]
            ),
            GovernmentScheme(
                title="PM National Relief Fund (PMNRF) Medical Aid",
                description="Medical assistance grant provided directly to citizens affected by natural disasters like floods, cyclones, or earthquakes, covering hospital surgical treatments and critical injuries.",
                category="Medical Aid",
                eligibility_criteria="Victims of natural disasters undergoing treatment in government or empaneled private hospitals.",
                benefit_amount="Up to Rs. 200,000 direct hospital cost coverage.",
                contact_helpline="011-23014020 (PMO Relief Wing)",
                documents_required=["Aadhaar Card", "Hospital Admission Slip", "Estimated Treatment Cost Bill", "Disaster Victim Card / Ration Card"]
            ),
            GovernmentScheme(
                title="SDRF House Reconstruction Subsidy",
                description="State Disaster Response Fund housing grant to assist disaster victims in reconstructing completely damaged or washed-away homes in rural and urban areas.",
                category="Housing",
                eligibility_criteria="Owner of a residential property destroyed by flood, cyclone, landslide, or earthquake, verified by the local revenue authority.",
                benefit_amount="Rs. 95,100 per house in hilly areas; Rs. 70,000 in plains; Rs. 15,000 for partially damaged structures.",
                contact_helpline="108 (State Disaster Helpline)",
                documents_required=["Land Ownership Documents", "Geotagged Photo of Destroyed House", "Aadhaar Card", "Verification Form signed by Tehsildar"]
            )
        ]
        db.add_all(schemes)

        # 7. Seed Weather Alerts (initial state)
        alerts = [
            WeatherAlert(
                city="Mumbai",
                alert_type="Rain",
                severity="Severe",
                description="Extremely heavy rainfall expected over the next 48 hours. Risk of localized flooding in low-lying areas. Citizens are advised to stay indoors.",
                forecast_date=datetime.utcnow()
            ),
            WeatherAlert(
                city="Chennai",
                alert_type="Cyclone",
                severity="Extreme",
                description="Cyclone alert issued for coastal regions. Wind speeds reaching 90-100 km/h. Sea waves up to 2 meters. Evacuations in progress for fishermen.",
                forecast_date=datetime.utcnow()
            )
        ]
        db.add_all(alerts)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
