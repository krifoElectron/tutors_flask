import data
import json

json_data = {
    'goals': data.goals,
    'teachers': data.teachers,
    'bookings': [],
    'requests': []
}

with open('db.json', 'w') as db:
    json.dump(json_data, db, indent=4)
