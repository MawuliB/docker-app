import requests
from flask import Flask, render_template
from flask_wtf import CSRFProtect

url = "https://api.github.com/users/"
USER_NOT_FOUND = "User not found 😥."

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)


def fetch_user(username):
    response = requests.get(url + username)
    if response.status_code == 200:
        return response.json()
    return USER_NOT_FOUND


def fetch_followers(username):
    response = requests.get(url + username + "/followers")
    if response.status_code != 200:
        return []
    res = []
    for follower in response.json():
        res.append(follower['login'])
    return res


def fetch_following(username):
    response = requests.get(url + username + "/following")
    if response.status_code != 200:
        return []
    res = []
    for following in response.json():
        res.append(following['login'])
    return res


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/<username>")
def user_profile(username):
    try:
        user = fetch_user(username)
        user["followers_list"] = fetch_followers(username)
        user["following_list"] = fetch_following(username)
        return user
    except Exception as e:
        return {"error": str(e), "message": USER_NOT_FOUND}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
