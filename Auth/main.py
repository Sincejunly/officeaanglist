from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import databases
import sqlalchemy
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
DATABASE_URL = "mysql://root:159756@192.168.5.4/officeaanglist"

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(50), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
)



engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

database = databases.Database(DATABASE_URL)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问，根据需要进行配置
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法，根据需要进行配置
    allow_headers=["*"],  # 允许所有HTTP头，根据需要进行配置
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_current_user(request: Request):
    session = request.session
    user_id = session.get("user_id")
    if not user_id:
        return None
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query)
    return user


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code, content={"message": exc.detail}
    )


@app.post("/register")
async def register_user(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends()
):
    username = form_data.username
    password = form_data.password

    query = users.select().where(users.c.username == username)
    existing_user = await database.fetch_one(query)

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(password)

    query = users.insert().values(username=username, password=hashed_password)
    user_id = await database.execute(query)

    session = request.session
    session["user_id"] = user_id
    return {"message": "Registered and logged in successfully"}


@app.post("/login")
async def login(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends()
):
    username = form_data.username
    password = form_data.password

    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)

    if not user or not pwd_context.verify(password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    session = request.session
    session["user_id"] = user["id"]
    return {"message": "Logged in successfully"}


@app.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"message": "You are authenticated"}


app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
