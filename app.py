from flask import Flask, request, jsonify
import os
import msal
import time
import requests
import base64
import json

app = Flask(__name__)

@app.route('/')
def home():
    user = {}
    if 'X-MS-CLIENT-PRINCIPAL' in request.headers:
        # 初期トークン情報をヘッダーから取得
        encoded = request.headers.get('X-MS-CLIENT-PRINCIPAL')
        jwt_id_token = request.headers.get('X-MS-TOKEN-AAD-ID-TOKEN')
        jwt_access_token = request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN')
        expires_on = request.headers.get('X-MS-TOKEN-AAD-EXPIRES-ON')

        # 有効期限（秒）の数値変換（取得できなければ0）
        # try:
        #     expires_on_int = int(expires_on) if expires_on else 0
        # except ValueError:
        #     expires_on_int = 0

        # # トークンの残り有効期間が300秒未満の場合にリフレッシュ処理を行う
        # if expires_on_int and (expires_on_int - time.time() < 300):
        refresh_url = f"https://{request.host}/.auth/refresh"

        session_cookie = request.cookies.get('AppServiceAuthSession')
        cookies = {'AppServiceAuthSession': session_cookie} if session_cookie else request.cookies
                
        refresh_resp = requests.get(refresh_url, cookies=cookies)
        print("------------- Refresh Response -------------")
        print(refresh_resp.status_code, refresh_resp.text)
        
        if refresh_resp.status_code == 200:
            # refresh自体は更新結果を返さないので、/.auth/meで最新のトークン情報を取得
            me_url = f"https://{request.host}/.auth/me"
            me_resp = requests.get(me_url, cookies=cookies)
            if me_resp.status_code == 200:
                me_data = me_resp.json()
                # 通常、me_dataは認証プロバイダー毎の情報がリストになっているので、最初の要素を利用
                if isinstance(me_data, list) and len(me_data) > 0:
                    provider_data = me_data[0]
                    jwt_id_token = provider_data.get("id_token", jwt_id_token)
                    jwt_access_token = provider_data.get("access_token", jwt_access_token)
                    expires_on = provider_data.get("expires_on", expires_on)
                    print("トークンのリフレッシュに成功しました")
            else:
                print("更新後のトークン取得に失敗しました:", me_resp.text)
        else:
            print("トークンのリフレッシュに失敗しました:", refresh_resp.text)

        # On-Behalf-Ofフロー用のMSAL設定
        CLIENT_ID = os.environ.get('CLIENT_ID')
        CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
        TENANT_ID = os.environ.get('TENANT_ID')
        AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
        SCOPE = ["User.Read"]

        msal_app = msal.ConfidentialClientApplication(
            client_id=CLIENT_ID,
            client_credential=CLIENT_SECRET,
            authority=AUTHORITY,
        )

        # On-Behalf-OfフローではIDトークンをアサーションとして利用
        result = msal_app.acquire_token_on_behalf_of(jwt_id_token, scopes=SCOPE)
        try:
            access_token = result["access_token"]
            decoded = base64.b64decode(encoded)
            user_info = json.loads(decoded)
            name_claim = next((c["val"] for c in user_info.get("claims", []) if c.get("typ") == "name"), None)
            preferred_username_claim = next((c["val"] for c in user_info.get("claims", []) if c.get("typ") == "preferred_username"), None)
            user = {
                'user_info': user_info,
                'user_name': name_claim,
                'jwt_id_token': jwt_id_token,
                'jwt_access_token': jwt_access_token,
                'preferred_username': preferred_username_claim,
                "access_token": access_token,
                "token_expires_on": expires_on
            }
        except Exception as e:
            user = {
                'error': str(e),
                "result": result
            }
    return jsonify({
        'message': 'Hello, World!',
        'user': user
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
