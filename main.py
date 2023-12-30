from fastapi import FastAPI
from tortoise import Tortoise, fields, run_async
from tortoise.models import Model
import httpx
import sqlite3
from pydantic import BaseModel

app = FastAPI(
    title='FastApi by Stungelx'
)

class Post(BaseModel):
    id: int
    user_id: int
    title: str
    body: str

class User(BaseModel):
    id: int
    name: str
    email: str
    gender: str
    status: str

class Users(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    email = fields.TextField(null=True, default="", description="Email not found")
    gender = fields.TextField(null=True, default="", description="Gender not found")
    status = fields.TextField(null=True, default="", description="Status not found")

    class Meta:
        table = "users"

    def __str__(self):
        return self.name

class Posts(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(Null=True)
    title = fields.TextField(null=True, default="", description="Title not found")
    body = fields.TextField(null=True, default="", description="Message not found")

    class Meta:
        table = "posts"

    def __str__(self):
        return self.title

async def init():
    await Tortoise.init(db_url="sqlite://sqlite3.db", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

async def fetch_and_save_users():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://gorest.co.in/public/v2/users")
        if response.status_code == 200:
            data = response.json()
            for user_data in data:
                existing_user = await Users.filter(id=user_data["id"])
                if not existing_user:
                    await Users.create(id=user_data["id"], name=user_data["name"], email=user_data.get("email"),
                                       gender=user_data.get("gender", ""), status=user_data.get("status", ""))
            print(await Users.all().values("id", "name"))
        else:
            print("Failed to fetch data from API")

async def fetch_and_save_posts():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://gorest.co.in/public/v2/posts")
        if response.status_code == 200:
            data = response.json()
            for post_data in data:
                existing_post = await Posts.filter(id=post_data["id"])
                if not existing_post:
                    await Posts.create(id=post_data["id"], user_id=post_data["user_id"],
                                       title=post_data.get("title", ""), body=post_data.get("body", ""))
            print(await Posts.all().values("id", "user_id", "title"))
        else:
            print("Failed to fetch data from API")

if __name__ == "__main__":

    run_async(init())
    run_async(fetch_and_save_users())
    run_async(fetch_and_save_posts())

#Function, what retunned the list of all users
@app.get("/all_users/", response_model=list[User])
async def all_users():
    with sqlite3.connect('sqlite3.db') as dbu:
        cursor = dbu.cursor()
        dtb1 = cursor.execute("""SELECT * FROM users""")
        result = dtb1.fetchall()
        return [dict(zip(['id', 'name', 'email', 'gender', 'status'], row)) for row in result]

@app.get("/all_posts/", response_model=list[Post])
async def all_posts():
    async with sqlite3.connect('sqlite3.db') as dbu:
        cursor = dbu.cursor()
        dtb2 = cursor.execute("""SELECT * FROM posts""")
        result = dtb2.fetchall()
        return [dict(zip(['id', 'user_id', 'title', 'body'], row)) for row in result]

@app.get("/user/{user_id}", response_model=list[User])
async def find_user(user_id: int):
    with sqlite3.connect('sqlite3.db') as dbu:
        cursor = dbu.cursor()
        dtb1 = cursor.execute(f"""SELECT * FROM users WHERE id = {user_id}""")
        result = dtb1.fetchall()
        return [dict(zip(['id', 'name', 'email', 'gender', 'status'], row)) for row in result]

@app.get("/post/{user_id}", response_model=list[Post])
async def find_user_posts(user_id: int):
    with sqlite3.connect('sqlite3.db') as dbu:
        cursor = dbu.cursor()
        dtb1 = cursor.execute(f"""SELECT * FROM posts WHERE user_id = {user_id}""")
        result = dtb1.fetchall()
        return [dict(zip(['id', 'user_id', 'title', 'body'], row)) for row in result]