# TalkStream

A real-time voice communication application using Google's Gemini API for interactive voice conversations.

## Setup Instructions

### 1. Environment Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/talkstream.git
   cd talkstream
   ```

2. Create and activate a virtual environment:
   ```
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Gemini API key:
   - Create a `.env` file in the project root
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`

### 2. Running the Application

#### Option 1: Run the API Server

The API server handles WebRTC connections and communicates with the Gemini API:

```
python api.py
```

This will start the server at http://localhost:7860

#### Option 2: Run the Client

The client connects to the API server and handles audio input/output:

```
python client_rtc.py
```

When running the client, you'll be prompted to:
1. Enter your Gemini API key (if not in .env file)
2. Select a voice (Puck, Charon, Kore, Fenrir, or Aoede)
3. Enter the server URL (default: http://localhost:7860)

#### Option 3: Run the Demo Application

For a full demo with a Gradio UI:

```
python demo.py
```

## Troubleshooting

### Audio Device Issues

If you encounter audio device issues:

1. In `client_rtc.py`, you may need to modify the audio device settings:
   - For Windows: `MediaPlayer('audio=Microphone', format='dshow')`
   - For macOS: `MediaPlayer('default', format='avfoundation')`
   - For Linux: `MediaPlayer('default', format='pulse')`

2. To list available audio devices on Windows:
   ```
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```

### Connection Issues

- Ensure the server is running before starting the client
- Check that your Gemini API key is valid
- Verify that port 7860 is not blocked by a firewall

## License

[Your license information here]

## The two main repostitories this project is going to be based off of:
- https://github.com/shravanasati/pyscreenrec/blob/master/pyscreenrec/__init__.py#L166
- https://huggingface.co/spaces/fastrtc/gemini-audio-video/blob/main/app.py

The first one deals with multithreaded video recording while the second one allows for real-time audio and video conversations with Gemini.
Thr way the video recording library works is that:
1. It takes screenshots at intervals determined by the FPS 
2. Adds these screenshots to the queue
3. Another thread accesses this queue and writes it as a video continually until the queue is empty

To integrate this with our gemini conversation, we can directly access the queue