from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import redis
import uuid
import json

app = FastAPI(title="API de Séries e Filmes com Redis")

# Conexão Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


# ----------------------------
# Modelos
# ----------------------------
class Item(BaseModel):
    nome: str


class ListaCreate(BaseModel):
    nome: str
    usuario_id: str


# ----------------------------
# Criar lista
# ----------------------------
@app.post("/listas")
def criar_lista(lista: ListaCreate):
    lista_id = str(uuid.uuid4())
    key = f"lista:{lista_id}"

    data = {
        "id": lista_id,
        "nome": lista.nome,
        "usuario_id": lista.usuario_id,
        "itens": []
    }

    r.set(key, json.dumps(data))
    return data


# ----------------------------
# Obter lista
# ----------------------------
@app.get("/listas/{lista_id}")
def obter_lista(lista_id: str):
    key = f"lista:{lista_id}"
    data = r.get(key)

    if not data:
        raise HTTPException(status_code=404, detail="Lista não encontrada")

    return json.loads(data)


# ----------------------------
# Adicionar item
# ----------------------------
@app.post("/listas/{lista_id}/itens")
def adicionar_item(lista_id: str, item: Item):
    key = f"lista:{lista_id}"
    data = r.get(key)

    if not data:
        raise HTTPException(status_code=404, detail="Lista não encontrada")

    lista = json.loads(data)
    lista["itens"].append(item.nome)

    r.set(key, json.dumps(lista))
    return lista


# ----------------------------
# Remover item
# ----------------------------
@app.delete("/listas/{lista_id}/itens")
def remover_item(lista_id: str, item: Item):
    key = f"lista:{lista_id}"
    data = r.get(key)

    if not data:
        raise HTTPException(status_code=404, detail="Lista não encontrada")

    lista = json.loads(data)

    if item.nome in lista["itens"]:
        lista["itens"].remove(item.nome)
        r.set(key, json.dumps(lista))
        return lista

    raise HTTPException(status_code=404, detail="Item não encontrado")


# ----------------------------
# Listar todas as listas do usuário
# ----------------------------
@app.get("/listas")
def listar_listas(usuario_id: str):
    """RF09: Retorna todas as listas associadas a um usuário autenticado."""
    keys = r.keys("lista:*")
    listas = []

    for key in keys:
        lista = json.loads(r.get(key))
        if lista.get("usuario_id") == usuario_id:
            listas.append(lista)

    return listas


# ----------------------------
# Deletar lista
# ----------------------------
@app.delete("/listas/{lista_id}")
def deletar_lista(lista_id: str):
    key = f"lista:{lista_id}"

    if not r.exists(key):
        raise HTTPException(status_code=404, detail="Lista não encontrada")

    r.delete(key)
    return {"message": "Lista removida com sucesso"}