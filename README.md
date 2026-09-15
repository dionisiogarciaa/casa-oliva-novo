# Casa Oliva — Backend Flask + SQLite

Backend em um único arquivo (`app.py`), sem ORM. Na primeira execução,
cria o banco `casa_oliva.sqlite3` e popula os 150 produtos automaticamente.

## Executar

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000

## Rotas

- `GET  /api/products` — lista os 150 produtos do cardápio (id, nome, descrição, preço, categoria, imagem).
- `POST /api/orders` — recebe `cliente`, `mesa`, `pagamento`, `observacoes` (opcional), `taxa_servico` (bool) e `itens` (lista de `{produto_id, quantidade}`); calcula subtotal, os 10% do garçom (se marcado) e o total, e grava o pedido no banco.

## Estrutura

- `app.py` — schema do banco, seed dos 150 produtos e as 3 rotas (tudo em um arquivo só).
- `templates/index.html` — interface do cardápio (sem alterações).
- `static/script.js` / `static/styles.css` — lógica e estilo do front-end (sem alterações).
- `casa_oliva.sqlite3` — criado automaticamente ao rodar `python app.py` (não precisa subir pro git).
