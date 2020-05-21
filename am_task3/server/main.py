from flask import Flask, jsonify
app = Flask(__name__)

TEST = []

@app.route('/login/<username>')
def api_login(username):
    global TEST
    status = False
    if username in TEST:
        status = True
    data = {
        'status': status,
        '__debug': 'login'
    }
    return jsonify(data)

@app.route('/register/<username>')
def api_register(username):
    global TEST
    status = False
    if username in TEST:
        status = False
    else:
        TEST.append(username)
        status = True
    data = {
        'status': status,
        '__debug': 'register'
    }
    return jsonify(data)

SCORES = {}

@app.route("/score/<username>/<score>")
def api_score(username, score):
    global SCORES
    SCORES[username] = score
    data = {
        'status': True,
        '__debug': 'score'
    }
    return jsonify(data)

@app.route("/rank")
def api_rank():
    global SCORES
    local_list = []
    for username in SCORES:
        local_list.append({"name": username, "score": SCORES[username]})
    local_list = sorted(local_list, key=lambda x: x["score"], reverse=True)
    print(local_list)
    data = {
        'list': local_list,
        'status': True,
        '__debug': 'rank'
    }
    return jsonify(data)


if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=8000)
