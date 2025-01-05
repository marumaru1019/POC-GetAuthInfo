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
