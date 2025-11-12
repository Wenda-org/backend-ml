# 📝 Adaptações Realizadas no Backend ML

## Mudanças do Schema do Banco de Dados

Baseado no novo schema Prisma em `docs/db.txt`, as seguintes adaptações foram feitas:

---

## ✅ Arquivos Modificados

### 1. **app/models.py** - Modelos SQLAlchemy

#### User Model:
- ✅ `id`: UUID → String (Prisma usa String para UUID)
- ✅ `role`: Enum alterado de `tourist/operator/admin` → `user/admin`
- ✅ `country`: Campo removido (não existe mais no novo schema)
- ✅ `email`: VarChar(120) → VarChar(255)
- ✅ `password_hash`: Adicionado `name="password_hash"` para mapear corretamente

#### Destination Model:
- ✅ `id`: UUID → String
- ✅ `name`: VarChar(150) → VarChar(200)
- ✅ `province`: Nullable → NOT NULL, VarChar(100) → VarChar(50)
- ✅ `description`: Nullable → NOT NULL
- ✅ `latitude/longitude`: Float → Numeric (Decimal no Prisma)
- ✅ `category`: Removido - substituído por `category_id` (FK para categories)
- ✅ `rating_avg`: Removido - substituído por `rating` (Decimal 2,1)
- ✅ `images`: Campo removido (agora é tabela separada destination_images)

#### RecommendationsLog Model:
- ✅ `user_id`: UUID → String
- ✅ `destination_id`: UUID → String
- ✅ Adicionado `name=""` para todos os campos snake_case

---

### 2. **app/api/ml.py** - API Endpoints

#### DestinationRecommendation (Pydantic Model):
- ✅ `rating_avg` → `rating`

#### Endpoint `/recommend` (linha 267-291):
- ✅ `rec['rating_avg']` → `rec.get('rating')`
- ✅ Verificação de rating: `rec['rating_avg'] >= 4.5` → `rec.get('rating') and rec['rating'] >= 4.5`

#### Endpoint `/recommend-by-preferences` (linha 300-360):
- ✅ Query filter: `Destination.category.in_()` → `Destination.category_id.in_()`
- ✅ Order by: `Destination.rating_avg.desc()` → `Destination.rating.desc()`
- ✅ Score calculation: `dest.rating_avg` → `float(dest.rating)` com conversão de Decimal
- ✅ Comparison: `dest.category` → `dest.category_id`
- ✅ Response: `rating_avg=dest.rating_avg` → `rating=float(dest.rating)`

---

### 3. **app/services/recommender.py** - Serviço de Recomendações

#### Método `recommend_similar()` (linha 120-135):
- ✅ Suporte para ambos formatos (compatibilidade retroativa):
  - `dest.get('category', dest.get('category_id'))`
  - `dest.get('rating', dest.get('rating_avg'))`

#### Método `recommend_by_preferences()` (linha 160-200):
- ✅ Filtro de categoria: suporta ambos `category` e `category_id`
- ✅ Filtro de rating: suporta ambos `rating` e `rating_avg`
- ✅ Ordenação: usa `rating` ou `rating_avg` como fallback
- ✅ Response: retorna `rating` em vez de `rating_avg`

---

### 4. **scripts/train_recommender.py** - Script de Treinamento

#### Query de busca (linha 47-52):
- ✅ Query atualizada:
  ```sql
  SELECT d.id, d.name, d.province, c.slug as category, d.description, 
         CAST(d.rating AS FLOAT) as rating
  FROM destinations d
  LEFT JOIN categories c ON d.category_id = c.id
  WHERE d.is_active = true AND d.deleted_at IS NULL
  ```
- ✅ JOIN com tabela `categories` para obter o slug da categoria
- ✅ Conversão de `rating` (Decimal) para Float
- ✅ Filtros de `is_active` e `deleted_at` adicionados

#### Processamento de dados:
- ✅ `df['rating_avg']` → `df['rating']` (todas as ocorrências)
- ✅ Preenchimento de valores: `df['category'].fillna('other')` adicionado

#### Metadata (linha 266):
- ✅ Campo salvo: `'rating_avg'` → `'rating'`

---

## 🔄 Compatibilidade Retroativa

O código foi adaptado para suportar AMBOS os formatos quando possível:

```python
# Exemplo no recommender.py
dest_category = dest.get('category', dest.get('category_id'))
dest_rating = dest.get('rating', dest.get('rating_avg', 0))
```

Isso permite que:
- ✅ Modelos antigos já treinados continuem funcionando
- ✅ Novos modelos usem o novo formato
- ✅ Transição suave entre schemas

---

## ⚠️ Campos Removidos/Alterados

### Removidos do User:
- ❌ `country` - não existe mais

### Removidos do Destination:
- ❌ `category` (string) - agora é `category_id` (FK)
- ❌ `rating_avg` (float) - agora é `rating` (Decimal 2,1)
- ❌ `images` (JSONB) - agora é tabela `destination_images`

### Novos no Destination:
- ✅ `category_id` - Foreign Key para `categories.id`
- ✅ `slug` - URL-friendly identifier
- ✅ `long_description` - Descrição detalhada
- ✅ `review_count` - Contador de reviews
- ✅ `view_count` - Contador de visualizações
- ✅ `is_featured` - Destaque
- ✅ `is_active` - Ativo/Inativo
- ✅ `deleted_at` - Soft delete

---

## 🧪 Testes Necessários

Após essas mudanças, você deve:

1. ✅ Verificar se as tabelas existem no banco:
   ```bash
   python3 scripts/check-ml-tables.py
   ```

2. ✅ Re-treinar o modelo de recomendações:
   ```bash
   python3 scripts/train_recommender.py
   ```

3. ✅ Testar os endpoints da API:
   ```bash
   # Iniciar servidor
   uvicorn app.main:app --reload
   
   # Testar
   curl http://localhost:8000/api/ml/recommend-by-preferences
   ```

---

## 📌 Notas Importantes

1. **IDs são agora Strings**: O Prisma gera UUIDs como strings, não como objetos UUID
2. **Decimal vs Float**: Campos `rating`, `latitude`, `longitude` são Decimal no banco
3. **Relacionamentos**: `category` agora é um relacionamento, não um campo direto
4. **Soft Deletes**: Use `is_active` e `deleted_at` para filtros
5. **Enums**: `UserRole` agora é apenas `user` ou `admin` (sem `tourist`/`operator`)

---

## ✨ Benefícios das Mudanças

- ✅ Schema mais normalizado (categorias em tabela separada)
- ✅ Melhor precisão para ratings (Decimal 2,1 = 0.0 a 5.0)
- ✅ Coordenadas mais precisas (Decimal em vez de Float)
- ✅ Suporte a soft deletes
- ✅ Melhor rastreamento (view_count, review_count)
- ✅ URLs amigáveis (slug)
