# Flask Azure App Service Authentication Example

このリポジトリには、Azure App Service の認証機能（**App Service Authentication / Authorization**、通称 **Easy Auth**）を使用して、ログインしているユーザーの情報を取得するシンプルな Flask アプリケーションが含まれています。

## 概要

この Flask アプリケーションは、Azure App Service の認証機能を利用して、認証されたユーザーの情報を取得し、JSON 形式で表示します。主な機能は以下の通りです：

- **ユーザー認証**: Azure Active Directory (Azure AD) を使用してユーザーを認証。
- **ユーザー情報の取得**: 認証されたユーザーの詳細情報（ユーザーID、ユーザー名、メールアドレスなど）を取得。
- **デプロイ手段**: ZIP ファイルを使用したデプロイ手順を提供。

---

## 取得されるデータ例

`X-MS-CLIENT-PRINCIPAL` ヘッダーをデコードすると、下記のようにユーザー認証情報が含まれる JSON データを取得します（一部の値は伏せ字です）：

```json
{
  "auth_typ": "...",
  "claims": [
    {
      "typ": "aud",
      "val": "..."
    },
    {
      "typ": "iss",
      "val": "..."
    },
    {
      "typ": "name",
      "val": "ユーザー名"
    },
    {
      "typ": "preferred_username",
      "val": "ユーザーのメールアドレス"
    },
    {
      "typ": "exp",
      "val": "..."
    },
    ...
  ],
  ...
}
```

このデータには、以下の情報が含まれます：

- **auth_typ**: 認証の種類。
- **claims**: ユーザーに関連するクレーム情報。
  - **typ**: クレームの種類（例: `name`, `preferred_username`）。
  - **val**: クレームの値（例: ユーザー名、メールアドレス）。

---

## アプリケーションコード

以下は、認証されたユーザーの情報を取得し、JSON 形式で返す Flask アプリケーションのコードです。

```python
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    user = {}
    # App Service Authentication によって設定されるヘッダーからユーザー情報を取得
    if 'X-MS-CLIENT-PRINCIPAL' in request.headers:
        import base64
        import json
        encoded = request.headers.get('X-MS-CLIENT-PRINCIPAL')
        decoded = base64.b64decode(encoded)
        user_info = json.loads(decoded)
        name_claim = next((c["val"] for c in user_info["claims"] if c["typ"] == "name"), None)
        preferred_username_claim = next((c["val"] for c in user_info["claims"] if c["typ"] == "preferred_username"), None)
        user = {
            'user_info': user_info,
            'user_name': name_claim,
            'preferred_username': preferred_username_claim
        }
    return jsonify({
        'message': 'Hello, World!',
        'user': user
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

### コードの説明

- **ヘッダーからのユーザー情報取得**:
  - `X-MS-CLIENT-PRINCIPAL` ヘッダーには、Base64 エンコードされたユーザー情報が含まれています。
  - この情報をデコードし、JSON オブジェクトとして解析します。
  - `name` と `preferred_username` のクレームを抽出し、レスポンスに含めます。

- **レスポンス**:
  - 認証されたユーザーの場合、ユーザー情報を含む JSON を返します。
  - 認証されていない場合は、`user` フィールドが空の JSON を返します。

---