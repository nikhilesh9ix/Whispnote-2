# 🔒 Environment Configuration Guide

## Setting Up API Tokens Securely

### 1. Create Environment File

Copy the example environment file and add your actual tokens:

```bash
cp .env.example .env
```

### 2. Edit the .env file

Open `.env` in a text editor and replace the placeholder with your actual Swecha API token:

```env
# Swecha API Configuration
SWECHA_API_TOKEN=your_actual_bearer_token_here
SWECHA_API_BASE_URL=https://api.corpus.swecha.org
```

### 3. Important Security Notes

⚠️ **NEVER commit the .env file to version control**
- The `.env` file is already ignored by git
- Only commit `.env.example` as a template
- Share tokens through secure channels only

### 4. Getting Your API Token

1. Contact the Swecha team for API access
2. Obtain your bearer token through official channels
3. Add it to your local `.env` file
4. The token will be automatically loaded by the application

### 5. Verifying Configuration

Run the test script to verify your setup:

```bash
uv run python tests/quick_test.py
```

## 🛡️ Security Best Practices

- **Environment Variables**: All secrets stored in environment variables
- **No Hardcoded Tokens**: No API tokens in source code
- **Git Ignored**: Sensitive files excluded from version control
- **Template System**: `.env.example` provides setup guidance
- **Validation**: Automatic validation of configuration

## 🚨 If You Accidentally Committed Tokens

If you previously committed API tokens:

1. **Immediately revoke the exposed tokens**
2. **Generate new tokens**
3. **Update your .env file with new tokens**
4. **Consider using git-filter-branch to remove from history**

## 📞 Support

For API access or token issues, contact the Swecha team through official channels.
