# College Buddy - GitHub Pages Frontend

This is the GitHub Pages hosted frontend for College Buddy chatbot.

## Configuration

Edit `config.js` to set your backend URL:

```javascript
window.CONFIG = {
    BACKEND_URL: 'wss://your-backend-url.onrender.com'
};
```

## Local Testing

1. Open `index.html` in a browser
2. Make sure your backend is running on the configured URL
3. Start chatting!

## Deployment

This folder is automatically served by GitHub Pages when you:
1. Go to Repository Settings → Pages
2. Select "Deploy from a branch"
3. Choose `main` branch and `/docs` folder
4. Save

Your frontend will be available at: `https://yourusername.github.io/college-buddy/`
