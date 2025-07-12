import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("YourserviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "YourDataBaseURL",
})

ref = db.reference("Students")

data={
    "452331":{
        "name": "Aditya",
        "branch": "CSE-AI",
        "year": "2nd",
        "section": "A",
        "attendance": 4,
        "yearOfJoining": "2022",
        "last_attendance": "2025-07-01 09:00:00",
    },
     "896575":{
        "name": "Aryan",
        "branch": "CSE",
        "year": "1st",
        "section": "A",
        "attendance": 3,
        "yearOfJoining": "2024",
        "last_attendance": "2025-07-01 09:00:00",
    },
    "963852":{
        "name": "Priyanshu Shukla",
        "branch": "mechanical",
        "year": "2nd",
        "section": "B",
        "attendance": 10,
        "yearOfJoining": "2022",
        "last_attendance": "2025-07-01 09:00:00",    
    }  
}

for key, value in data.items():
    ref.child(key).set(value)