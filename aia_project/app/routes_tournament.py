import datetime
from flask import Blueprint
from flask import render_template
from flask import request, redirect
from flask import current_app as app_cls
from markdown import Markdown
from pprint import pprint

import app.action.user
import app.action.tournament
from app.utils import FORM_TOURNAMENT_VALID, parser, DataError
from app.utils import is_anonymous, is_authenticated
from app.log import print

bp = Blueprint('tournament', __name__)


class ErrFormDate(Exception):
    pass


#####################################################################
@bp.context_processor
def utility_processor():
    def current_user():
        try:
            print("[AUTH]")
            auth_token = request.cookies.get('auth_token')
            return app.action.user.user_instance_from_token(
                app_cls, auth_token)
        except:
            return None

    return dict(current_user=current_user)


#####################################################################


@bp.route('/tournament_display/<idx>')
def tournament_display(idx):
    from app.cron import check_if_deadline_passed
    check_if_deadline_passed(app_cls.service)
    #############################################
    from app.models import Tournament
    tournament = (Tournament.query.filter(Tournament.id == idx).first())
    is_owner = False
    is_joined = False
    try:
        auth_token = request.cookies.get('auth_token')
        user = app.action.user.user_instance_from_token(app_cls, auth_token)
        if user.id == tournament.owner_id:
            is_owner = True
        from app.models import Tier
        already_joined = (Tier.query.filter(Tier.user_id == user.id).filter(
        Tier.tournament_id == tournament.id).first())
        if already_joined is not None:
            is_joined = True
    except:
        pass
    # @1 MARKDOWN
    mk = Markdown()
    html = mk.convert(tournament.readme)
    # @2 LOCATION
    location_geo = (0, 0)
    location_map = False
    if tournament.location:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="python")
        location = geolocator.geocode(tournament.location)
        if location:
            location_geo = (location.latitude, location.longitude)
            location_map = True

    # FIMXE: 404

    is_ladder = False
    if tournament.ladder:
        is_ladder = True

    js_teams = app.action.tournament.get_js_teams(app_cls, tournament)
    js_results = app.action.tournament.get_js_results(app_cls, tournament)

    return render_template('tournament_display.html',
                           tournament=tournament,
                           is_owner=is_owner,
                           is_joined=is_joined,
                           html=html,
                           location=location_geo,
                           location_map=location_map,
                           js_teams=js_teams,
                           js_results=js_results,
                           is_ladder=is_ladder)


@bp.route('/')
@bp.route('/index')
@bp.route('/tournament/<int:page>', methods=['GET'])
def tournament_page(page=1):
    per_page = 10
    from app.models import Tournament
    tournaments = Tournament.query.order_by(
        Tournament.date_created.desc()).paginate(page,
                                                 per_page,
                                                 error_out=False)
    return render_template('tournament_page.html', tournaments=tournaments)


@bp.route('/new_tournament', methods=['GET', 'POST'])
@is_authenticated
def tournament_new():
    errors = {}
    successes = {}
    FORM_ARGS = {
        'title': FORM_TOURNAMENT_VALID['title'],
        'max_users': FORM_TOURNAMENT_VALID['max_users'],
        'location': FORM_TOURNAMENT_VALID['location'],
        'readme': FORM_TOURNAMENT_VALID['readme'],
        'date_start': FORM_TOURNAMENT_VALID['date_start'],
        'date_deadline': FORM_TOURNAMENT_VALID['date_deadline'],
    }
    parsed_args = request.form.to_dict(flat=True)
    # print(request.form.to_dict(flat=True))
    if request.method == 'POST':
        try:
            auth_token = request.cookies.get('auth_token')
            user = app.action.user.user_instance_from_token(
                app_cls, auth_token)
            parsed_args = parser.parse(FORM_ARGS, location="form")
            parsed_args['user'] = user
            pprint(parsed_args)
            cur_date = datetime.datetime.utcnow()
            if parsed_args['date_deadline'] > parsed_args['date_start']:
                raise ErrFormDate
            if parsed_args['date_deadline'] < cur_date:
                raise ErrFormDate
            tournament = app.action.tournament.tournament_create(
                app_cls.service, parsed_args)
            successes = {"tournament": [f"The event was created."]}
        except DataError as e:
            errors = e.args[0]['form']
            print("ERROR", errors)
        except app.action.tournament.ErrDuplicate as e:
            print("ERROR", "duplicate")
            errors = {
                "tournament": ["This event already exists (with this title)."]
            }
        except ErrFormDate as e:
            print("ERROR", "date")
            errors = {
                "tournament": [
                    "Wrong datetime span (should be: current <= deadline <= start)."
                ]
            }
    return render_template('tournament_new.html',
                           errors=errors,
                           successes=successes,
                           parsed_args=parsed_args)


@bp.route('/edit_tournament/<idx>', methods=['GET', 'POST'])
@is_authenticated
def tournament_edit(idx):
    errors = {}
    successes = {}
    FORM_ARGS = {
        'title': FORM_TOURNAMENT_VALID['title'],
        'max_users': FORM_TOURNAMENT_VALID['max_users'],
        'location': FORM_TOURNAMENT_VALID['location'],
        'readme': FORM_TOURNAMENT_VALID['readme'],
        'date_start': FORM_TOURNAMENT_VALID['date_start'],
        'date_deadline': FORM_TOURNAMENT_VALID['date_deadline'],
    }
    from app.models import Tournament
    tournament = (Tournament.query.filter(Tournament.id == idx).first())
    parsed_args = tournament.__dict__
    # check if author is editing
    auth_token = request.cookies.get('auth_token')
    user = app.action.user.user_instance_from_token(app_cls, auth_token)
    if user.id != tournament.owner_id:
        return redirect(f"/tournament_display/{idx}")
    # if posted -> edit
    if request.method == 'POST':
        try:
            parsed_args = parser.parse(FORM_ARGS, location="form")
            parsed_args['user'] = user
            pprint(parsed_args)
            cur_date = datetime.datetime.utcnow()
            if parsed_args['date_deadline'] > parsed_args['date_start']:
                raise ErrFormDate
            if parsed_args['date_deadline'] < cur_date:
                raise ErrFormDate
            tournament = app.action.tournament.tournament_edit(
                app_cls.service, parsed_args, tournament)
            successes = {"tournament": [f"The event was edited."]}
        except DataError as e:
            errors = e.args[0]['form']
            print("ERROR", errors)
        except app.action.tournament.ErrDuplicate as e:
            print("ERROR", "duplicate")
            errors = {
                "tournament": ["This event already exists (with this title)."]
            }
        except ErrFormDate as e:
            print("ERROR", "date")
            errors = {
                "tournament": [
                    "Wrong datetime span (should be: current <= deadline <= start)."
                ]
            }
    return render_template('tournament_edit.html',
                           tournament=tournament,
                           errors=errors,
                           successes=successes,
                           parsed_args=parsed_args)


@bp.route('/join_tournament/<idx>', methods=['GET', 'POST'])
@is_authenticated
def tournament_join(idx):
    errors = {}
    successes = {}
    parsed_args = {}
    FORM_ARGS = {
        'license': FORM_TOURNAMENT_VALID['license'],
        'rating': FORM_TOURNAMENT_VALID['rating'],
    }
    from app.models import Tournament
    tournament = (Tournament.query.filter(Tournament.id == idx).first())

    auth_token = request.cookies.get('auth_token')
    user = app.action.user.user_instance_from_token(app_cls, auth_token)

    if request.method == 'POST':
        try:
            parsed_args = parser.parse(FORM_ARGS, location="form")
            parsed_args['user'] = user
            pprint(parsed_args)
            cur_date = datetime.datetime.utcnow()
            if tournament.date_deadline < cur_date:
                raise ErrFormDate
            app.action.tournament.tournament_join(
                app_cls.service, parsed_args, tournament, user)
            successes = {"tournament": [f"User joined the list."]}
        except DataError as e:
            errors = e.args[0]['form']
            print("ERROR", errors)
        except ErrFormDate as e:
            print("ERROR", "date")
            errors = {"tournament": ["Deadline passed."]}
        except app.action.tournament.ErrAlreadyJoined as e:
            print("ERROR", "already")
            errors = {
                "tournament": ["User already on the list."]
            }
    return render_template('tournament_join.html',
                           tournament=tournament,
                           errors=errors,
                           successes=successes,
                           parsed_args=parsed_args)

@bp.route('/unjoin_tournament/<idx>')
@is_authenticated
def tournament_unjoin(idx):
    from app.models import Tournament
    tournament = (Tournament.query.filter(Tournament.id == idx).first())

    auth_token = request.cookies.get('auth_token')
    user = app.action.user.user_instance_from_token(app_cls, auth_token)

    app.action.tournament.tournament_unjoin(app_cls.service, tournament, user)

    return redirect(f'/tournament_display/{tournament.id}')

@bp.route('/close_tournament/<idx>')
@is_authenticated
def tournament_close(idx):
    # FIXME: check if owner?

    from app.models import Tournament
    tournament = (Tournament.query.filter(Tournament.id == idx).first())

    auth_token = request.cookies.get('auth_token')
    user = app.action.user.user_instance_from_token(app_cls, auth_token)

    if user.id != tournament.owner_id:
        print("NOT OWNER!")
        return redirect(f'/tournament_display/{tournament.id}')

    app.action.tournament.tournament_close(app_cls.service, tournament, user,
            force=True)

    return redirect(f'/tournament_display/{tournament.id}')


@bp.route('/new_result/<idx>', methods=['GET', 'POST'])
@is_authenticated
def match_new(idx):
    from app.models import Match, User
    match = (Match.query.filter(Match.id == idx).first())

    from app.models import Tournament
    tournament = (Tournament.query.filter(Tournament.id == match.tournament_id).first())

    auth_token = request.cookies.get('auth_token')
    user = app.action.user.user_instance_from_token(app_cls, auth_token)
    ####################################################################

    errors = {}
    successes = {}
    FORM_ARGS = {
        'score_1': FORM_TOURNAMENT_VALID['score_1'],
        'score_2': FORM_TOURNAMENT_VALID['score_2'],
    }
    parsed_args = {}
    user_1 = None
    user_2 = None
    if match.user_id_1:
        _user = (User.query.filter(User.id == match.user_id_1).first())
        user_1 = _user
    if match.user_id_2:
        _user = (User.query.filter(User.id == match.user_id_2).first())
        user_2 = _user
    if user.id not in [match.user_id_1, match.user_id_2]:
        return redirect(f'/tournament_display/{tournament.id}')
    
    #####
    # fixme unpack score for user!
    results_by_user = None
    if user.id is match.user_id_1:
        results_by_user = match.results_by_user_id_1
    if user.id is match.user_id_2:
        results_by_user = match.results_by_user_id_2
    if results_by_user:
        parsed_args['score_1'], parsed_args['score_2'] = map(int, results_by_user.split("@"))

    if request.method == 'POST':
        try:
            parsed_args = parser.parse(FORM_ARGS, location="form")
            pprint(parsed_args)
            results_by_user = str(parsed_args['score_1'])+"@"+str(parsed_args['score_2'])
            ###########################################
            if user.id is match.user_id_1:
                match.results_by_user_id_1 = results_by_user
            if user.id is match.user_id_2:
                match.results_by_user_id_2 = results_by_user
            if match.results_by_user_id_1 == match.results_by_user_id_2:
                match.results = match.results_by_user_id_1
                # FIXME: set winner WHO IS
                winner_id = None
                loser_id = None
                if parsed_args['score_1'] > parsed_args['score_2']:
                    winner_id = match.user_id_1
                    loser_id = match.user_id_2
                else:
                    winner_id = match.user_id_2
                    loser_id = match.user_id_1
                if match.next_match_id:
                    match_next = (Match.query.filter(Match.tournament_id == match.tournament_id).filter(Match.match_id == match.next_match_id).first())
                    if match.match_id % 2 == 1:
                        match_next.user_id_1 = winner_id
                    else:
                        match_next.user_id_2 = winner_id
                    if match_next.flag == 1: # FIXME: for 3th place
                        match_next_losers = \
                        (Match.query.filter(Match.tournament_id ==
                            match.tournament_id).filter(Match.match_id ==
                                match_next.next_match_id).first())
                        if match.match_id % 2 == 1:
                            match_next_losers.user_id_1 = loser_id
                        else:
                            match_next_losers.user_id_2 = loser_id



            app_cls.service.db.session.commit()
            ###########################################
            successes = {"match": [f"The score was recorded."]}
        except DataError as e:
            errors = e.args[0]['form']
            print("ERROR", errors)

    """
    results = db.Column(db.Text)
    results_by_user_id_1 = db.Column(db.Text)
    results_by_user_id_2 = db.Column(db.Text)

    #return redirect(f'/tournament_display/{tournament.id}')
    """

    return render_template('match_new.html',
                           match=match,
                           tournament=tournament,
                           user_1=user_1,
                           user_2=user_2,
                           errors=errors,
                           successes=successes,
                           parsed_args=parsed_args)

@bp.route('/search')
def search():
    query = request.args.get('query')
    print("QUERY", query)

    from app.models import Tournament

    obj = Tournament.query
    obj = obj.filter(Tournament.title.like('%' + query + '%'))
    obj = obj.order_by(Tournament.title).all()

    return render_template('search.html', query=query, tournaments=obj)
