"""MCP client 的 OAuth 設定。

token 必須持久化，否則每次跑都要重開瀏覽器授權一次。但存哪裡有講究：

- **不要用 Windows 認證管理員（keyring）。** 單筆憑證上限 2560 bytes，而 keyring
  用 UTF-16 存，等於**只能放 1280 個字元**（實測 1280 OK、1281 就失敗）。
  OAuth 的 access_token + refresh_token 輕鬆超過，CredWrite 會回 WinError 1783。
- 改用**加密檔案**：FileTreeStore 沒有大小限制，外面包一層 Fernet。
  金鑰由 OAUTH_STORAGE_KEY 推導 —— 放 .env，已被 .gitignore 擋住。
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp.client.auth import OAuth
from key_value.aio.stores.filetree import FileTreeStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper

load_dotenv()

TOKEN_DIR = Path.home() / ".agent-lab" / "oauth-tokens"

# salt 不需要保密，只要固定且唯一就行 —— 它的作用是讓同一組密語推導出不同的金鑰。
SALT = "agent-lab-v1"


def make_oauth() -> OAuth:
    """建立會把 token 加密存到磁碟的 OAuth。"""
    return OAuth(
        token_storage=FernetEncryptionWrapper(
            key_value=FileTreeStore(data_directory=TOKEN_DIR),
            source_material=os.environ["OAUTH_STORAGE_KEY"],
            salt=SALT,
        )
    )
