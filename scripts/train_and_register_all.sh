#!/bin/bash
# 🚀 GUIA COMPLETO: Treinar e Registrar Modelos ML
# ================================================

echo "════════════════════════════════════════════════════════════════"
echo "🤖 WENDA ML - GUIA DE TREINAMENTO E REGISTRO DE MODELOS"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Verificar se está no diretório correto
if [ ! -f "app/main.py" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto backend-ml"
    exit 1
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "❌ Erro: Arquivo .env não encontrado"
    echo "💡 Crie um arquivo .env com DATABASE_URL"
    exit 1
fi

echo "✅ Ambiente configurado corretamente"
echo ""

# ════════════════════════════════════════════════════════════════
# ETAPA 1: VERIFICAR DADOS NO BANCO
# ════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ETAPA 1: Verificar dados no banco"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 Verificando se as tabelas ML existem..."
python3 scripts/check-ml-tables.py
echo ""

echo "📈 Contando registros nas tabelas..."
python3 scripts/count_records.py
echo ""

read -p "❓ Deseja continuar com o treinamento? (s/n): " continue_train
if [ "$continue_train" != "s" ]; then
    echo "❌ Treinamento cancelado"
    exit 0
fi

# ════════════════════════════════════════════════════════════════
# ETAPA 2: TREINAR MODELOS
# ════════════════════════════════════════════════════════════════
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 ETAPA 2: Treinar Modelos de Machine Learning"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 2.1 - Modelo de Recomendações (Content-Based)
echo "1️⃣  Treinando modelo de RECOMENDAÇÕES (Content-Based)..."
echo "    📁 Entrada: destinations (do banco de dados)"
echo "    📁 Saída: models/recommender_*.joblib"
echo ""
python3 scripts/train_recommender.py
if [ $? -ne 0 ]; then
    echo "⚠️  Erro no treinamento do modelo de recomendações"
    read -p "Continuar mesmo assim? (s/n): " continue_after_error
    if [ "$continue_after_error" != "s" ]; then
        exit 1
    fi
fi
echo ""
echo "✅ Modelo de recomendações treinado!"
echo ""

# 2.2 - Modelo de Clustering (Perfis de Viajantes)
echo "2️⃣  Treinando modelo de CLUSTERING (Perfis de Viajantes)..."
echo "    📁 Entrada: tourism_statistics (do banco de dados)"
echo "    📁 Saída: models/clustering_*.joblib"
echo ""
python3 scripts/train_clustering.py
if [ $? -ne 0 ]; then
    echo "⚠️  Erro no treinamento do modelo de clustering"
    read -p "Continuar mesmo assim? (s/n): " continue_after_error
    if [ "$continue_after_error" != "s" ]; then
        exit 1
    fi
fi
echo ""
echo "✅ Modelo de clustering treinado!"
echo ""

# 2.3 - Modelo de Previsão (Forecast de Visitantes)
echo "3️⃣  Treinando modelo de PREVISÃO (Forecast de Visitantes)..."
echo "    📁 Entrada: tourism_statistics (do banco de dados)"
echo "    📁 Saída: models/forecast_*.joblib"
echo ""
python3 scripts/train_forecast_baseline.py
if [ $? -ne 0 ]; then
    echo "⚠️  Erro no treinamento do modelo de previsão"
    read -p "Continuar mesmo assim? (s/n): " continue_after_error
    if [ "$continue_after_error" != "s" ]; then
        exit 1
    fi
fi
echo ""
echo "✅ Modelo de previsão treinado!"
echo ""

# ════════════════════════════════════════════════════════════════
# ETAPA 3: VERIFICAR MODELOS CRIADOS
# ════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 ETAPA 3: Verificar Modelos Criados"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 Arquivos criados em models/:"
echo ""
ls -lh models/ 2>/dev/null || echo "⚠️  Diretório models/ não encontrado"
echo ""

# ════════════════════════════════════════════════════════════════
# ETAPA 4: REGISTRAR MODELOS NO BANCO DE DADOS
# ════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 ETAPA 4: Registrar Modelos no Banco de Dados"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Registrando modelos na tabela ml_models_registry..."
echo ""
python3 scripts/register_models.py
if [ $? -ne 0 ]; then
    echo "❌ Erro ao registrar modelos no banco"
    exit 1
fi
echo ""
echo "✅ Modelos registrados no banco com sucesso!"
echo ""

# ════════════════════════════════════════════════════════════════
# ETAPA 5: TESTAR MODELOS
# ════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 ETAPA 5: Testar Modelos"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚡ Iniciando servidor em background para testes..."
echo ""

# Verificar se servidor já está rodando
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Servidor já está rodando na porta 8000"
    SERVER_STARTED=false
else
    echo "🚀 Iniciando servidor..."
    uvicorn app.main:app --reload &
    SERVER_PID=$!
    SERVER_STARTED=true
    echo "⏳ Aguardando servidor iniciar..."
    sleep 5
fi

echo ""
echo "🧪 Executando testes dos modelos..."
echo ""
bash scripts/test_trained_models.sh

if [ "$SERVER_STARTED" = true ]; then
    echo ""
    echo "🛑 Parando servidor de testes..."
    kill $SERVER_PID 2>/dev/null
fi

# ════════════════════════════════════════════════════════════════
# RESUMO FINAL
# ════════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🎉 TREINAMENTO E REGISTRO CONCLUÍDO COM SUCESSO!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 MODELOS TREINADOS:"
echo "   ✅ 1. Recomendações (Content-Based)"
echo "   ✅ 2. Clustering (Perfis de Viajantes)"
echo "   ✅ 3. Previsão (Forecast de Visitantes)"
echo ""
echo "💾 REGISTROS NO BANCO:"
echo "   ✅ Modelos salvos em ml_models_registry"
echo "   ✅ Métricas e versões registradas"
echo ""
echo "📁 ARQUIVOS GERADOS:"
echo "   • models/recommender_similarity_matrix.npy"
echo "   • models/recommender_features.npy"
echo "   • models/recommender_tfidf.joblib"
echo "   • models/recommender_scaler.joblib"
echo "   • models/recommender_metadata.json"
echo "   • models/clustering_model.joblib"
echo "   • models/clustering_scaler.joblib"
echo "   • models/clustering_metadata.json"
echo "   • models/forecast_*.joblib (por província)"
echo "   • models/training_summary.json"
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo "   1. Inicie o servidor: uvicorn app.main:app --reload"
echo "   2. Acesse: http://localhost:8000/docs"
echo "   3. Teste os endpoints de ML"
echo ""
echo "════════════════════════════════════════════════════════════════"
