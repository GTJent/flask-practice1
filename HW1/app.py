from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def main_template_render():
    return render_template("main.html", myname="김준혁", mynum ="22011725")
