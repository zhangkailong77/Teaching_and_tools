from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api import deps
from app.core.config import settings
from app.core.federation_sso import consume_federation_ticket, issue_federation_ticket
from app.models.user import User
from app.schemas.federation import (
    FederationSsoConsumeRequest,
    FederationSsoConsumeResponse,
    FederationSsoTicketResponse,
)

router = APIRouter()


@router.post("/sso/token", response_model=FederationSsoTicketResponse)
def issue_sso_ticket(current_user: User = Depends(deps.get_current_user)):
    try:
        result = issue_federation_ticket(
            user_id=current_user.id,
            username=current_user.username,
            role=current_user.role,
            school_id=settings.school_id,
            ttl_seconds=settings.federation_sso_ttl_seconds,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return {
        "ticket": result["ticket"],
        "expires_in": result["expires_in"],
        "school_id": settings.school_id,
    }


@router.post("/sso/consume", response_model=FederationSsoConsumeResponse)
def consume_sso_ticket(
    request: FederationSsoConsumeRequest,
    x_federation_secret: str | None = Header(default=None),
):
    expected = settings.federation_consumer_secret
    if expected and x_federation_secret != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid federation consumer secret",
        )

    try:
        payload = consume_federation_ticket(ticket=request.ticket)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return FederationSsoConsumeResponse(
        user_id=payload["user_id"],
        username=payload["username"],
        role=payload["role"],
        school_id=payload["school_id"],
    )
