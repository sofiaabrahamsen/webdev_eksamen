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
# Profile
##############################
@app.get("/profile")
def view_profile():
    user = session.get("user", "")
    user_role = session.get("role_name", "")
    if not user:
        return redirect(url_for("view_index"))
    return render_template("view_profile.html", user=user, user_role=user_role)

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

    try:
        db, cursor = x.db()  # Connect to the database

        # Fetch all items
        item_query = """
            SELECT
                i.item_pk, i.item_title, i.item_description, i.item_price, i.item_image,
                u.user_name AS restaurant_name
            FROM items i
            JOIN users u ON i.item_user_fk = u.user_pk
            WHERE i.item_deleted_at = 0
        """
        cursor.execute(item_query)
        items = cursor.fetchall()  # Fetch all items as a list of dictionaries
        ic(items)  # Debugging output to confirm data
        
        # Pass data to the template
        return render_template("view_customer.html", user=user, items=items)
    
    except Exception as ex:
        x.ic(ex)  # Log the error for debugging
        return "Error loading admin page", 500  # Return an error message if something goes wrong
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



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
    
    try:
        db, cursor = x.db()  # Connect to the database

        # Fetch all users
        user_query = """
            SELECT
                user_name, user_last_name, user_email
            FROM users
            WHERE user_deleted_at = 0
        """
        cursor.execute(user_query)
        users = cursor.fetchall()  # Fetch all users as a list of dictionaries
        ic(users)  # Debugging output to confirm data

        # Fetch all items
        item_query = """
            SELECT
                i.item_pk, i.item_title, i.item_description, i.item_price, i.item_image,
                u.user_name AS restaurant_name
            FROM items i
            JOIN users u ON i.item_user_fk = u.user_pk
            WHERE i.item_deleted_at = 0
        """
        cursor.execute(item_query)
        items = cursor.fetchall()  # Fetch all items as a list of dictionaries
        ic(items)  # Debugging output to confirm data
        
        # Pass data to the template
        return render_template("view_admin.html", user=user, users=users, items=items)
    
    except Exception as ex:
        x.ic(ex)  # Log the error for debugging
        return "Error loading admin page", 500  # Return an error message if something goes wrong
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Restaurant
##############################
@app.get("/restaurant")
@x.no_cache
def view_restaurant():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    
    try:
        db, cursor = x.db()  # Connect to the database

        # Fetch all items
        q = """
            SELECT
                i.item_pk, i.item_title, i.item_description, i.item_price, i.item_image,
                u.user_name AS restaurant_name
            FROM items i
            JOIN users u ON i.item_user_fk = u.user_pk
            WHERE i.item_deleted_at = 0
        """
        cursor.execute(q)
        items = cursor.fetchall()  # Fetch all items as a list of dictionaries
        ic(items)  # Debugging output to confirm data
        
        # Pass data to the template
        return render_template("view_restaurant.html", user=user, items=items)
    
    except Exception as ex:
        x.ic(ex)  # Log the error for debugging
        return "Error loading admin page", 500  # Return an error message if something goes wrong
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

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

##############################
# View restaurant add an item
##############################
@app.get("/add-item")
@x.no_cache
def view_restaurant_add():
    return render_template("view_restaurant_add.html")

##############################
# View restaurant edit an item
##############################
@app.get("/edit-item/<item_pk>")
@x.no_cache
def view_restaurant_edit(item_pk):
    if not session.get("user"):
        return redirect(url_for("view_login"))
    try:
        db, cursor = x.db()
        
        # Fetch the specific item data from the database
        q = """
            SELECT
                i.item_pk, i.item_title, i.item_description, i.item_price, i.item_image,
                u.user_name AS restaurant_name
            FROM items i
            JOIN users u ON i.item_user_fk = u.user_pk
            WHERE i.item_pk = %s AND i.item_deleted_at = 0
        """
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()

        if not item:
            x.raise_custom_exception("Item not found", 404)
        
        # Store the item_pk in the session
        session["item"] = {"item_pk": item_pk}
        
        # Pass item data to the template
        return render_template("view_restaurant_edit.html", item=item)
    
    except Exception as ex:
        x.ic(ex)
        return "Error loading edit page", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


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

        item_pk = str(uuid.uuid4())  # Generate a unique identifier for the item        
        item_created_at = int(time.time())
        item_deleted_at = 0
        item_blocked_at = 0
        item_updated_at = 0

        # Save the uploaded image to the designated folder
        file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image))

        # Database connection and insertion
        db, cursor = x.db()

        # Insert the new item into the database
        q = """
            INSERT INTO items (item_pk, item_user_fk, item_title, item_description, item_price, item_image, item_created_at, item_deleted_at, item_blocked_at, item_updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(q, (item_pk, user_pk, item_title, item_description, item_price, item_image, item_created_at, item_deleted_at, item_blocked_at, item_updated_at))

        # Commit the transaction to save the item
        db.commit()

        # Success response
        session["item"] = {"item_pk": item_pk}  # Store item_pk in the session

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
# Block user
##############################
@app.put("/users/block/<user_pk>")
def user_block(user_pk):
    try:
        # Check if the user is an admin
        if not "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_login"))
        
        # Validate the user_pk
        user_pk = x.validate_uuid4(user_pk)
        user_blocked_at = int(time.time())
        
        # Perform the database update to block the user
        db, cursor = x.db()
        q = 'UPDATE users SET user_blocked_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_blocked_at, user_pk))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot block user", 400)
        db.commit()

        # Return the updated block button (or change the button to Unblock)
        btn_block = render_template("___btn_block_user.html", user={"user_pk": user_pk})
        return f"""<template mix-target="#block-{user_pk}" mix-replace>{btn_block}</template>"""
    
    except Exception as ex:
        # Handle exceptions and roll back if needed
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
# Unblock user
##############################
@app.put("/users/unblock/<user_pk>")
def user_unblock(user_pk):
    try:
        # Check if the user is an admin
        if not "admin" in session.get("user").get("roles"): 
            return redirect(url_for("view_login"))
        
        # Validate the user_pk
        user_pk = x.validate_uuid4(user_pk)
        user_blocked_at = 0  # Unblock the user by setting user_blocked_at to 0
        
        # Perform the database update to unblock the user
        db, cursor = x.db()
        q = 'UPDATE users SET user_blocked_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_blocked_at, user_pk))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot unblock user", 400)
        db.commit()

        # Return the updated unblock button (or change the button to Block)
        btn_block = render_template("___btn_unblock_user.html", user={"user_pk": user_pk})
        return f"""<template mix-target="#unblock-{user_pk}" mix-replace>{btn_block}</template>"""
    
    except Exception as ex:
        # Handle exceptions and roll back if needed
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>Database error</template>", 500        
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

        # Get the item_pk from the session
        item_pk = session.get("item").get("item_pk")
        if not item_pk:
            ic("item_pk not found in session")
            x.raise_custom_exception("invalid item", 400)
        
        # validate inputs for form data
        item_title = x.validate_item_title()
        item_description = x.validate_item_description()
        item_price = x.validate_item_price()
        item_updated_at = int(time.time())
        
        # Validate and process the new image if provided
        file, item_image = x.validate_item_image()
        # Save the new image file
        file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image))

        db, cursor = x.db()
        q = """ UPDATE items
                SET item_title = %s, item_description = %s, item_price = %s, item_image = %s, item_updated_at = %s
                WHERE item_pk = %s
            """
        cursor.execute(q, (item_title, item_description, item_price, item_image, item_updated_at, item_pk))

        # Ensure exactly one row was updated
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


##############################
# Block item
##############################
@app.put("/items/block/<item_pk>")
def item_block(item_pk):
    try:
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
        item_pk = x.validate_uuid4(item_pk)
        item_blocked_at = int(time.time())
        db, cursor = x.db()
        q = 'UPDATE items SET item_blocked_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_blocked_at, item_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot block item", 400)
        db.commit()
        return """<template>item blocked</template>"""
    
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

##############################
# Unblock item
##############################
@app.put("/items/unblock/<item_pk>")
def item_unblock(item_pk):
    try:
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
        item_pk = x.validate_uuid4(item_pk)
        item_blocked_at = 0
        db, cursor = x.db()
        q = 'UPDATE items SET item_blocked_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_blocked_at, item_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot unblock item", 400)
        db.commit()
        return """<template>item unblocked</template>"""
    
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


##############################
# Delete item
##############################
@app.delete("/items/<item_pk>")
def item_delete(item_pk):
    try:
        # Check if user is logged
        if not session.get("user", ""): return redirect(url_for("view_login"))
        # Check if it is an admin (can delete all items). If its not the admin role then you can only delete your own items.
        if not "admin" in session.get("user").get("roles") and session.get("item").get("item_pk") != item_pk:
            return redirect(url_for("view_login"))
        item_pk = x.validate_uuid4(item_pk)
        item_deleted_at = int(time.time())
        db, cursor = x.db()
        q = 'UPDATE items SET item_deleted_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_deleted_at, item_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot delete item", 400)
        db.commit()
        return """<template>item deleted</template>"""
    
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