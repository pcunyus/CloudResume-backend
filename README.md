# CloudResume-backend

Python Azure Function API + ARM infrastructure for the [Azure Cloud Resume Challenge](https://cloudresumechallenge.dev/).

## Architecture

- **API**: Azure Function (Python 3.11, v2 programming model) with HTTP trigger
- **Database**: CosmosDB Table API (Serverless capacity mode)
- **IaC**: ARM template (`infra/main.json`)
- **CI/CD**: GitHub Actions — tests → deploy ARM → deploy function

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/counter` | Returns current visitor count |
| `POST` | `/api/counter` | Increments and returns new count |

**Response**: `{"count": 42}`

## Local Development

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r api/requirements.txt
pip install pytest

# Configure local settings
# Edit api/local.settings.json with your CosmosDB connection string

# Run tests
pytest tests/ -v

# Run function locally (requires Azure Functions Core Tools)
cd api
func start
```

## GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `AZURE_CREDENTIALS` | Service principal JSON credentials |
| `AZURE_RG` | Azure resource group name |
| `COSMOS_ACCOUNT_NAME` | CosmosDB account name |
| `AZURE_FUNCTIONAPP_NAME` | Function App name |
| `AZURE_BACKEND_STORAGE_NAME` | Storage account for Functions runtime |
| `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` | Function App publish profile XML |

## Deployment

Infrastructure deploys automatically via GitHub Actions on push to `main`.

Manual deployment:
```bash
az deployment group create \
  --resource-group YOUR_RG \
  --template-file infra/main.json \
  --parameters cosmosAccountName=YOUR_COSMOS functionAppName=YOUR_FUNC storageAccountName=YOUR_STORAGE
```
