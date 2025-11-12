# Tabelas Necessárias para o Backend ML

## 📋 Resumo

O backend de ML (`backend-ml`) precisa de **5 tabelas** para funcionar:

### ✅ Tabelas Compartilhadas (já devem existir no backend CRUD):
1. **users** - Tabela de usuários
2. **destinations** - Tabela de destinos turísticos

### 🆕 Tabelas Específicas do ML (precisam ser criadas):
3. **tourism_statistics** - Estatísticas de turismo por província/mês/ano
4. **ml_models_registry** - Registro de modelos de ML treinados
5. **ml_predictions** - Previsões geradas pelos modelos
6. **recommendations_log** - Log de recomendações geradas para usuários

---

## 🚀 Opção 1: Adicionar ao Prisma Schema (RECOMENDADO)

### Passo 1: Adicionar ao `schema.prisma` do backend CRUD

Copie os seguintes models para o seu `schema.prisma`:

```prisma
// TABELA 1: Estatísticas de Turismo
model TourismStatistics {
  id                Int      @id @default(autoincrement())
  province          String   @db.VarChar(100)
  month             Int
  year              Int
  domesticVisitors  Int?     @map("domestic_visitors")
  foreignVisitors   Int?     @map("foreign_visitors")
  occupancyRate     Float?   @map("occupancy_rate") @db.DoublePrecision
  avgStayDays       Float?   @map("avg_stay_days") @db.DoublePrecision
  createdAt         DateTime @default(now()) @map("created_at")

  @@map("tourism_statistics")
}

// TABELA 2: Registro de Modelos ML
model MLModelsRegistry {
  id          Int       @id @default(autoincrement())
  modelName   String    @map("model_name") @db.VarChar(100)
  version     String    @db.VarChar(20)
  algorithm   String?   @db.VarChar(100)
  metrics     Json?     @db.JsonB
  status      String    @default("active") @db.VarChar(20)
  trainedOn   DateTime? @map("trained_on") @db.Date
  lastUpdated DateTime  @default(now()) @map("last_updated")

  @@map("ml_models_registry")
}

// TABELA 3: Previsões ML
model MLPredictions {
  id                  Int      @id @default(autoincrement())
  modelName           String   @map("model_name") @db.VarChar(100)
  modelVersion        String?  @map("model_version") @db.VarChar(20)
  province            String   @db.VarChar(100)
  month               Int
  year                Int
  predictedVisitors   Int?     @map("predicted_visitors")
  confidenceInterval  Json?    @map("confidence_interval") @db.JsonB
  createdAt           DateTime @default(now()) @map("created_at")

  @@map("ml_predictions")
}

// TABELA 4: Log de Recomendações
model RecommendationsLog {
  id            Int      @id @default(autoincrement())
  userId        String?  @map("user_id") @db.Uuid
  destinationId String?  @map("destination_id") @db.Uuid
  score         Float?   @db.DoublePrecision
  modelVersion  String?  @map("model_version") @db.VarChar(20)
  createdAt     DateTime @default(now()) @map("created_at")

  user        User?        @relation(fields: [userId], references: [id])
  destination Destination? @relation(fields: [destinationId], references: [id])

  @@map("recommendations_log")
}
```

### Passo 2: Adicionar relacionamentos aos models existentes

No seu model **User**, adicione:
```prisma
model User {
  // ... campos existentes ...
  
  recommendations RecommendationsLog[]
}
```

No seu model **Destination**, adicione:
```prisma
model Destination {
  // ... campos existentes ...
  
  recommendations RecommendationsLog[]
}
```

### Passo 3: Executar migration

```bash
npx prisma migrate dev --name add_ml_tables
npx prisma generate
```

---

## 🔧 Opção 2: SQL Direto (Alternativa)

Se preferir executar SQL diretamente no banco:

```bash
# No backend-ml
psql $DATABASE_URL -f sql-ml-tables.sql
```

Ou execute o arquivo `sql-ml-tables.sql` manualmente no seu cliente PostgreSQL.

---

## 📊 Campos Mínimos Necessários

### Na tabela `users`:
- ✅ `id` (UUID)
- ✅ `name` (String)
- ✅ `email` (String)
- ✅ `password_hash` (String, nullable)
- ✅ `role` (String)
- ✅ `country` (String, nullable)
- ✅ `created_at` (DateTime)

### Na tabela `destinations`:
- ✅ `id` (UUID)
- ✅ `name` (String)
- ✅ `province` (String, nullable)
- ✅ `description` (Text, nullable)
- ✅ `latitude` (Float, nullable)
- ✅ `longitude` (Float, nullable)
- ✅ `category` (String, nullable)
- ✅ `rating_avg` (Float, nullable)
- ✅ `images` (JSON, nullable)
- ✅ `created_at` (DateTime)

---

## ✅ Verificação

Após criar as tabelas, verifique:

```bash
# No backend-ml
python3 scripts/check-tables.py
```

Deve mostrar pelo menos estas tabelas:
- ✅ users
- ✅ destinations
- ✅ tourism_statistics
- ✅ ml_models_registry
- ✅ ml_predictions
- ✅ recommendations_log

---

## 📝 Notas Importantes

1. **Não delete `users` e `destinations`** - São compartilhadas entre os backends
2. As 4 tabelas ML são específicas do backend-ml e não afetam o backend CRUD
3. Se você já tem dados em `users` e `destinations`, eles serão preservados
4. A tabela `recommendations_log` faz foreign key para `users` e `destinations`

---

## 🎯 Arquivos de Referência

- `prisma-schema-ml-tables.prisma` - Schema Prisma completo
- `sql-ml-tables.sql` - SQL direto para criar tabelas
- `README-ML-TABLES.md` - Este documento
