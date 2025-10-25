# Contributing to College Buddy Chatbot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🐛 Reporting Bugs

If you find a bug, please create an issue with:
- Clear title describing the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Your environment (OS, browser, Python version)

## 💡 Suggesting Features

Feature requests are welcome! Please:
- Check if the feature already exists or is in progress
- Describe the feature and its use case
- Explain why it would be valuable for students
- Provide examples or mockups if possible

## 🔧 Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/college-buddy.git
cd college-buddy
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Add your GEMINI_API_KEY to .env
```

5. **Run the server**
```bash
python main.py
```

## 📝 Code Style Guidelines

- **Python**: Follow PEP 8 style guide
- **Variable naming**: Use descriptive names (e.g., `user_query` not `uq`)
- **Comments**: Add comments for complex logic
- **Functions**: Keep functions focused and under 50 lines when possible
- **Type hints**: Use type hints for function parameters and returns

### Example:
```python
def enhance_response(response: str, question: str) -> str:
    """
    Enhance response to be student-friendly.
    
    Args:
        response: Original response text
        question: User's question
    
    Returns:
        Enhanced response with friendly tone
    """
    # Implementation here
    pass
```

## 🌿 Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/feature-name` - New features
- `fix/bug-name` - Bug fixes
- `hotfix/issue-name` - Urgent fixes

## 📤 Pull Request Process

1. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write clean, readable code
   - Add comments where needed
   - Test your changes thoroughly

3. **Commit with clear messages**
```bash
git commit -m "Add: Description of what you added"
git commit -m "Fix: Description of what you fixed"
git commit -m "Update: Description of what you updated"
```

4. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

5. **Create Pull Request**
   - Provide clear title and description
   - Reference any related issues
   - Explain what changed and why
   - Add screenshots for UI changes

6. **Code Review**
   - Respond to feedback
   - Make requested changes
   - Keep discussions professional and constructive

## ✅ Testing Guidelines

Before submitting PR, test:
- Text chat functionality
- Voice input (English, Telugu, Hindi)
- Voice response with typing animation
- RAG retrieval accuracy
- Rule-based responses
- Analytics tracking
- Error handling

## 🚫 What NOT to Include

- API keys or credentials
- Personal information
- Large binary files
- Generated files (__pycache__, .pyc)
- Database files (chroma/, *.sqlite3)
- Cache files (response_cache.json, analytics_data.json)

## 📚 Areas Needing Contribution

### High Priority:
- Unit tests for RAG system
- Mobile UI improvements
- Response accuracy improvements
- Performance optimizations

### Medium Priority:
- Additional language support
- Chat history export
- User feedback system
- Error monitoring integration

### Low Priority:
- Dark mode theme
- Custom voice options
- Advanced analytics dashboard

## 💬 Communication

- Be respectful and professional
- Ask questions if unclear
- Provide constructive feedback
- Help others learn and grow

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Thank You!

Every contribution, no matter how small, helps make this chatbot better for students. Thank you for being part of this project!

---

**Questions?** Open an issue or reach out to the maintainers.
