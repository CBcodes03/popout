# OAuth Setup Instructions

## Google OAuth Configuration

To enable Google OAuth authentication, follow these steps:

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API** or **Google Identity API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Web application** as the application type
6. Add authorized redirect URIs:
   - `http://localhost:8000/api/oauth/google/callback/` (for development)
   - `https://yourdomain.com/api/oauth/google/callback/` (for production)
7. Copy the **Client ID** and **Client Secret**

### 2. Configure Django Settings

Add your Google OAuth credentials to `backend/settings.py`:

```python
GOOGLE_OAUTH2_CLIENT_ID = 'your-client-id-here'
GOOGLE_OAUTH2_CLIENT_SECRET = 'your-client-secret-here'
```

### 3. Install Required Packages

The OAuth implementation uses the `requests` library which should already be installed. If not:

```bash
pip install requests
```

### 4. Test OAuth

1. Start your Django server
2. Go to the login or register page
3. Click "Continue with Google"
4. You should be redirected to Google's login page
5. After authentication, you'll be redirected back and logged in

## How It Works

1. User clicks "Continue with Google" button
2. Frontend calls `/api/oauth/google/` to get the authorization URL
3. User is redirected to Google's OAuth consent screen
4. After user approves, Google redirects to `/api/oauth/google/callback/` with an authorization code
5. Backend exchanges the code for access token and user info
6. User is created/logged in and JWT tokens are generated
7. Frontend callback page stores tokens and redirects to home page

## Security Notes

- Never commit your OAuth credentials to version control
- Use environment variables for production:
  ```python
  import os
  GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID', '')
  GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET', '')
  ```
- Ensure redirect URIs match exactly (including trailing slashes)
- Use HTTPS in production

