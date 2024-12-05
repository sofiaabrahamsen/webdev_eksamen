from flask import make_response, request
from functools import wraps
from decimal import Decimal, InvalidOperation
import mysql.connector
import re
import os
import uuid

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

ADMIN_ROLE_PK = "16fd2706-8baf-433b-82eb-8c7fada847da"
CUSTOMER_ROLE_PK = "c56a4180-65aa-42ec-a945-5fd21dec0538"
PARTNER_ROLE_PK = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
RESTAURANT_ROLE_PK = "9f8c8d22-5a67-4b6c-89d7-58f8b8cb4e15"

class CustomException(Exception):
    def __init__(self, message, code):
        super().__init__(message)  # Initialize the base class with the message
        self.message = message  # Store additional information (e.g., error code)
        self.code = code  # Store additional information (e.g., error code)

def raise_custom_exception(error, status_code):
    raise CustomException(error, status_code)

##############################
def db():
    db = mysql.connector.connect(
        host="mysql",      # Replace with your MySQL server's address or docker service name "mysql"
        user="root",  # Replace with your MySQL username
        password="password",  # Replace with your MySQL password
        database="company"   # Replace with your MySQL database name
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor

##############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view

##############################
def allow_origin(origin="*"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Call the wrapped function
            response = make_response(f(*args, **kwargs))
            # Add Access-Control-Allow-Origin header to the response
            response.headers["Access-Control-Allow-Origin"] = origin
            # Optionally allow other methods and headers for full CORS support
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        return decorated_function
    return decorator

##############################
USER_NAME_MIN = 2
USER_NAME_MAX = 20
USER_NAME_REGEX = f"^.{{{USER_NAME_MIN},{USER_NAME_MAX}}}$"
def validate_user_name():
    error = f"name {USER_NAME_MIN} to {USER_NAME_MAX} characters"
    user_name = request.form.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name): raise_custom_exception(error, 400)
    return user_name

##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    error = f"last name {USER_LAST_NAME_MIN} to {USER_LAST_NAME_MAX} characters"
    user_last_name = request.form.get("user_last_name", "").strip() # None
    if not re.match(USER_LAST_NAME_REGEX, user_last_name): raise_custom_exception(error, 400)
    return user_last_name

##############################
REGEX_EMAIL = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
def validate_user_email():
    error = "email invalid"
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_EMAIL, user_email): raise_custom_exception(error, 400)
    return user_email

##############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password():
    error = f"password {USER_PASSWORD_MIN} to {USER_PASSWORD_MAX} characters"
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password): raise_custom_exception(error, 400)
    return user_password

##############################
REGEX_UUID4 = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
def validate_uuid4(uuid4 = ""):
    error = f"invalid uuid4"
    if not uuid4:
        uuid4 = request.values.get("uuid4", "").strip()
    if not re.match(REGEX_UUID4, uuid4): raise_custom_exception(error, 400)
    return uuid4


##############################
UPLOAD_ITEM_FOLDER = './images'
ALLOWED_ITEM_FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def validate_item_image():
    if 'item_image' not in request.files: raise_custom_exception("item_image missing", 400)
    file = request.files.get("item_image", "")
    if file.filename == "": raise_custom_exception("item_image field is empthy", 400)

    if file:
        ic(file.filename)
        file_extension = os.path.splitext(file.filename)[1][1:]
        ic(file_extension)
        if file_extension not in ALLOWED_ITEM_FILE_EXTENSIONS: raise_custom_exception("item_image invalid extension", 400)
    
        filename = f"{str(uuid.uuid4())}.{file_extension}"
        return file, filename
    
##############################
ITEM_TITLE_MIN = 2
ITEM_TITLE_MAX = 20
ITEM_TITLE_REGEX = f"^.{{{ITEM_TITLE_MIN},{ITEM_TITLE_MAX}}}$"
def validate_item_title():
    error = f"title must be between {ITEM_TITLE_MIN} to {ITEM_TITLE_MAX} characters"
    item_title = request.form.get("item_title", "").strip()
    if not re.match(ITEM_TITLE_REGEX, item_title): raise_custom_exception(error, 400)
    return item_title

##############################
ITEM_DESCRIPTION_MIN = 2
ITEM_DESCRIPTION_MAX = 50
ITEM_DESCRIPTION_REGEX = f"^.{{{ITEM_DESCRIPTION_MIN},{ITEM_DESCRIPTION_MAX}}}$"
def validate_item_description():
    error = f"description much be between {ITEM_DESCRIPTION_MIN} to {ITEM_DESCRIPTION_MAX} characters"
    item_description = request.form.get("item_description", "").strip()
    if not re.match(ITEM_DESCRIPTION_REGEX, item_description): raise_custom_exception(error, 400)
    return item_description

##############################
ITEM_PRICE_MIN = Decimal('0.01')
ITEM_PRICE_MAX = Decimal('10000.00')
# allows numbers up to 5 digits before the decimal. Optional decimal with up to 2 digits
ITEM_PRICE_REGEX = r"^\d{1,5}(\.\d{1,2})?$"  # Match numbers like 12345.67, 12, 123.4
def validate_item_price():
    error = f"Price must be a valid number between {ITEM_PRICE_MIN} and {ITEM_PRICE_MAX}"
    item_price_str = request.form.get("item_price", "").strip()
    try:
        # Convert item_price to Decimal for precise validation
        item_price = Decimal(item_price_str)
    except InvalidOperation:
        # Raise error if conversion to Decimal fails
        raise_custom_exception("Price must be a valid decimal number", 400)
    # Check if the price is within the allowed range
    if not re.match(ITEM_PRICE_REGEX, item_price): raise_custom_exception(error, 400)
    return item_price
