#!/usr/bin/env python3

from flask import Flask, request, jsonify, render_template_string, redirect
import os
from shopee_affiliate import convert_shopee_affiliate_link

# Configuração da aplicação Flask
app = Flask(__name__)

# Template HTML para a página principal
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopee Affiliate Converter</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }
        h1 {
            color: #ee4d2d;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background-color: #ee4d2d;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #d73211;
        }
        .result {
            margin-top: 30px;
            display: {{ 'block' if shopee_url else 'none' }};
        }
        .url-box {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            position: relative;
        }
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #0095f6;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 12px;
        }
        .url-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: #555;
        }
        .url-content {
            word-break: break-all;
            font-family: monospace;
            margin-right: 50px;
        }
        footer {
            margin-top: 40px;
            text-align: center;
            color: #999;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Shopee Affiliate Converter</h1>
        
        <form action="/" method="get">
            <div class="form-group">
                <label for="shopee_url">URL da Shopee:</label>
                <input type="text" id="shopee_url" name="shopee_url" placeholder="Ex: https://shopee.com.br/produto..." value="{{ shopee_url }}" required>
            </div>
            <button type="submit">Converter URL</button>
        </form>
        
        <div class="result">
            {% if shopee_url %}
                <h2 style="text-align: center;">URL Convertida</h2>
                
                <div class="url-box">
                    <div class="url-title">URL de Afiliado:</div>
                    <div class="url-content" id="converted_url">{{ converted_url }}</div>
                    <button class="copy-btn" onclick="copyToClipboard('converted_url')">Copiar</button>
                </div>
            {% endif %}
        </div>
    </div>

    <footer>
        <p>Conversor de Links de Afiliado Shopee © 2023</p>
    </footer>

    <script>
        function copyToClipboard(elementId) {
            const text = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(text).then(() => {
                const button = document.querySelector(`#${elementId}`).nextElementSibling;
                button.innerText = "Copiado!";
                setTimeout(() => {
                    button.innerText = "Copiar";
                }, 2000);
            }).catch(err => {
                console.error('Erro ao copiar texto: ', err);
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    shopee_url = request.args.get('shopee_url', '')
    converted_url = ''
    
    if shopee_url:
        converted_url = convert_shopee_affiliate_link(shopee_url)
    
    return render_template_string(
        HTML_TEMPLATE, 
        shopee_url=shopee_url,
        converted_url=converted_url
    )

@app.route('/api/convert-shopee', methods=['POST'])
def api_convert_shopee():
    """
    API endpoint para converter links da Shopee
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL não fornecida'}), 400
    
    original_url = data['url']
    affiliate_id = data.get('affiliate_id', '18396650603')  # ID padrão se não for fornecido
    
    converted_url = convert_shopee_affiliate_link(original_url, affiliate_id)
    
    return jsonify({
        'original_url': original_url,
        'converted_url': converted_url,
        'affiliate_id': affiliate_id
    })

@app.route('/converter', methods=['GET'])
def convert_simple():
    """
    Rota simples para converter URL via parâmetro de consulta
    """
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400
    
    affiliate_id = request.args.get('id', '18396650603')  # ID padrão se não for fornecido
    converted_url = convert_shopee_affiliate_link(url, affiliate_id)
    
    # Se solicitado como redirecionamento, redireciona para a URL convertida
    if request.args.get('redirect', 'false').lower() == 'true':
        return redirect(converted_url)
    
    # Caso contrário, retorna a URL convertida em JSON
    return jsonify({
        'original_url': url,
        'converted_url': converted_url,
        'affiliate_id': affiliate_id
    })

# Garante que gunicorn encontre a aplicação Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 
