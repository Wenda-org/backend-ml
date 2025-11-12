# 🚀 QUICK START - Treinar e Registrar Modelos ML

## ⚡ Comando Único (Tudo de uma vez)

```bash
bash scripts/train_and_register_all.sh
```

Este comando irá:
1. ✅ Verificar dados no banco
2. ✅ Treinar 3 modelos (Recomendações, Clustering, Previsão)
3. ✅ Registrar modelos no banco de dados
4. ✅ Testar endpoints

---

## 📝 Comandos Individuais

### 1. Treinar Modelos

```bash
# Modelo de Recomendações (Content-Based)
python3 scripts/train_recommender.py

# Modelo de Clustering (Perfis de Viajantes)
python3 scripts/train_clustering.py

# Modelo de Previsão (Forecast)
python3 scripts/train_forecast_baseline.py
```

### 2. Registrar no Banco

```bash
python3 scripts/register_models.py
```

### 3. Testar

```bash
# Iniciar servidor
uvicorn app.main:app --reload

# Em outro terminal
bash scripts/test_trained_models.sh
```

---

## ✅ Verificações Rápidas

```bash
# Ver dados no banco
python3 scripts/count_records.py

# Ver modelos salvos
ls -lh models/

# Ver registros no banco
python3 -c "
import asyncio, asyncpg, os
from dotenv import load_dotenv

async def check():
    load_dotenv()
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    models = await conn.fetch('SELECT model_name, version, status FROM ml_models_registry')
    print(f'\n📊 Modelos: {len(models)}\n')
    for m in models:
        print(f'  • {m[\"model_name\"]} v{m[\"version\"]}')
    await conn.close()

asyncio.run(check())
"
```

---

## 📚 Documentação Completa

Ver: **GUIA-TREINAMENTO-ML.md**
