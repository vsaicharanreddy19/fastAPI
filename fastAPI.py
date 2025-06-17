from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import hashlib
import uvicorn

app = FastAPI()

# Password hashing function using SHA-256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# PostgreSQL database connection
def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="Sai@9177"
    )

# Pydantic model for user input
class User(BaseModel):
    username: str
    password: str

# Root endpoint to avoid 404
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI User Auth API!"}

# Register endpoint
@app.post("/register")
def register_user(user: User):
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Check if user already exists
        cur.execute("SELECT username FROM users WHERE username = %s", (user.username,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists.")

        # Insert new user with hashed password
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (user.username, hash_password(user.password))
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "User registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Login endpoint
@app.post("/login")
def login_user(user: User):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (user.username,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and result[0] == hash_password(user.password):
            return {"message": f"Welcome, {user.username}!"}
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with Uvicorn if executed directly
if __name__ == "__main__":
    uvicorn.run("fastAPI:app", host="127.0.0.1", port=8000, reload=True)
