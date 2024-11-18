from flask import Flask, render_template, app
import x

app = Flask(__name__)

def _________GET_________(): pass

##############################
@app.get("/")
def view_index():
    name = "Test"
    return render_template("view_index.html", name=name)