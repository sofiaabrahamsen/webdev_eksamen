from flask import Flask, render_template, app, session, redirect, url_for, request
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

###################################
###################################
def _________GET_________(): pass
###################################
###################################

##############################
# Login / landingpage
##############################
@app.get("/")
@x.no_cache
def view_login():
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role"))
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer"))
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))

###################################
###################################
def _________POST_________(): pass
###################################
###################################

##############################
# Login /landingpage
##############################
@app.post("/")
def login():
    try:
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        db, cursor = x.db()
        q = """ SELECT * FROM users
                JOIN users_roles
                ON user_pk = user_role_user_fk
                JOIN roles
                ON role_pk = user_role_role_fk
                WHERE user_email = %s"""
        cursor.execute(q, (user_email,))
        rows = cursor.fetchall()
        if not rows:
            toast = render_template("___toast.html", message="user not registered")
            return f"""<template mix-target="#toast">{toast}</template>""", 400
        if not check_password_hash(rows[0]["user_password"], user_password):
            toast = render_template("___toast.html", message="invalid credentials")
            return f"""<template mix-target="#toast">{toast}</template>""", 401
        roles = []
        for row in rows:
            roles.append(row["role_name"])
        user = {
            "user_pk": rows[0]["user_pk"],
            "user_name": rows[0]["user_name"],
            "user_last_name": rows[0]["user_last_name"],
            "user_email": rows[0]["user_email"],
            "roles": roles
        }
        ic(user)
        session["user"] = user
        if len(roles) == 1:
            return f"""<template mix-redirect="/{roles[0]}"></template>"""
        return f"""<template mix-redirect="/choose-role"></template>"""
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500
        return "<template>System under maintenance</template>", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


if __name__ == "__main__":
    app.run(debug=True)