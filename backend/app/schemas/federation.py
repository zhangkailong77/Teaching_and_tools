from pydantic import BaseModel


class FederationSsoTicketResponse(BaseModel):
    ticket: str
    expires_in: int
    school_id: str


class FederationSsoConsumeRequest(BaseModel):
    ticket: str


class FederationSsoConsumeResponse(BaseModel):
    user_id: int
    username: str
    role: str
    school_id: str
