from pydantic import BaseModel


class ResetSenhaResposta(BaseModel):
    mensagem: str
