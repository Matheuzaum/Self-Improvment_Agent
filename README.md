# Groq AI Telegram Bot

Um bot do Telegram que utiliza o Groq AI para processamento de linguagem natural, com suporte a ferramentas personalizadas e memória persistente usando Zep.

## Funcionalidades

- 🤖 Processamento de linguagem natural usando Groq AI
- 🧠 Memória persistente usando Zep
- 🛠️ Sistema de ferramentas personalizáveis
- 🔄 Integração com APIs externas
- 🌐 Suporte a múltiplos idiomas

## Requisitos

- Python 3.9+
- Conta no Groq AI
- Conta no Zep Cloud
- Bot do Telegram (criado via @BotFather)

## Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/groq-telegram-bot.git
cd groq-telegram-bot
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` com as seguintes variáveis:
   ```
   GROQ_API_KEY=sua_chave_groq
   TELEGRAM_BOT_TOKEN=seu_token_telegram
   ZEP_API_KEY=sua_chave_zep
   ZEP_API_URL=https://api.zep.cloud
   ```

   - Crie um arquivo `tool_keys.env` para mapear as variáveis de ambiente das ferramentas:
   ```
   WEATHER_API_KEY=OPENWEATHER_API_KEY
   GOOGLE_API_KEY=GOOGLE_SEARCH_API_KEY
   # ... outras variáveis
   ```

## Uso

1. Execute o bot:
```bash
python main.py
```

2. No Telegram, inicie uma conversa com seu bot usando o comando `/start`

3. Comandos disponíveis:
   - `/start` - Inicia o bot
   - `/help` - Mostra ajuda
   - `/tools` - Lista ferramentas disponíveis
   - `/memory` - Mostra memórias armazenadas
   - `/clear` - Limpa memórias

## Deploy

### Usando Docker

1. Construa a imagem:
```bash
docker build -t groq-telegram-bot .
```

2. Execute o container:
```bash
docker run -d --env-file .env groq-telegram-bot
```

### Usando GitHub Actions

1. Configure os secrets no seu repositório GitHub:
   - `GROQ_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `ZEP_API_KEY`
   - `ZEP_API_URL`

2. O workflow será executado automaticamente quando você fizer push para a branch main

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 