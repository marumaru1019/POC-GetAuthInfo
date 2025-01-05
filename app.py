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
        user = {
            'user_id': user_info.get('userId'),
            'user_details': user_info.get('userDetails'),
            'user_roles': user_info.get('userRoles'),
            'identity_provider': user_info.get('identityProvider'),
            'claims': user_info.get('userClaims')
        }
    return jsonify({
        'message': 'Hello, World!',
        'user': user
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
