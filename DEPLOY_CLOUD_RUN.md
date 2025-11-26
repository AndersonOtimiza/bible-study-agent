# Deploy Bible Study Agent to Google Cloud Run

Este guia explica como fazer deploy do Bible Study Agent no Google Cloud Run.

## 📋 Pré-requisitos

1. **Conta Google Cloud** com faturamento habilitado
2. **Google Cloud CLI** instalado:

   ```bash
   # Windows (PowerShell como Admin)
   (New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
   & $env:Temp\GoogleCloudSDKInstaller.exe
   ```

3. **Docker** instalado (para build local)

## 🚀 Deploy Passo a Passo

### 1. Configurar Google Cloud

```bash
# Login
gcloud auth login

# Configurar projeto (substitua PROJECT_ID)
gcloud config set project PROJECT_ID

# Habilitar APIs necessárias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Build e Deploy

**Opção A - Deploy Direto (Recomendado):**

```bash
# Deploy direto do código fonte
gcloud run deploy bible-study-agent \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --port 8080
```

**Opção B - Build Manual:**

```bash
# Build da imagem
gcloud builds submit --tag gcr.io/PROJECT_ID/bible-study-agent

# Deploy da imagem
gcloud run deploy bible-study-agent \
  --image gcr.io/PROJECT_ID/bible-study-agent \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2
```

### 3. Configurar Variáveis de Ambiente

```bash
# Configurar chaves de API (opcional)
gcloud run services update bible-study-agent \
  --region us-central1 \
  --set-env-vars="OPENAI_API_KEY=sk-...,ANTHROPIC_API_KEY=sk-ant-..."
```

### 4. Verificar Deploy

```bash
# Obter URL do serviço
gcloud run services describe bible-study-agent --region us-central1 --format="value(status.url)"

# Testar health endpoint
curl https://YOUR-SERVICE-URL/health
```

## ⚙️ Configurações

### Recursos

- **Memória**: 4GB (ajuste conforme necessidade)
- **CPU**: 2 vCPUs
- **Timeout**: 300s (5 minutos)
- **Cold Start**: ~10-20 segundos

### Escala Automática

```bash
# Configurar min/max instances
gcloud run services update bible-study-agent \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 10
```

### Custom Domain

```bash
# Mapear domínio customizado
gcloud run domain-mappings create --service bible-study-agent --domain yourdomain.com --region us-central1
```

## 💰 Custos Estimados

**Free Tier (mensalmente):**

- 2 milhões de requisições
- 360,000 vCPU-segundos
- 180,000 GiB-segundos de memória

**Após Free Tier:**

- ~$0.00001 por requisição
- ~$0.00002400 por vCPU-segundo
- ~$0.00000250 por GiB-segundo

**Exemplo:**

- 100k requisições/mês
- 2 vCPUs, 4GB RAM
- ~$15-30/mês

## 🔒 Segurança

### Autenticação (opcional)

```bash
# Requerer autenticação
gcloud run services update bible-study-agent \
  --region us-central1 \
  --no-allow-unauthenticated

# Criar service account
gcloud iam service-accounts create bible-study-invoker

# Dar permissão
gcloud run services add-iam-policy-binding bible-study-agent \
  --region us-central1 \
  --member="serviceAccount:bible-study-invoker@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Secrets Manager (chaves de API)

```bash
# Criar secret
echo -n "sk-your-key" | gcloud secrets create openai-key --data-file=-

# Usar no Cloud Run
gcloud run services update bible-study-agent \
  --region us-central1 \
  --update-secrets=OPENAI_API_KEY=openai-key:latest
```

## 📊 Monitoramento

### Logs

```bash
# Ver logs em tempo real
gcloud run services logs tail bible-study-agent --region us-central1

# Ou no console
https://console.cloud.google.com/run
```

### Métricas

No Cloud Console:

1. Cloud Run → bible-study-agent
2. Aba "Metrics"
3. Monitore: requests/s, latency, CPU, memory

## 🔄 Atualizações

### Deploy Nova Versão

```bash
# Push para GitHub
git push origin main

# Rebuild e deploy
gcloud run deploy bible-study-agent \
  --source . \
  --region us-central1
```

### Rollback

```bash
# Listar revisões
gcloud run revisions list --service bible-study-agent --region us-central1

# Fazer rollback
gcloud run services update-traffic bible-study-agent \
  --region us-central1 \
  --to-revisions=REVISION_NAME=100
```

## 🐛 Troubleshooting

### Logs de Erro

```bash
# Ver últimos erros
gcloud run services logs read bible-study-agent --region us-central1 --limit 50
```

### Cold Start Lento

```bash
# Manter sempre 1 instância ativa
gcloud run services update bible-study-agent \
  --region us-central1 \
  --min-instances 1
```

### Timeout

```bash
# Aumentar timeout para 15 minutos
gcloud run services update bible-study-agent \
  --region us-central1 \
  --timeout 900
```

## 📚 Recursos

- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Best Practices](https://cloud.google.com/run/docs/tips)

## 🎯 Próximos Passos

1. ✅ Deploy realizado
2. Configure domínio customizado
3. Configure CI/CD com GitHub Actions
4. Habilite Cloud CDN para assets estáticos
5. Configure alertas de monitoramento

---

**URL do Serviço:** Será exibida após o deploy
**Custo Estimado:** ~$15-30/mês (após free tier)
**Uptime:** 99.95% SLA
