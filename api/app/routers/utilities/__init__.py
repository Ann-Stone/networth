from fastapi import APIRouter

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/utilities", tags=["utilities"])


@router.get(
    "/ping",
    response_model=ApiResponse[dict],
    summary="Health ping",
    description="Returns an envelope-shaped response to verify the API is up.",
    responses={
        200: {"description": "API is reachable and returning a well-formed envelope."},
    },
)
def ping() -> ApiResponse[dict]:
    return ApiResponse(data={"pong": True})
