from pydantic import BaseModel, ConfigDict
from datetime import date


class MovieDetailResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    date: date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str


class MovieListResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    movies: list[MovieDetailResponseSchema]
    prev_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int
