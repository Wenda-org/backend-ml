# 📋 COPIAR E COLAR - Tabelas ML para Prisma

## ✂️ O QUE COPIAR

Copie **EXATAMENTE** este código e cole no final do seu `schema.prisma` do backend CRUD:

```prisma
// ============================================
// TABELAS DO BACKEND ML
// ============================================

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

---

## ✏️ O QUE MODIFICAR

### No model `User` (encontre e adicione):

**ANTES:**
```prisma
model User {
  // ... campos existentes ...
  
  reviews         Review[]
  favorites       Favorite[]
  trips           Trip[]
  
  @@map("users")
}
```

**DEPOIS:**
```prisma
model User {
  // ... campos existentes ...
  
  reviews         Review[]
  favorites       Favorite[]
  trips           Trip[]
  recommendations RecommendationsLog[]  // ⬅️ ADICIONAR ESTA LINHA
  
  @@map("users")
}
```

---

### No model `Destination` (encontre e adicione):

**ANTES:**
```prisma
model Destination {
  // ... campos existentes ...
  
  reviews            Review[]
  favorites          Favorite[]
  tripDestinations   TripDestination[]
  
  @@map("destinations")
}
```

**DEPOIS:**
```prisma
model Destination {
  // ... campos existentes ...
  
  reviews            Review[]
  favorites          Favorite[]
  tripDestinations   TripDestination[]
  recommendations    RecommendationsLog[]  // ⬅️ ADICIONAR ESTA LINHA
  
  @@map("destinations")
}
```

---

## 🚀 EXECUTAR

Depois de copiar e modificar, execute:

```bash
cd /caminho/do/backend-crud

# Criar migration
npx prisma migrate dev --name add_ml_tables

# Gerar Prisma Client
npx prisma generate

# Aplicar ao banco
npx prisma migrate deploy
```

---

## ✅ VERIFICAR

Volte ao backend-ml e verifique:

```bash
cd /caminho/do/backend-ml
python3 scripts/check-ml-tables.py
```

Deve mostrar: **🎉 TODAS AS TABELAS NECESSÁRIAS ESTÃO PRESENTES!**

---

## 🆘 ALTERNATIVA (SQL Direto)

Se não quiser usar Prisma, execute direto no banco:

```bash
psql $DATABASE_URL -f sql-ml-tables.sql
```

Ou copie o conteúdo de `sql-ml-tables.sql` e execute no seu cliente PostgreSQL favorito.
