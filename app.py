from flask import Flask, render_template, app, session, redirect, url_for, request
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x
import uuid
import time
import os

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
# Index / landingpage
##############################
@app.get("/")
def view_index():
    return render_template("view_index.html")

##############################
# Index / landingpage
##############################
@app.get("/profile")
def view_profile():
    user = session.get("user", "")
    if not user:
        return redirect(url_for("view_index"))
    return render_template("view_profile.html", user=user)


##############################
# Items and map
##############################
@app.get("/items")
def view_items():
    return render_template("view_item.html")
##############################
# Login
##############################
@app.get("/login")
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

##############################
# Signup
##############################
@app.get("/signup")
@x.no_cache
def view_signup():  
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
    return render_template("view_signup.html", x=x, title="Signup")

##############################
# Customer
##############################
@app.get("/customer")
@x.no_cache
def view_customer():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return render_template("view_customer.html", user=user)

##############################
# Partner
##############################
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return render_template("view_partner.html", user=user)

##############################
# Admin
##############################
@app.get("/admin")
@x.no_cache
def view_admin():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user")
    if not "admin" in user.get("roles", ""):
        return redirect(url_for("view_login"))
    return render_template("view_admin.html", user=user)

##############################
# Choose role
##############################
@app.get("/choose-role")
@x.no_cache
def view_choose_role():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    if not len(session.get("user").get("roles")) >= 2:
        return redirect(url_for("view_login"))
    user = session.get("user")
    return render_template("view_choose_role.html", user=user, title="Choose role")

###################################
###################################
def _________POST_________(): pass
###################################
###################################

##############################
# Login
##############################
@app.post("/login")
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

##############################
# Signup
##############################
@app.post("/users")
@x.no_cache
def create_user():
    try:
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        hashed_password = generate_password_hash(user_password)
        
        user_pk = str(uuid.uuid4())
        user_created_at = int(time.time())
        user_deleted_at = 0
        user_blocked_at = 0
        user_updated_at = 0
        user_verified_at = 0
        user_verification_key = str(uuid.uuid4())

        db, cursor = x.db()
        q = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(q, (user_pk, user_name, user_last_name, user_email, 
                        hashed_password, user_created_at, user_deleted_at, user_blocked_at, 
                        user_updated_at, user_verified_at, user_verification_key))
        
        role_fk = x.CUSTOMER_ROLE_PK
        q_roles = 'INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES (%s, %s)'
        cursor.execute(q_roles, (user_pk, role_fk))
        db.commit()
        return """<template mix-redirect="/login"></template>""", 201
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "users.user_email" in str(ex): 
                toast = render_template("___toast.html", message="email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            return f"""<template mix-target="#toast" mix-bottom>System upgrating</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Logout
##############################
@app.post("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("view_login"))

##############################
# Create item
##############################
@app.post("/items")
def create_item():
    try:
        # Check if the user is logged in
        if not session.get("user"):
            x.raise_custom_exception("Please login to create an item.", 401)
        # Extract the user ID from the session
        user_pk = session.get("user").get("user_pk")
        # Validate inputs for the item
        item_title = x.validate_item_title()
        item_description = x.validate_item_description()
        item_price = x.validate_item_price()
        file, item_image = x.validate_item_image()  # Validate and process image file

        item_created_at = int(time.time())
        item_deleted_at = 0
        item_blocked_at = 0
        item_updated_at = 0

        # Save the uploaded image to the designated folder
        file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image))

        # Database connection and insertion
        db, cursor = x.db()
        item_pk = str(uuid.uuid4())  # Generate a unique identifier for the item

        # Insert the new item into the database
        q = """
            INSERT INTO items (item_pk, item_user_fk, item_title, item_description, item_price, item_image, item_created_at, item_deleted_at, item_blocked_at, item_updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(q, (item_pk, user_pk, item_title, item_description, item_price, item_image, item_created_at, item_deleted_at, item_blocked_at, item_updated_at))

        # Commit the transaction to save the item
        db.commit()

        # Success response
        toast = render_template("___toast.html", message="Item successfully created.")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""
    except Exception as ex:
        ic(ex)
        # Rollback the database transaction if there's an error
        if "db" in locals(): db.rollback()

        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    

        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500

        return "<template>System under maintenance</template>", 500
    finally:
        # Close database resources
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
##############################
##############################

def _________PUT_________(): pass

##############################
##############################
##############################

##############################
# Update user
##############################
@app.put("/users")
def user_update():
    try:
        if not session.get("user"): x.raise_custom_exception("please login", 401)

        user_pk = session.get("user").get("user_pk")
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()

        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE users
                SET user_name = %s, user_last_name = %s, user_email = %s, user_updated_at = %s
                WHERE user_pk = %s
            """
        cursor.execute(q, (user_name, user_last_name, user_email, user_updated_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot update user", 401)
        db.commit()
        return """<template>user updated</template>"""
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            if "users.user_email" in str(ex): return "<template>email not available</template>", 400
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500    
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Update item
##############################
@app.put("/items")
def item_update():
    try:
        if not session.get("user"): x.raise_custom_exception("please login", 401)

        #item_pk = session.get("item").get("item_pk")
        #if not item_pk:
        #    x.raise_custom_exception("invalid item", 400)

        # Validate item from session
        item_data = session.get("item")
        if not item_data or not item_data.get("item_pk"):
            x.raise_custom_exception("Invalid item. Please refresh and try again.", 400)
        item_pk = item_data.get("item_pk")
    
        item_title = x.validate_item_title()
        item_description = x.validate_item_description()
        item_price = x.validate_item_price()
        item_updated_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE items
                SET item_title = %s, item_description = %s, item_price = %s, item_updated_at = %s
                WHERE item_pk = %s
            """
        cursor.execute(q, (item_title, item_description, item_price, item_updated_at, item_pk))
        
        if cursor.rowcount != 1: x.raise_custom_exception("cannot update item", 401)
        db.commit()
        return """<template>item updated</template>"""
    
    except Exception as ex:
        ic(ex)
        # Rollback the database transaction if there's an error
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


###################################
###################################
def ________DELETE________(): pass
###################################
###################################


##############################
# Delete user
##############################
@app.delete("/users/<user_pk>")
def user_delete(user_pk):
    try:
        # Check if user is logged
        if not session.get("user", ""): return redirect(url_for("view_login"))
        # Check if it is an admin (can delete all users). If its not the admin role then you can only delete your own user.
        if not "admin" in session.get("user").get("roles") and session.get("user").get("user_pk") != user_pk:
            return redirect(url_for("view_login"))
        user_pk = x.validate_uuid4(user_pk)
        user_deleted_at = int(time.time())
        db, cursor = x.db()
        q = 'UPDATE users SET user_deleted_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_deleted_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot delete user", 400)
        db.commit()
        return """<template>user deleted</template>"""
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##########################
if __name__ == "__main__":
    app.run(debug=True)