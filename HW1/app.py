from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def main_template_render():
    return render_template("main.html", myname="김준혁", mynum ="22011725")

@app.route("/profile")
def profile_template_render():
    hobbies = ["게임","영화","유튜브 시청"]
    return render_template("profile.html",myhobbies=hobbies)

@app.route("/greet/<name>")
def greet_template_render(name):
    return render_template("greet.html",name=name)
