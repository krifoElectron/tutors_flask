import data
import json

from app import db, Tutor, Goal


def seed_db():
    goal_entities_dict = {}
    for goal_name, goal_display_name in data.goals.items():
        goal_entity = Goal(name=goal_name, display_name=goal_display_name)
        db.session.add(goal_entity)
        goal_entities_dict[goal_name] = goal_entity

    for tutor in data.teachers:
        tutor_entity = Tutor(name=tutor['name'],
                             about=tutor['about'],
                             rating=tutor['rating'],
                             picture=tutor['picture'],
                             price=tutor['price'],
                             free=json.dumps(tutor['free']))

        for goal in tutor['goals']:
            tutor_entity.goals.append(goal_entities_dict[goal])

        db.session.add(tutor_entity)

    db.session.commit()


if __name__ == '__main__':
    seed_db()
