#conftest.py
#Pytest configuration — adds backend module directories to sys.path and stubs out
#credential-dependent imports so unit tests run without OAuth tokens or API keys.

import os
import sys
from unittest.mock import MagicMock

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

#Each module folder is added so tests can do `import gmail_api` etc. directly.
sys.path.insert(0, os.path.join(backend_dir, 'Gmail'))
sys.path.insert(0, os.path.join(backend_dir, 'Outlook'))
sys.path.insert(0, os.path.join(backend_dir, 'ai'))
sys.path.insert(0, os.path.join(backend_dir, 'database'))

#Stub Google_API before gmail_api is imported — prevents OAuth flow from running.
sys.modules['Google_API'] = MagicMock()

#Stub MS_Graph before outlook_api is imported — prevents MSAL token fetch.
ms_graph_stub = MagicMock()
ms_graph_stub.MS_GRAPH_BASE_ENDPOINT = 'https://graph.microsoft.com/v1.0/'
sys.modules['MS_Graph'] = ms_graph_stub

#Set a dummy OpenAI key so the OpenAI client can be instantiated without raising.
os.environ.setdefault('OPENAI_API_KEY', 'test-dummy-key-for-unit-tests')
