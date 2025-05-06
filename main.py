#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_file, render_template_string, redirect, url_for
import os
import io
import base64
import json
import time
from get_profile_pic import get_instagram_profile_pic
from shopee_affiliate import convert_shopee_affiliate_link

# Configuração da aplicação Flask
app = Flask(__name__)

# Diretório para cache de imagens
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Template HTML para a página principal
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram URL & Shopee Affiliate Converter</title>
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
            color: #e1306c;
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
            background-color: #e1306c;
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
            background-color: #c13584;
        }
        .result {
            margin-top: 30px;
            display: {{ 'block' if username else 'none' }};
        }
        .shopee-result {
            margin-top: 30px;
            display: {{ 'block' if shopee_url else 'none' }};
        }
        .profile-pic {
            display: block;
            max-width: 150px;
            border-radius: 50%;
            margin: 0 auto 20px;
            border: 3px solid #e1306c;
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
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            margin-right: 5px;
            border-radius: 4px 4px 0 0;
            font-weight: 600;
        }
        .tab.active {
            background-color: #e1306c;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .shopee-color {
            color: #ee4d2d;
        }
    </style>
</head>
<body>
    <div class="tabs">
        <div class="tab active" onclick="switchTab('instagram')">Instagram URL</div>
        <div class="tab" onclick="switchTab('shopee')">Shopee Afiliado</div>
    </div>
    
    <div id="instagram-tab" class="tab-content active">
        <div class="container">
            <h1>Instagram URL Converter</h1>
            
            <form action="/" method="get">
                <div class="form-group">
                    <label for="username">Nome de usuário do Instagram:</label>
                    <input type="text" id="username" name="username" placeholder="Ex: instagram" value="{{ username }}" required>
                </div>
                <button type="submit">Obter URLs</button>
            </form>
            
            <div class="result">
                {% if username %}
                    <h2 style="text-align: center;">Resultados para @{{ username }}</h2>
                    <img src="/image/{{ username }}" class="profile-pic" alt="{{ username }} profile picture">
                    
                    <div class="url-box">
                        <div class="url-title">URL Direta da Imagem:</div>
                        <div class="url-content" id="url1">{{ request.url_root }}image/{{ username }}.jpg</div>
                        <button class="copy-btn" onclick="copyToClipboard('url1')">Copiar</button>
                    </div>
                    
                    <div class="url-box">
                        <div class="url-title">URL para API (JSON):</div>
                        <div class="url-content" id="url2">{{ request.url_root }}api/profile-pic/{{ username }}</div>
                        <button class="copy-btn" onclick="copyToClipboard('url2')">Copiar</button>
                    </div>
                    
                    <div class="url-box">
                        <div class="url-title">Tag HTML para Imagem:</div>
                        <div class="url-content" id="url3">&lt;img src="{{ request.url_root }}image/{{ username }}.jpg" alt="{{ username }} profile picture"&gt;</div>
                        <button class="copy-btn" onclick="copyToClipboard('url3')">Copiar</button>
                    </div>
                    
                {% endif %}
            </div>
        </div>
    </div>
    
    <div id="shopee-tab" class="tab-content">
        <div class="container">
            <h1><span class="shopee-color">Shopee</span> Affiliate Converter</h1>
            
            <form action="/" method="get">
                <div class="form-group">
                    <label for="shopee_url">URL do produto Shopee:</label>
                    <input type="text" id="shopee_url" name="shopee_url" placeholder="Ex: https://shopee.com.br/product/..." value="{{ shopee_url }}" required>
                </div>
                <div class="form-group">
                    <label for="affiliate_id">Seu ID de afiliado (opcional):</label>
                    <input type="text" id="affiliate_id" name="affiliate_id" placeholder="Ex: 18396650603" value="{{ affiliate_id or '18396650603' }}">
                </div>
                <button type="submit">Converter URL</button>
            </form>
            
            <div class="shopee-result">
                {% if shopee_url %}
                    <h2 style="text-align: center;">URL Convertida</h2>
                    
                    <div class="url-box">
                        <div class="url-title">URL Original:</div>
                        <div class="url-content" id="original_url">{{ shopee_url }}</div>
                        <button class="copy-btn" onclick="copyToClipboard('original_url')">Copiar</button>
                    </div>
                    
                    <div class="url-box">
                        <div class="url-title">URL Convertida com seu ID de afiliado:</div>
                        <div class="url-content" id="converted_url">{{ converted_shopee_url }}</div>
                        <button class="copy-btn" onclick="copyToClipboard('converted_url')">Copiar</button>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <footer>
        <p>Esta ferramenta extrai URLs diretas de imagens de perfil do Instagram e converte links de afiliado da Shopee.</p>
    </footer>
    
    <script>
        function copyToClipboard(elementId) {
            const element = document.getElementById(elementId);
            const text = element.innerText;
            
            navigator.clipboard.writeText(text).then(() => {
                const button = element.nextElementSibling;
                const originalText = button.innerText;
                button.innerText = 'Copiado!';
                setTimeout(() => {
                    button.innerText = originalText;
                }, 2000);
            });
        }
        
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Activate the selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Activate the selected tab button
            document.querySelectorAll('.tab').forEach(tab => {
                if (tab.textContent.toLowerCase().includes(tabName)) {
                    tab.classList.add('active');
                }
            });
        }
        
        // Check if we need to activate a specific tab based on URL parameters
        window.onload = function() {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('shopee_url')) {
                switchTab('shopee');
            } else if (urlParams.has('username')) {
                switchTab('instagram');
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Rota principal da aplicação"""
    username = request.args.get('username', '')
    shopee_url = request.args.get('shopee_url', '')
    affiliate_id = request.args.get('affiliate_id', '18396650603')
    
    converted_shopee_url = ''
    if shopee_url:
        converted_shopee_url = convert_shopee_affiliate_link(shopee_url, affiliate_id)
    
    return render_template_string(
        HTML_TEMPLATE, 
        username=username, 
        shopee_url=shopee_url,
        affiliate_id=affiliate_id,
        converted_shopee_url=converted_shopee_url,
        request=request
    )


@app.route('/image/<username>')
@app.route('/image/<username>.jpg')  # Rota que termina com .jpg
@app.route('/image/<username>.png')  # Rota que termina com .png
def get_image(username):
    """Rota para servir a imagem de perfil diretamente"""
    # Remove extensões do username se estiverem presentes
    if username.endswith(('.jpg', '.png')):
        username = username.rsplit('.', 1)[0]
        
    try:
        # Verifica o cache primeiro
        cache_file = os.path.join(CACHE_DIR, f"{username}_profile_pic.jpg")
        
        # Se o cache tem mais de 1 dia ou não existe, atualize-o
        if not os.path.exists(cache_file) or \
           (os.path.exists(cache_file) and \
            (os.path.getmtime(cache_file) < time.time() - 86400)):
            
            # Obtém imagem nova e salva no cache
            get_instagram_profile_pic(username, output_format='file', save_dir=CACHE_DIR)
        
        return send_file(cache_file, mimetype='image/jpeg')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile-pic/<username>')
def api_profile_pic(username):
    """API endpoint para obter informações da imagem de perfil"""
    try:
        format_type = request.args.get('format', 'url')
        
        if format_type not in ['url', 'base64', 'json']:
            return jsonify({'error': 'Formato inválido. Use "url", "base64" ou "json"'}), 400
        
        result = get_instagram_profile_pic(username, output_format=format_type)
        
        # Para o formato URL, garantimos que ela termine com .jpg
        if format_type == 'url' and not result.endswith('.jpg'):
            if '?' in result:
                result = result.split('?')[0]
            if not result.endswith('.jpg'):
                result += '.jpg'
        
        return jsonify({
            'username': username,
            'format': format_type,
            'result': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/convert-shopee', methods=['POST'])
def api_convert_shopee():
    """API endpoint para converter links de afiliado da Shopee"""
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'URL não fornecida'}), 400
        
        shopee_url = data['url']
        affiliate_id = data.get('affiliate_id', '18396650603')
        
        converted_url = convert_shopee_affiliate_link(shopee_url, affiliate_id)
        
        return jsonify({
            'original_url': shopee_url,
            'converted_url': converted_url,
            'affiliate_id': affiliate_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/converter', methods=['GET'])
def convert_simple():
    """Endpoint simples para converter links via GET para uso em integrações"""
    try:
        # Obter a URL da query string
        url = request.args.get('url', '')
        # Se não foi fornecida URL, redirecionar para página principal
        if not url:
            return redirect('/')
            
        # Obter o ID de afiliado da query string ou usar o padrão
        affiliate_id = request.args.get('id', '18396650603')
        
        # Converter a URL
        converted_url = convert_shopee_affiliate_link(url, affiliate_id)
        
        # Se o usuário solicitou apenas o texto da URL
        if request.args.get('text_only', 'false').lower() == 'true':
            return converted_url
            
        # Opcional: retornar um HTML básico para exibir e copiar a URL
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>URL Convertida</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .url-box {
                    background-color: #f8f9fa;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 15px 0;
                    word-break: break-all;
                    position: relative;
                }
                .copy-btn {
                    background-color: #0095f6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 15px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-top: 10px;
                }
                h1 {
                    color: #ee4d2d;
                }
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .back-btn {
                    background-color: #f0f0f0;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    cursor: pointer;
                    text-decoration: none;
                    color: #333;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>URL Convertida</h1>
                    <a href="/" class="back-btn">Voltar</a>
                </div>
                
                <div class="url-box">
                    <h3>URL Original:</h3>
                    <div id="original-url">{{ original_url }}</div>
                    <button class="copy-btn" onclick="copyToClipboard('original-url')">Copiar URL Original</button>
                </div>
                
                <div class="url-box">
                    <h3>URL com seu ID de Afiliado:</h3>
                    <div id="converted-url">{{ converted_url }}</div>
                    <button class="copy-btn" onclick="copyToClipboard('converted-url')">Copiar URL Convertida</button>
                </div>
            </div>
            
            <script>
                function copyToClipboard(elementId) {
                    const element = document.getElementById(elementId);
                    const text = element.innerText;
                    
                    navigator.clipboard.writeText(text).then(() => {
                        const button = element.nextElementSibling;
                        const originalText = button.innerText;
                        button.innerText = 'Copiado!';
                        setTimeout(() => {
                            button.innerText = originalText;
                        }, 2000);
                    });
                }
            </script>
        </body>
        </html>
        ''', original_url=url, converted_url=converted_url)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para integrações com bots de WhatsApp ou outros serviços"""
    try:
        data = request.json
        
        # Verifique a estrutura de dados do seu webhook específico
        # Isto é apenas um exemplo. Adapte conforme o serviço que você usar
        if 'message' in data and 'text' in data['message']:
            message_text = data['message']['text']
            
            # Procurar por URLs da Shopee no texto
            import re
            shopee_urls = re.findall(r'https?://[^\s]+shopee[^\s]+', message_text)
            shopee_urls.extend(re.findall(r'https?://s\.shopee[^\s]+', message_text))
            
            if shopee_urls:
                # Converter o primeiro link encontrado
                original_url = shopee_urls[0]
                converted_url = convert_shopee_affiliate_link(original_url)
                
                return jsonify({
                    'success': True,
                    'original_url': original_url,
                    'converted_url': converted_url
                })
            
            return jsonify({
                'success': False,
                'error': 'Nenhum link da Shopee encontrado na mensagem'
            })
        
        return jsonify({
            'success': False,
            'error': 'Formato de mensagem não reconhecido'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 