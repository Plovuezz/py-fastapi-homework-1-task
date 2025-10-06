import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db, MovieModel
from src.schemas import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter()


@router.get(
    "/movies/",
    response_model=MovieListResponseSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "content": {
                "application/json": {
                    "example": {"detail": "No movies found."},
                },
            },
        },
    },
)
async def get_movies(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=20)] = 10,
) -> MovieListResponseSchema:

    total_items = await db.scalar(select(func.count()).select_from(MovieModel))
    total_pages = math.ceil(total_items / per_page)

    if not total_items or page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    movies = await db.scalars(
        select(MovieModel)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .order_by(MovieModel.id)
    )

    return MovieListResponseSchema(
        movies=movies,
        prev_page=(
            str(request.url.replace_query_params(page=page - 1, per_page=per_page))
            if page > 1 else None
        ),
        next_page=(
            str(request.url.replace_query_params(page=page + 1, per_page=per_page))
            if page < total_pages else None
        ),
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get(
    "/movies/{movie_id}/",
    response_model=MovieDetailResponseSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "content": {
                "application/json": {
                    "example": {"detail": "Movie with the given ID was not found."},
                },
            },
        },
    },
)
@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    movie = await db.get(MovieModel, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )
    return movie
