# User Guide

## GUI Interface

### Getting Started
1. Launch the application:
```bash
python main.py
```

2. The main window appears with:
   - Chat area (messages)
   - Input field (type messages)
   - Control panel (buttons)
   - Theme toggle (light/dark)

### Basic Usage

#### Sending Messages
1. Type in the input field
2. Press Enter or click Send
3. View bot's response in chat area

#### Managing Sessions
- **Save**: Click "Save Session" to store conversation
- **Load**: Click "Load Session" to restore previous chats
- **Clear**: Click "Clear Chat" to start fresh

#### Themes
- Click theme toggle in top-right
- Choose between light/dark modes

### Advanced Features

#### Model Retraining
1. Click "Retrain Model"
2. Wait for completion notification
3. Continue chatting with improved model

#### API Keys
1. Click "Generate API Key"
2. Copy and save the key
3. Use for API access

## Web Interface

### Setup
1. Navigate to `web_frontend/`
2. Open `index.html` in browser

### Configuration
1. Edit `app.js`:
```javascript
const API_HOST = 'localhost:8080';
const API_KEY = 'your-key-here';
```

### Usage
1. Enter message in text box
2. Click send or press Enter
3. View response in chat window

### Features
- Message history
- Error handling
- Connection status
- Response timing

## Mobile Interface

### PWA Support
- Add to home screen
- Offline capability
- Push notifications

### Settings
- Server URL
- API key
- Theme
- Notifications

## Supported Commands

### Basic
- Greeting: "hi", "hello"
- Help: "help", "?", "commands"
- Status: "how are you"

### Information
- About: "what are you"
- Creator: "who made you"
- Version: "version"

### System
- Clear: "clear chat"
- Reset: "reset context"
- Stats: "show stats"

## Tips & Tricks

### Better Responses
- Be specific
- Use complete sentences
- Check context window
- Try rephrasing

### Performance
- Clear chat regularly
- Update API key monthly
- Check connection speed
- Monitor response times

### Troubleshooting
1. Messages not sending
   - Check connection
   - Verify API key
   - Review logs

2. Slow responses
   - Check server load
   - Verify network
   - Clear cache

3. UI issues
   - Reload page
   - Clear browser cache
   - Update app

## Keyboard Shortcuts

### Chat
- Send: Enter
- New line: Shift+Enter
- Clear: Ctrl+L

### Navigation
- Focus input: Ctrl+I
- Toggle theme: Ctrl+T
- Save session: Ctrl+S

## Error Messages

### Common Errors
1. "Connection failed"
   - Check server status
   - Verify URL/port
   - Test network

2. "Invalid API key"
   - Regenerate key
   - Update config
   - Check format

3. "Model error"
   - Wait for retry
   - Check logs
   - Contact support

## Settings

### Application
- Theme
- Font size
- Window size
- Notifications

### Chat
- Message display
- Time format
- Sound effects
- Auto-scroll

### API
- Server URL
- API key
- Timeout
- Retry count

## Customization

### Themes
- Light
- Dark
- Custom CSS

### Layout
- Window position
- Chat width
- Font family
- Colors

### Behavior
- Auto-save
- Notifications
- Sound effects
- Animations

## Security

### API Keys
- Keep private
- Rotate monthly
- Monitor usage
- Report issues

### Data
- Local storage
- Session backup
- Encryption
- Privacy

## Support

### Resources
- Documentation
- FAQ
- Forum
- Contact

### Updates
- Check version
- Auto-update
- Release notes
- Changelog

### Help
- Error codes
- Solutions
- Feedback
- Support tickets
