print("[TOURNAMENT]")

import math
import random
import datetime
from app.models import Tournament, Tier, Match
from pprint import pprint
from app.log import print


class ErrFatal(Exception):
    pass


class ErrDuplicate(Exception):
    pass


class ErrAlreadyJoined(Exception):
    pass


# FIXME: remove user from data['user']
def tournament_create(s, data):
    try:
        user = data['user']
        print(user)
        print(s)
        tournament = Tournament(
            title=data['title'],
            date_start=data['date_start'],
            date_deadline=data['date_deadline'],
            location=data['location'],
            max_users=data['max_users'],
            readme=data['readme'],
            owner_id=user.id,
        )

        s.db.session.add(tournament)
        s.db.session.commit()
    except Exception as e:
        print(str(e))
        if "UNIQUE constraint failed" in str(e):
            raise ErrDuplicate()
        raise ErrFatal()
    return tournament


def tournament_edit(s, data, tournament):
    tournament.title = data['title']
    tournament.date_start = data['date_start']
    tournament.date_deadline = data['date_deadline']
    tournament.location = data['location']
    tournament.max_users = data['max_users']
    tournament.readme = data['readme']
    s.db.session.commit()
    return tournament


def tournament_join(s, data, tournament, user):
    if tournament.ladder:
        print("LADDER!!!!")
        return False
    already_joined = (Tier.query.filter(Tier.user_id == user.id).filter(
        Tier.tournament_id == tournament.id).first())
    if already_joined is not None:
        raise ErrAlreadyJoined()

    tier = Tier(user_id=user.id,
                tournament_id=tournament.id,
                license=data['license'],
                rating=data['rating'])
    tournament.tiers.append(tier)
    s.db.session.commit()

def tournament_unjoin(s, tournament, user):
    if tournament.ladder:
        print("LADDER!!!!")
        return False
    already_joined = (Tier.query.filter(Tier.user_id == user.id).filter(
        Tier.tournament_id == tournament.id).delete())
    if already_joined is not None:
        print("UNJOINED!")
        s.db.session.commit()
    else:
        print("NO NEED")


# FIXME: add tournament delete!!!!

def tournament_close(s, tournament, user):
    tiers = tournament.tiers.limit(tournament.max_users).all()
    # FIXME: order users by rating

    def compare(x, y):
        return x.rating - y.rating

    from functools import cmp_to_key
    tiers = sorted(tiers, key=cmp_to_key(compare), reverse=True)

    teams = []
    results = []

    max_users = tournament.max_users
    if max_users <= 1:
        tree_n = 2**1
    else:
        tree_n = 2**math.ceil(math.log2(len(tiers)))

    print("---------->", tiers)
    print("!"*100)

    tiers_n = len(tiers)
    for i in range(0, tree_n, 2):
        print(f"PAIR ---> {i}")
        tier_1 = None
        tier_2 = None
        if i < tiers_n:
            tier_1 = tiers[i].user_id
        if i + 1 < tiers_n:
            tier_2 = tiers[i + 1].user_id
        print(f"tier 1 -> {tier_1}")
        print(f"tier 2 -> {tier_2}")
        print()

        teams.append([tier_1, tier_2])

    pprint(teams)

    store_matches = []

    def _create_match(tournament_id, match_id, next_match_id, flag=0):
        print("======= MATCH ========")
        print(f"tournament_id = {tournament_id}")
        print(f"match_id = {match_id} --> {next_match_id}")
        print(f"flag = {flag}")
        match = Match(
            match_id = match_id,
            tournament_id = tournament_id,
            next_match_id = next_match_id,
            flag = flag,
        )

        """
        user_id_1 = db.Column(db.Integer, db.ForeignKey('user.id'))
        user_id_2 = db.Column(db.Integer, db.ForeignKey('user.id'))

        results = db.Column(db.Text)
        results_by_user_id_1 = db.Column(db.Text)
        results_by_user_id_2 = db.Column(db.Text)
        """
        print("======================")
        return match

    match_id = 1
    matches_n_cul = 0
    for level in range(int(math.log2(tree_n))):
        matches = []
        matches_n = int((tree_n / 2) / (2**level))
        print(f"\033[91m===== {level} | {matches_n} =====\033[0m")
        for j in range(matches_n):
            matches.append(match_id)
            if match_id % 2 == 1:
                next_match_id = ((match_id - matches_n_cul + 1) // 2) \
                        + matches_n_cul + matches_n
            else:
                next_match_id = ((match_id - matches_n_cul + 0) // 2) \
                        + matches_n_cul + matches_n
            # print(f">>> {match_id} --> {next_match_id}")
            match = _create_match(tournament.id,
                                  match_id,
                                  next_match_id,
                                  flag=int(matches_n == 1))
            if level == 0:
                print("ASSIGN", j, teams[j])
                match.user_id_1 = teams[j][0]
                match.user_id_2 = teams[j][1]
            store_matches.append(match)
            match_id += 1
        if matches_n == 1:
            print("3MATCH")
            matches.append(match_id)
            match = _create_match(tournament.id, match_id, None, flag=2)
            store_matches.append(match)
            match_id += 1
        results.append(matches)
        matches_n_cul += matches_n

    pprint(results)

    import json
    print("------------")
    ladder_txt = json.dumps({"teams": teams, "results": results})
    pprint(ladder_txt)
    print("------------")

    tournament.date_deadline = datetime.datetime.utcnow()
    tournament.ladder = ladder_txt
    tournament.matches = []
    for match in store_matches:
        tournament.matches.append(match)

    # XXX: find wildcards
    cached_ids = []
    while 1:
        push_i = 0
        for match in store_matches:
            push_user = None

            if (match.user_id_2 is None and match.user_id_1 is not None and
                    match.id not in cached_ids):
                push_user = match.user_id_1
                cached_ids.append(match.id)
            if (match.user_id_1 is None and match.user_id_2 is not None and
                    match.id not in cached_ids):
                push_user = match.user_id_2
                cached_ids.append(match.id)
 
            if push_user and match.next_match_id:
                match_next = (Match.query.filter(Match.tournament_id == match.tournament_id).filter(Match.match_id == match.next_match_id).first())
                if match.match_id % 2 == 1:
                    match_next.user_id_1 = push_user
                else:
                    match_next.user_id_2 = push_user
                push_i = 1
                print(f"{match} ==============================> PUSH")
        s.db.session.commit()
        print()
        if push_i == 0:
            break

    s.db.session.commit()

    #         --> ALWAYS
    # FIXME: change deadline if manually clicked!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # FIXME: ignore matches if null, null
    # FIXME: get from match_id and tournamnt_id --> Match --> [null, null]

from app.models import User

def get_js_teams(s, tournament):
    if tournament.get_ladder()['teams'] is None:
        return str([])
    # print(tournament.get_ladder()['teams'])
    teams = []
    for u1, u2 in tournament.get_ladder()['teams']:
        pair = [None, None]
        if u1:
            user = (User.query.filter(User.id == u1).first())
            pair[0] = user.name
        if u2:
            user = (User.query.filter(User.id == u2).first())
            pair[1] = user.name
        teams.append(pair)
    return str(teams).replace("None", "null")

def get_js_results(s, tournament):
    if tournament.get_ladder()['results'] is None:
        return str([])
    # print(tournament.get_ladder()['results'])
    results = []
    for layer in tournament.get_ladder()['results']:
        layer_results = []
        for match_id in layer:
            score = [None, None]
            print(match_id)
            match = (Match.query.filter(Match.match_id ==
                match_id).filter(Match.tournament_id == tournament.id).first())
            # FIXME -----------------------------------------------------
            # jak to bedzie?????????????????????????????????????????????
            if match.results:
                score = list(map(int, match.results.split("@")))
            layer_results.append(score)
        results.append(layer_results)
    return str(results).replace("None", "null")
