from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Modelo para criar tarefa (sem ID)
class TarefaCreate(BaseModel):
    Titulo: str
    Descricao: str

# Modelo da tarefa com ID
class Tarefa(BaseModel):
    id: int
    Titulo: str
    Descricao: str

# Armazenamento em memória
tarefas: List[Tarefa] = []
proximo_id = 1

# GET /tarefas - Listar todas as tarefas
@app.get("/tarefas", response_model=List[Tarefa])
def listar_tarefas():
    return tarefas

# POST /tarefas - Criar nova tarefa
@app.post("/tarefas", response_model=Tarefa)
def criar_tarefa(tarefa: TarefaCreate):
    global proximo_id
    nova_tarefa = Tarefa(id=proximo_id, **tarefa.dict())
    tarefas.append(nova_tarefa)
    proximo_id += 1
    return nova_tarefa

# DELETE /tarefas/{id} - Deletar uma tarefa
@app.delete("/tarefas/{id}")
def deletar_tarefa(id: int):
    for t in tarefas:
        if t.id == id:
            tarefas.remove(t)
            return {"mensagem": "Tarefa deletada com sucesso"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")
