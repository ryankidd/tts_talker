from flask import Flask, render_template, request, jsonify
from main import TTSSpeaker
import os

app = Flask(__name__)
speakers = {}  # Store TTS instances

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init_tts', methods=['POST'])
def init_tts():
    data = request.json
    tts_type = data.get('tts_type')
    voice_name = data.get('voice_name')
    speaker_wav = data.get('speaker_wav')
    
    session_id = str(hash(f"{tts_type}{voice_name}{speaker_wav}"))
    speakers[session_id] = TTSSpeaker(tts_type=tts_type, voice_name=voice_name, speaker_wav=speaker_wav)
    
    return jsonify({"session_id": session_id})

@app.route('/api/get_voices', methods=['POST'])
def get_voices():
    data = request.json
    tts_type = data.get('tts_type')
    temp_speaker = TTSSpeaker(tts_type=tts_type)
    voices = temp_speaker.get_available_voices()
    return jsonify({"voices": voices})

@app.route('/api/speak', methods=['POST'])
def speak():
    data = request.json
    session_id = data.get('session_id')
    text = data.get('text')
    volume = float(data.get('volume', 1.0))
    
    if session_id in speakers:
        speaker = speakers[session_id]
        # Adjust volume if supported by the TTS type
        if speaker.tts_type == "local":
            speaker.engine.setProperty('volume', volume)
        speaker.speak(text)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Session not found"})

if __name__ == '__main__':
    app.run(debug=True) 