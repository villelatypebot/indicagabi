# Shopee Affiliate & Instagram URL Converter

Esta aplicação oferece duas funcionalidades principais:

1. **Converter links de afiliado da Shopee** para usar seu próprio ID de afiliado
2. **Obter URLs diretas para imagens de perfil do Instagram**

Ideal para criadores de conteúdo, afiliados e desenvolvedores.

## Funcionalidades

### Conversão de Links de Afiliado da Shopee

- Converte URLs completas da Shopee para usar seu ID de afiliado
- Resolve URLs encurtadas (s.shopee.com.br) automaticamente
- Inclui parâmetros UTM necessários para rastreamento
- API simples para integração com outros serviços
- Endpoint webhook para integração com bots de WhatsApp

### Extração de Imagens de Perfil do Instagram

- Obtém URLs diretas para imagens de perfil do Instagram
- Contorna problemas de hashes e expiração de URLs
- Cache automático para melhor desempenho
- Endpoints de API para integração

## Como Usar

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/shopee-instagram-converter.git
cd shopee-instagram-converter

# Instalar dependências
pip install -r requirements.txt

# Executar a aplicação
python run.py
```

A aplicação estará disponível em `http://localhost:5000`

### Configuração no Render

1. Crie uma nova aplicação Web Service no Render
2. Conecte ao seu repositório GitHub
3. Configurações:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app`
   - **Environment Variables**: (opcional) Adicione variáveis de ambiente se necessário

## Endpoints da API

### Conversão de URL da Shopee

#### Interface Web

Acesse `/` e clique na aba "Shopee Afiliado" para usar a interface web.

#### Endpoint Simples GET

```
GET /converter?url=https://s.shopee.com.br/7pgU9ozK4c&id=18396650603
```

Parâmetros:
- `url`: URL da Shopee para converter (obrigatório)
- `id`: Seu ID de afiliado (opcional, padrão: 18396650603)
- `text_only`: Se 'true', retorna apenas a URL como texto plano (opcional)

#### Endpoint API POST

```
POST /api/convert-shopee
Content-Type: application/json

{
  "url": "https://s.shopee.com.br/7pgU9ozK4c",
  "affiliate_id": "18396650603"
}
```

Resposta:
```json
{
  "original_url": "https://s.shopee.com.br/7pgU9ozK4c",
  "converted_url": "https://shopee.com.br/product/123456/789012?utm_source=an_18396650603&utm_medium=affiliates&utm_campaign=id_18396650603",
  "affiliate_id": "18396650603"
}
```

#### Webhook para Bots

```
POST /webhook
Content-Type: application/json

{
  "message": {
    "text": "Olha essa oferta: https://s.shopee.com.br/7pgU9ozK4c"
  }
}
```

Resposta:
```json
{
  "success": true,
  "original_url": "https://s.shopee.com.br/7pgU9ozK4c",
  "converted_url": "https://shopee.com.br/product/123456/789012?utm_source=an_18396650603&utm_medium=affiliates&utm_campaign=id_18396650603"
}
```

### URLs de Imagem do Instagram

#### Interface Web

Acesse `/` e use a aba "Instagram URL" para obter URLs de imagens de perfil.

#### Endpoint API

```
GET /api/profile-pic/instagram
```

Parâmetros de query (opcionais):
- `format`: Formato de saída (`url`, `base64` ou `json`)

Resposta:
```json
{
  "username": "instagram",
  "format": "url",
  "result": "https://scontent.cdninstagram.com/..."
}
```

#### Endpoint Direto da Imagem

```
GET /image/instagram.jpg
```

Retorna a imagem de perfil diretamente.

## Integração com WhatsApp

Para integrar com grupos de WhatsApp e monitorar links:

1. Use um serviço de bot para WhatsApp (como Twilio API, WhatApp Business API, ou similares)
2. Configure o bot para enviar mensagens com links da Shopee para o endpoint `/webhook`
3. O endpoint retornará o link convertido que pode ser enviado de volta ao grupo

Exemplo de fluxo:
1. Alguém posta um link da Shopee no grupo: "https://s.shopee.com.br/7pgU9ozK4c"
2. Seu bot detecta a mensagem e envia para `/webhook`
3. A API converte o link e retorna a versão com seu ID de afiliado
4. O bot posta de volta a URL convertida no grupo

## Customização

### Alterando o ID de Afiliado Padrão

Edite o valor padrão na função `convert_shopee_affiliate_link` no arquivo `shopee_affiliate.py`:

```python
def convert_shopee_affiliate_link(original_url, your_affiliate_id="SEU_ID_AQUI"):
    # ...
```

## Licença

Este projeto está licenciado sob a licença MIT. 