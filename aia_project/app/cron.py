import datetime
import app.action.tournament
from app.models import Tournament, User

def check_if_deadline_passed(service):
    print("------> CHECK <------")

    tournaments = (Tournament.query.all())
    current_date = datetime.datetime.utcnow()
    for tournament in tournaments:
        if tournament.date_deadline < current_date:
            print("-------------> PASSED")
            user = (User.query.filter(User.id == tournament.owner_id).first())
            app.action.tournament.tournament_close(service, tournament, user)
