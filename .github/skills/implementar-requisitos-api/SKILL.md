---
name: implementar-requisitos-api
description: 'Use quando: implementar novos requisitos da API, encapsular rotas HTTP, organizar endpoints em routers, criar serviços para isolar lógica. Implementação em Python (FastAPI) com suporte a Redis, seguindo padrões de código limpo e português.'
argument-hint: 'Qual requisito ou endpoint você precisa implementar?'
user-invocable: true
---

# Implementar Requisitos da API de Séries e Filmes

Skill para encapsular rotas HTTP, organizar endpoints e implementar novos requisitos funcionais da API em Python (FastAPI + Redis), com código limpo e comentários em português.

## Quando Usar

✅ Implementar um novo requisito funcional (RF##)  
✅ Refatorar endpoints para melhor organização  
✅ Criar serviços para encapsular lógica de Redis  
✅ Adicionar novos routers ou modelos  
✅ Implementar validações ou tratamento de erros  

## Checklist de Implementação (5-7 passos)

### 1. Entender o Requisito
- [ ] Ler descrição do requisito em `requisitos.md`
- [ ] Identificar quais dados serão usados (lista, itens, metadados)
- [ ] Definir inputs e outputs esperados
- [ ] Listar dependências ou requisitos relacionados (RF## prévios)

### 2. Criar o Modelo Pydantic (se necessário)
```python
# Estrutura padrão para novos modelos
class NomeDoModelo(BaseModel):
    """Descrição do modelo em português."""
    campo1: str
    campo2: int | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "campo1": "valor_exemplo",
                "campo2": 42
            }
        }
```

### 3. Criar ou Estender o Serviço (Service/Repository)
Encapsular lógica de Redis em uma classe dedicada:

```python
# Exemplo: ServicoLista para RF01, RF02, RF03, etc.
class ServicoLista:
    """Encapsula operações Redis para gerenciamento de listas."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def criar_lista(self, nome: str) -> dict:
        """Cria uma nova lista vazia e retorna dados da lista."""
        lista_id = str(uuid.uuid4())
        dados = {
            "id": lista_id,
            "nome": nome,
            "itens": [],
            "publica": False,
            "criada_em": datetime.now().isoformat()
        }
        chave = f"lista:{lista_id}"
        self.redis.set(chave, json.dumps(dados))
        return dados
    
    def obter_lista(self, lista_id: str) -> dict | None:
        """Recupera uma lista pelo ID."""
        chave = f"lista:{lista_id}"
        dados = self.redis.get(chave)
        return json.loads(dados) if dados else None
    
    def adicionar_item(self, lista_id: str, nome_item: str) -> dict:
        """Adiciona um item à lista."""
        lista = self.obter_lista(lista_id)
        if not lista:
            raise ValueError(f"Lista {lista_id} não encontrada")
        
        item = {
            "id": str(uuid.uuid4()),
            "nome": nome_item,
            "adicionado_em": datetime.now().isoformat()
        }
        lista["itens"].append(item)
        chave = f"lista:{lista_id}"
        self.redis.set(chave, json.dumps(lista))
        return item
```

### 4. Criar ou Estender o Router (Rotas)
Organizar endpoints em um router dedicado:

```python
# arquivo: rotas_listas.py
from fastapi import APIRouter, HTTPException
from models import ListaCreate, Item  # Importar modelos
from servicos import ServicoLista     # Importar serviço

router_listas = APIRouter(
    prefix="/listas",
    tags=["Listas"],
    responses={404: {"description": "Não encontrado"}}
)

# Instanciar serviço (assumindo Redis disponível globalmente)
servico = ServicoLista(r)

@router_listas.post("", response_model=dict)
def criar_lista(lista: ListaCreate):
    """RF01: Criar uma nova lista vazia."""
    return servico.criar_lista(lista.nome)

@router_listas.get("/{lista_id}", response_model=dict)
def obter_lista(lista_id: str):
    """RF03: Consultar itens da lista."""
    lista = servico.obter_lista(lista_id)
    if not lista:
        raise HTTPException(status_code=404, detail="Lista não encontrada")
    return lista

@router_listas.post("/{lista_id}/itens")
def adicionar_item(lista_id: str, item: Item):
    """RF02: Adicionar séries/filmes à lista."""
    try:
        return servico.adicionar_item(lista_id, item.nome)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### 5. Integrar o Router no main.py
```python
# Em main.py, após criar a aplicação FastAPI
from rotas_listas import router_listas

app = FastAPI(title="API de Séries e Filmes com Redis")
app.include_router(router_listas)
```

### 6. Implementar Tratamento de Erros
Adicionar validações e exceções apropriadas:

```python
# Padrão para tratamento de erros
class ErroListaNaoEncontrada(Exception):
    """Lista solicitada não existe."""
    pass

class ErroListaJaExiste(Exception):
    """Lista já existe com este ID."""
    pass

# Em endpoints:
try:
    resultado = servico.operacao()
except ErroListaNaoEncontrada:
    raise HTTPException(status_code=404, detail="Lista não encontrada")
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### 7. Testar e Validar
- [ ] Testar endpoint via `POST /listas` (criar lista)
- [ ] Verificar resposta HTTP e dados em Redis
- [ ] Testar casos de erro (lista não encontrada, dados inválidos)
- [ ] Validar documentação automática em `/docs`

## Padrões Recomendados

### Nomenclatura em Português
```
- Funções: verb_objeto (criar_lista, adicionar_item)
- Variáveis: nome_descritivo (lista_id, dados_lista)
- Chaves Redis: tipo:id (lista:abc123, item:xyz789)
- Classes: NomePascalCase (ServicoLista, ErroListaNaoEncontrada)
```

### Estrutura de Dados (Exemplo)
```json
{
  "id": "uuid",
  "nome": "Minha Lista",
  "itens": [
    {
      "id": "uuid",
      "nome": "Breaking Bad",
      "adicionado_em": "2026-05-19T10:30:00"
    }
  ],
  "publica": false,
  "link_compartilhamento": "abc123xyz",
  "criada_em": "2026-05-19T10:00:00"
}
```

### Exemplo de Método para Requisito RF06 (Publicar)
```python
def publicar_lista(self, lista_id: str) -> dict:
    """RF06: Publica uma lista, gerando link compartilhável."""
    lista = self.obter_lista(lista_id)
    if not lista:
        raise ValueError(f"Lista {lista_id} não encontrada")
    
    lista["publica"] = True
    lista["link_compartilhamento"] = str(uuid.uuid4())[:8]
    
    chave = f"lista:{lista_id}"
    self.redis.set(chave, json.dumps(lista))
    
    return {
        "id": lista_id,
        "publica": True,
        "link": f"/listas/publicas/{lista['link_compartilhamento']}"
    }
```

## Dicas

💡 **Validação**: Use Pydantic models para validar entrada automaticamente  
💡 **Chaves Redis**: Prefixe com tipo de dado (lista:, item:, usuario:) para organizar  
💡 **Exceções**: Crie classes de erro customizadas para diferentes cenários  
💡 **Documentação**: Adicione docstrings em português em todas as funções  
💡 **Testabilidade**: Injete dependências (Redis client) nos serviços para facilitar testes  

## Próximos Passos

Após implementar um requisito:
1. Verifique se algum outro requisito depende deste (verificar em `requisitos.md`)
2. Considere refatorações ou extensões necessárias
3. Documente comportamentos especiais em comentários
4. Teste casos extremos (lista vazia, IDs inválidos, etc.)
