import requests
import pygame
import io
import time
import pyttsx3
import torch
from TTS.api import TTS
from config import (
    ELEVENLABS_API_KEY, 
    ELEVENLABS_API_URL, 
    ELEVENLABS_VOICES,
    XTTS_MODEL_NAME
)

class TTSSpeaker:
    def __init__(self, tts_type="local", voice_name=None, speaker_wav=None):
        self.tts_type = tts_type
        self.voice_name = voice_name
        
        if tts_type == "local":
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 1.0)
            if voice_name:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice_name in voice.name:
                        self.engine.setProperty('voice', voice.id)
                        break
        
        elif tts_type == "xtts":
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts = TTS(XTTS_MODEL_NAME).to(device)
            self.speaker_wav = speaker_wav  # Path to reference voice file
            
        elif tts_type == "online":
            pygame.mixer.init()
            self.voice_id = ELEVENLABS_VOICES.get(voice_name, ELEVENLABS_VOICES["Rachel"])

    def get_available_voices(self):
        if self.tts_type == "local":
            voices = self.engine.getProperty('voices')
            return [voice.name for voice in voices]
        elif self.tts_type == "online":
            return list(ELEVENLABS_VOICES.keys())
        elif self.tts_type == "xtts":
            return ["default"]  # XTTS uses a single model
            
    def speak_local(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Local TTS error: {str(e)}")
            
    def speak_xtts(self, text):
        try:
            output_path = "temp_audio.wav"
            
            # If we have a reference voice file, use it for voice cloning
            if self.speaker_wav:
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=self.speaker_wav,
                    language="en"
                )
            else:
                # Use default voice
                self.tts.tts_to_file(text=text, file_path=output_path)
            
            # Play the audio
            pygame.mixer.init()
            pygame.mixer.music.load(output_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up
            import os
            os.remove(output_path)
            
        except Exception as e:
            print(f"XTTS error: {str(e)}")
            
    def speak_online(self, text):
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            response = requests.post(
                f"{ELEVENLABS_API_URL}/{self.voice_id}",
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                audio_content = io.BytesIO(response.content)
                pygame.mixer.music.load(audio_content)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Online TTS error: {str(e)}")
            
    def speak(self, text):
        if self.tts_type == "local":
            self.speak_local(text)
        elif self.tts_type == "xtts":
            self.speak_xtts(text)
        else:
            self.speak_online(text)

def select_tts_system():
    while True:
        print("\nAvailable TTS Systems:")
        print("1. Local TTS (System voices)")
        print("2. Online TTS (ElevenLabs)")
        print("3. XTTS (Local AI model)")
        
        choice = input("Choose TTS type (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return {
                '1': "local",
                '2': "online",
                '3': "xtts"
            }[choice]
        print("Invalid choice. Please enter 1, 2, or 3.")

def select_voice(speaker):
    available_voices = speaker.get_available_voices()
    
    if not available_voices:
        return None
        
    print("\nAvailable voices:")
    for idx, voice in enumerate(available_voices, 1):
        print(f"{idx}. {voice}")
        
    while True:
        choice = input(f"Select voice (1-{len(available_voices)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available_voices):
                return available_voices[idx]
        except ValueError:
            pass
        print("Invalid choice. Please try again.")

def main():
    # Select TTS system
    tts_type = select_tts_system()
    
    # Initialize speaker with no voice first
    temp_speaker = TTSSpeaker(tts_type=tts_type)
    
    # Select voice
    voice_name = select_voice(temp_speaker)
    
    # Initialize final speaker with selected voice
    speaker = TTSSpeaker(tts_type=tts_type, voice_name=voice_name)
    
    print("\nTTS System ready!")
    print(f"Using: {tts_type.upper()} TTS")
    if voice_name:
        print(f"Voice: {voice_name}")
    
    while True:
        text = input("\nEnter text to speak (or 'quit' to exit): ")
        if text.lower() == 'quit':
            break
        speaker.speak(text)

if __name__ == "__main__":
    main() 