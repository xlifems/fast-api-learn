from email.policy import HTTP
from urllib import response
from wsgiref import validate
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

# import pydantic model
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field


# import typing for union type and optional type
from typing import Optional

from jwt_manager import create_token, validate_token

app = FastAPI()

# Metadata for the API documentation in the OpenAPI schema
app.title = "My FastAPI APP"
app.version = "0.1.0"

# Run the app with the command uvicorn main:app --reload or uvicorn main:app --reload --port 5000 --host 0.0.0.0


class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(max_length=100, min_length=1)
    overview: str = Field(max_length=500, min_length=1)
    year: int = Field(title="Movie year", ge=1900, le=2022)
    rating: float
    category: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Titanic",
                "overview": "Jack (Leonardo DiCaprio) es un joven artista que, en una partida de ...",
                "year": 1997,
                "rating": 7.8,
                "category": "Drama",
            }
        }


class User(BaseModel):
    username: Optional[str] = None
    password: str = Field(default="admin", min_length=5)
    email: str = Field(default="admin@admin.com")
    full_name: Optional[str] = None


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data["email"] != "admin@admin.com":
            raise HTTPException(status_code=403, detail="Invalid token")


movies = [
    {
        "id": 1,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        "year": "2009",
        "rating": 7.8,
        "category": "Acción",
    },
    {
        "id": 2,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        "year": "2009",
        "rating": 7.8,
        "category": "Acción",
    },
    {
        "id": 3,
        "title": "Titanic",
        "overview": "Jack (Leonardo DiCaprio) es un joven artista que, en una partida de ...",
        "year": "1997",
        "rating": 7.8,
        "category": "Drama",
    },
]


@app.get("/", tags=["Home"])
def message():
    return HTMLResponse("<h1>Hello world</h1>")


# create a new endpoint to login user
@app.post("/login", tags=["Auth"])
def login(user: User):
    if user.email == "admin@admin.com" and user.password == "admin":
        token = create_token(user.dict())
        return JSONResponse(
            status_code=200, content={"message": "Login success", "token": token}
        )


# create a new endpoint to get movies list
@app.get("/movies", tags=["Movies"], response_model=list[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> list[Movie]:
    return JSONResponse(content=movies)


# get a movie by id
@app.get("/movies/{movie_id}", tags=["Movies"])
def get_movie(movie_id: int = Path(ge=3, le=15)):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return {"message": "Movie not found"}


# create a new endpoint to get movies by category , year or rating this is a query parameter
@app.get("/movies/", tags=["Movies"])
def get_movies_by_category(category: str = Query(min_length=5)):
    result = movies
    if category:
        result = [movie for movie in result if movie["category"] == category]

    return result


# create a new endpoint to create a new movie to the list
@app.post("/movies", tags=["Movies"])
def create_movie(movie: Movie):
    new_movie = movie
    movies.append(new_movie)
    return new_movie


# create a new endpoint to update a movie by id
@app.put("/movies/{movie_id}", tags=["Movies"])
def update_movie(movie_id: int, movie: Movie):
    for mo in movies:
        if mo["id"] == movie_id:
            mo["title"] = movie.title
            mo["overview"] = movie.overview
            mo["year"] = movie.year
            mo["rating"] = movie.rating
            mo["category"] = movie.category
            return movie
    return {"message": "Movie not found"}


# create a new endpoint to delete a movie by id
@app.delete("/movies/{movie_id}", tags=["Movies"])
def delete_movie(movie_id: int):
    for movie in movies:
        if movie["id"] == movie_id:
            movies.remove(movie)
            return {"message": "Movie deleted"}
    return {"message": "Movie not found"}
