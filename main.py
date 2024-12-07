import requests
from flask import Flask, render_template

url = "https://api.github.com/users/"
USER_NOT_FOUND = "User not found 😥"

app = Flask(__name__)


def fetch_user(username):
    response = requests.get(url + username)
    if response.status_code == 200:
        return response.json()
    return USER_NOT_FOUND


def fetch_followers(username):
    response = requests.get(url + username + "/followers")
    res = []
    for followers in response.json():
        res.append(followers["login"])
    if response.status_code == 200:
        return res
    return USER_NOT_FOUND


def fetch_following(username):
    response = requests.get(url + username + "/following")
    res = []
    for following in response.json():
        res.append(following["login"])
    if response.status_code == 200:
        return res
    return USER_NOT_FOUND


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
    app.run(host="0.0.0.0", port=5000, debug=True)
