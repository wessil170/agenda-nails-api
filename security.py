from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def criar_hash(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha_digitada: str, senha_hash: str):
    return pwd_context.verify(senha_digitada, senha_hash)
