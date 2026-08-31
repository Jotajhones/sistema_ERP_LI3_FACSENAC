from pydantic import BaseModel, EmailStr

class AuthRequest(BaseModel):
    email: EmailStr
    senha: str

class AuthResponse(BaseModel):
    role: str