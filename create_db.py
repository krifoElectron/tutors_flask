import data
import json
from app import db
from app import Tutor

db.create_all()

for tutor in data.teachers:
    tutor_entity = Tutor(name=tutor['name'],
                         about=tutor['about'],
                         rating=tutor['rating'],
                         picture=tutor['picture'],
                         price=tutor['price'],
                         goals=json.dumps(tutor['goals']),
                         free=json.dumps(tutor['free']))
    db.session.add(tutor_entity)

db.session.commit()
