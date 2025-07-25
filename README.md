# Google AI Studio Proxy - FastAPI Edition

A clean, modular, high-performance proxy server for Google AI Studio, now powered by FastAPI. This version is a migration from the original Flask-based application, enhancing performance and maintainability.

## ✨ Acknowledgements
This project was originally written in Flask by **Sophiamccarty**. This version is a direct migration to FastAPI to improve performance and leverage modern Python async capabilities.

## 🚀 Quick Start

### Using Virtual Environment (Recommended)

#### Step 1: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
# Ensure you're in the project directory and venv is activated
pip install -r requirements.txt
```

#### Step 3: Set Up Your API Key
Create a `.env` file in the root of the project and add your Google AI API key:
```
GOOGLE_AI_API_KEY="YOUR_API_KEY_HERE"
```

#### Step 4: Run the Application
```bash
# Run with default settings (port 8000, Ngrok tunnel)
python run_proxy.py

# Run with custom settings
python run_proxy.py --model gemini-2.5-pro --port 8080
```

## 📁 Project Structure

```
google-ai-proxy/
├── config/                 # Configuration management
│   ├── settings.py        # Main configuration class
│   └── constants.py       # Constants and defaults
├── content/               # Content processing
│   ├── jailbreak.py       # Jailbreak text templates
│   ├── text_processing.py # Text utilities
│   └── lorebook.py        # Lorebook management
├── tunnel/                # Tunnel management
│   └── manager.py         # Tunnel provider (Ngrok)
├── ai/                    # AI client integration
│   └── client.py          # Google AI client wrapper
├── proxy/                 # Main proxy logic
│   └── app.py             # FastAPI application
├── main.py               # Application entry point
├── run_proxy.py          # CLI runner
├── test_structure.py     # Test suite
├── requirements.txt      # Dependencies
└── .env.example          # Example environment file
```

## ⚙️ Configuration

### Environment Variables
All configuration can be set via environment variables prefixed with `PROXY_`:

```bash
export PROXY_MODEL="gemini-2.5-pro"
export PROXY_TUNNEL_PROVIDER="Ngrok"
export PROXY_ENABLE_JAILBREAK="true"
```

### Configuration File
Create a `config.json` file and run the proxy with the `--config` flag:

```json
{
  "model": "gemini-2.5-pro-latest",
  "tunnel_provider": "Ngrok",
  "enable_jailbreak": true
}
```
```bash
python run_proxy.py --config config.json
```

## 🔧 Features

### Jailbreak System
- **None**: No jailbreak applied
- **Light**: Basic roleplay context
- **Strong**: Maximum creative freedom

### Content Processing
- **Markdown formatting**: Ensures proper markdown output
- **Text cleaning**: Removes unwanted formatting
- **Forbidden words**: Filters specific terms
- **Auto-plot**: Random plot injection
- **Spice system**: Adds narrative variety

### Lorebook System
- Dynamic context injection based on character and world information.

### Tunnel Provider
- **Ngrok**: The default and recommended tunnel provider. Requires an authtoken for stable usage.

## 🧪 Testing

Run the test suite to verify that all modules are working correctly:

```bash
python test_structure.py
```

## 📊 API Endpoints

- `POST /v1/chat/completions` - Main chat endpoint, compatible with Janitor.ai.
- `GET /health` - Health check.
- `GET /config` - View the current (safe) configuration.
- `GET /docs` - Interactive API documentation (Swagger UI).
- `GET /redoc` - Alternative API documentation (ReDoc).

## 🔐 Security Notes

- Never commit your `.env` file or API keys to version control.
- Use environment variables for sensitive data in production.

## 🐛 Troubleshooting

### Debug Mode and Logging

**Enable Debug Mode:**
```bash
# Run with the --debug flag
python run_proxy.py --debug
```

**View Logs:**
- **Console**: Logs are displayed in the terminal.
- **File**: Check the `proxy.log` file in the project directory.

### Common Issues

**`GOOGLE_AI_API_KEY not found`**
- Ensure you have created a `.env` file in the project root.
- Make sure the file is named `.env` and not `env` or `.env.txt`.
- Verify that `python-dotenv` is installed (`pip install -r requirements.txt`).

**Module Import Errors**
- Make sure your virtual environment is activated.
- Re-install dependencies with `pip install -r requirements.txt`.

**Tunnel Connection Issues**
- Check your internet connection.
- Verify your Ngrok authtoken is configured correctly if you have one.
- Ensure your firewall is not blocking Ngrok's connections.

## 📄 License

This project is provided as-is for educational and development purposes.
