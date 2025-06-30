from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from jose import JWTError, jwt
from datetime import datetime, timedelta

# App
app = FastAPI()

# Dados simulados (usuário fake)
fake_user = {
    "username": "admin",
    "password": "1234"  # Em produção, use hash
}

# Configurações do JWT
SECRET_KEY = "segredo_super_secreto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modelo de usuário e token
class Token(BaseModel):
    access_token: str
    token_type: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Função para criar o token JWT
def criar_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Função para verificar o token e retornar o usuário
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != fake_user["username"]:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

# Rota de login
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != fake_user["username"] or form_data.password != fake_user["password"]:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    token = criar_token({"sub": fake_user["username"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

# ======= MODELOS E ROTAS PROTEGIDAS =======

class TarefaCreate(BaseModel):
    Titulo: str
    Descricao: str

class Tarefa(BaseModel):
    id: int
    Titulo: str
    Descricao: str

tarefas: List[Tarefa] = []
proximo_id = 1

@app.get("/tarefas", response_model=List[Tarefa])
def listar_tarefas(usuario: str = Depends(get_current_user)):
    return tarefas

@app.post("/tarefas", response_model=Tarefa)
def criar_tarefa(tarefa: TarefaCreate, usuario: str = Depends(get_current_user)):
    global proximo_id
    nova_tarefa = Tarefa(id=proximo_id, **tarefa.dict())
    tarefas.append(nova_tarefa)
    proximo_id += 1
    return nova_tarefa

@app.delete("/tarefas/{id}")
def deletar_tarefa(id: int, usuario: str = Depends(get_current_user)):
    for t in tarefas:
        if t.id == id:
            tarefas.remove(t)
            return {"mensagem": "A sua Tarefa foi deletada com sucesso bro"}
    raise HTTPException(status_code=404, detail="A sua Tarefa não foi encontrada meu parceiro")
