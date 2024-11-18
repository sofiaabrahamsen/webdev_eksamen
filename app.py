from flask import Flask, render_template, app, default_app,
import x

app = Flask(__name__)

def _________GET_________(): pass

##############################
@app.get("/")
def view_index():
    name = "Test"
    return render_template("view_index.html", name=name)

application = default_app()
##############################
# if "PYTHONANYWHERE_DOMAIN" in os.environ:
#     application = default_app()
# else:
#     ic("Server listening...")
#     run(host="0.0.0.0", port=80, debug=True, reloader=True, interval=0.5)

##############################