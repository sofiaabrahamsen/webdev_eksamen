import x
import uuid

db, cursor = x.db()

def insert_user(user):
    q = f"""
        INSERT INTO users
        VALUES (%s, %s ,%s, %s)
        """
    values = tuple(user.values())
    cursor.execute(q, values)
try:
    ##############################
    cursor.execute("DROP TABLE IF EXISTS users")
    
    q = """
        CREATE TABLE users (
            user_pk CHAR(36),
            user_name VARCHAR(20) NOT NULL,
            user_last_name VARCHAR(20) NOT NULL,
            user_email VARCHAR(50) NOT NULL,
            PRIMARY KEY(user_pk)
        )
        """
    cursor.execute(q)

    # Create User
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "Santiago",
        "user_last_name" : "Donoso",
        "user_email": "a@a.com"
    }
    insert_user(user)

    db.commit()

except Exception as ex:
    if "db" in locals(): db.rollback()

finally:
    if "cursor" in locals(): cursor.close()
    if "db" in locals(): db.close()