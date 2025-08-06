# config.py

# Confluence instance details
CONFLUENCE_BASE_URL = "https://meesho.atlassian.net"
EMAIL = ""
API_TOKEN = ""
# Optional filters (can be empty string "")
SPACE_KEY = "DEVOPS"  # e.g., "DEVOPS"
CQL_QUERY = 'label=runbook OR title ~ "runbook" OR text ~ "runbook"'# customize if needed

PARENT_PAGE_ID = "2678227022"

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = ""
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_API_DEPLOYMENT_NAME = ""
AZURE_OPENAI_API_VERSION = ""

# Legacy OpenAI (for fallback)
OPENAI_API_KEY = ""