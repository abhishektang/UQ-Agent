# UQ Agent - Chrome Extension

A smart Chrome extension that helps University of Queensland (UQ) students automate tasks and interact with the UQ portal through natural language commands.

## 🚀 Features

- **AI-Powered Automation**: Uses natural language processing to understand user requests
- **UQ Portal Integration**: Automates tasks on the UQ student portal
- **Real-time Chat Interface**: Interactive chat-based user experience
- **Firebase Integration**: Secure user authentication and data storage
- **Playwright Automation**: Browser automation for task execution

## 📋 Prerequisites

Before installing, ensure you have:

- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Google Chrome** browser
- **Git** for version control

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd UQ-Agent
```

### 2. Install Frontend Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install playwright python-Levenshtein fuzzywuzzy
```

### 3. Install Playwright Browsers

```bash
python -m playwright install
```

### 4. Set Up Firebase (Optional for development)

Create a `.env` file in the root directory:

```env
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

## 🚀 Running the Application

### Development Mode

1. **Start the Python Automation Server** (Terminal 1):
```bash
python3 vectorDBClicksIntegrated.py
```

2. **Start the React Development Server** (Terminal 2):
```bash
npm run dev
```

3. **Load the Chrome Extension**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right)
   - Click "Load unpacked"
   - Select the `dist` folder from your project

### Production Build

```bash
# Build the extension
npm run build

# The built extension will be in the 'dist' folder
```

## 📁 Project Structure

```
UQ-Agent/
├── uq-agent-react/              # React + Vite Chrome Extension frontend
│   ├── public/                  # Static assets
│   ├── src/                     # React source code
│   │   ├── components/          # Reusable UI components
│   │   ├── views/               # App, Login, Chat views
│   │   ├── services/            # Firebase, API integrations
│   │   ├── styles/              # Stylesheets for each view
│   │   └── main.jsx             # App entry point
│   ├── manifest.json            # Chrome Extension manifest
│   ├── vite.config.js           # Vite configuration
│   └── package.json             # Frontend dependencies
│
├── vectorDBClicksIntegrated.py  # AI-powered vector DB & automation logic
│
└── README.md                    # Project documentation
```

## 🔧 Configuration

### Chrome Extension Permissions

The extension requires these permissions in `manifest.json`:
- Access to UQ portal domains
- Storage for user data
- Script execution capabilities

### Python Server

The automation server runs on `http://localhost:3001` and handles:
- Natural language processing
- Browser automation tasks
- Integration with UQ systems

## 🎯 Usage

1. **Navigate to UQ Portal**: Go to `https://portal.my.uq.edu.au`
2. **Click the Extension**: Click the UQ Agent icon in Chrome toolbar
3. **Start Chatting**: Type commands like:
   - "Book a library room"
   - "Find my COMPSCI 101 course"
   - "Show my class schedule"

## 🐛 Troubleshooting

### Common Issues

1. **Python Server Connection Refused**
   ```bash
   # Ensure Python server is running
   python3 vectorDBClicksIntegrated.py
   ```

2. **Chrome Debugging Port Error**
   ```bash
   # Launch Chrome with debugging
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   ```

3. **Firebase Authentication Errors**
   - Check Firebase configuration in `.env`
   - Verify Firebase project settings

4. **CORS Errors**
   - Ensure Python server includes proper CORS headers
   - Check Chrome extension permissions

### Debugging

- Check browser console for errors (F12)
- Monitor Python server logs for automation issues
- Use Chrome DevTools for extension debugging

## 📝 Development

### Adding New Features

1. **New Automation Tasks**:
   - Add to `vectorDBClicksIntegrated.py`
   - Update navigation plans in vector database

2. **UI Components**:
   - Create new React components in `src/components/`
   - Update chat interface in `ChatView.jsx`

3. **Firebase Integration**:
   - Modify `FirebaseConfig.js` for new data structures
   - Update security rules in Firebase console

### Testing

```bash
# Run frontend tests
npm test

# Test Python automation
python3 -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🆘 Support

For support and questions:
- Check existing [GitHub Issues](../../issues)
- Create a new issue with detailed description
- Contact the development team

🔄 Version History

v0.3.0 (2025-08-17)

Added AI-powered task execution

Users can type commands (e.g., “Show my grade”) for automated navigation

v0.2.1 (2025-08-16)

Improved login flow (auto-click Dashboard login button)

v0.2.0 (2025-08-16)

UI revamp, bug fixes, and real-time chat updates

v0.1.0 (2025-08-16)

Initial release with basic chat interface and Firebase integration

**Note**: This extension is for educational purposes. Always comply with UQ's terms of service and academic policies when using automation tools.
