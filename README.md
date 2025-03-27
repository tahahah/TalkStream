# TalkStream

TalkStream is a real-time voice and screen sharing application powered by Google's Gemini API. It enables interactive voice conversations with the Gemini AI model while optionally sharing your screen or a specific window.

## Features

- **Real-time voice conversations** with Google's Gemini AI
- **Multiple sharing modes**:
  - Full screen sharing
  - Specific window sharing
  - Camera input
  - Audio-only mode (no visual input)
- **System tray application** with:
  - Visual indicator that changes color when audio is playing
  - Easy selection between sharing modes
  - One-click start/stop functionality
- **Keyboard hotkeys** for quick access
- **Clipboard integration** for easy text copying

## Requirements

- Windows operating system
- Python 3.8 or higher
- Google Gemini API key

## Installation

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/talkstream.git
   cd talkstream
   ```

2. **Create and activate a virtual environment**:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Set up your Gemini API key**:
   - Create a `.env` file in the project root
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`

## Usage

### System Tray Application (Recommended)

The tray application provides the most user-friendly experience:

```
python tray_app.py
```

This will create a system tray icon with the following options:
- **Start (Full Screen)**: Share your entire screen with Gemini
- **Start (Selected Window)**: Share a specific window with Gemini
- **Start (Audio Only)**: Voice-only conversation with no visual input
- **Select Window**: Choose a specific window to share
- **Refresh Window List**: Update the list of available windows
- **Stop TalkStream**: Stop the current session
- **Exit**: Close the tray application

The tray icon will change color when Gemini is speaking, providing a visual indicator of audio activity.

#### Built-in Hotkeys

The tray application includes keyboard shortcuts:
- **Ctrl+Alt+G**: Toggle TalkStream in the default mode (screen sharing by default)
- **Ctrl+Alt+V**: Toggle TalkStream in voice-only mode (no screen sharing)

You can customize the main hotkey and default mode:

```
python tray_app.py --hotkey "ctrl+alt+t" --mode camera
```

If you want to disable the voice-only hotkey:

```
python tray_app.py --disable-voice-hotkey
```

### Hotkey Launcher

For keyboard-driven usage, you can use the hotkey launcher:

```
python main.py
```

By default, pressing `Ctrl+Alt+G` will toggle TalkStream on and off in screen sharing mode.

You can customize the hotkey and mode:

```
python main.py --hotkey "ctrl+alt+t" --mode none
```

Available modes:
- `screen`: Share your entire screen (default)
- `window`: Share a specific window (requires window selection via tray app first)
- `camera`: Use your webcam
- `none`: Audio-only mode

### Direct Execution

You can also run the core application directly:

```
python gemini_liveapi.py --mode screen
```

Available modes:
- `screen`: Share your entire screen
- `camera`: Use your webcam
- `none`: Audio-only mode

## Troubleshooting

### Audio Issues

- **No sound from Gemini**: Ensure your output device is properly configured and not muted
- **Microphone not working**: Check your default recording device in Windows sound settings
- **Echo**: Use headphones to prevent Gemini from hearing itself

### Visual Input Issues

- **Black screen when sharing**: Try restarting the application
- **Window capture not working**: Some applications with enhanced security may not allow screen capture

### API Issues

- **API key errors**: Verify your Gemini API key is correctly set in the `.env` file
- **Rate limiting**: If you encounter rate limiting, wait a few minutes before trying again

## License

[Your license information here]

## Acknowledgments

This project uses Google's Gemini API for AI conversation capabilities.