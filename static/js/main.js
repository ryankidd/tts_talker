let currentSession = null;

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initial voice loading
    loadVoicesForType('local');

    // TTS type change handler
    document.querySelectorAll('input[name="tts-type"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            loadVoicesForType(e.target.value);
        });
    });

    // Volume slider handler
    const volumeSlider = document.getElementById('volume-slider');
    const volumeValue = document.getElementById('volume-value');
    volumeSlider.addEventListener('input', (e) => {
        volumeValue.textContent = `${e.target.value}%`;
    });

    // Speak button handler
    document.getElementById('speak-button').addEventListener('click', speak);
});

async function loadVoicesForType(ttsType) {
    const voiceSelect = document.getElementById('voice-select');
    voiceSelect.innerHTML = '<option value="">Loading voices...</option>';

    try {
        const response = await fetch('/api/get_voices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tts_type: ttsType }),
        });

        const data = await response.json();
        
        voiceSelect.innerHTML = data.voices
            .map(voice => `<option value="${voice}">${voice}</option>`)
            .join('');

        // Initialize new TTS session
        initTTSSession(ttsType, voiceSelect.value);
    } catch (error) {
        console.error('Error loading voices:', error);
        voiceSelect.innerHTML = '<option value="">Error loading voices</option>';
    }
}

async function initTTSSession(ttsType, voiceName) {
    try {
        const response = await fetch('/api/init_tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tts_type: ttsType,
                voice_name: voiceName,
            }),
        });

        const data = await response.json();
        currentSession = data.session_id;
    } catch (error) {
        console.error('Error initializing TTS session:', error);
    }
}

async function speak() {
    if (!currentSession) {
        showStatus('No TTS session initialized', 'error');
        return;
    }

    const text = document.getElementById('text-input').value.trim();
    if (!text) {
        showStatus('Please enter some text', 'error');
        return;
    }

    const volume = document.getElementById('volume-slider').value / 100;
    const button = document.getElementById('speak-button');
    button.disabled = true;
    
    try {
        const response = await fetch('/api/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSession,
                text: text,
                volume: volume,
            }),
        });

        const data = await response.json();
        if (data.status === 'success') {
            showStatus('Speaking...', 'success');
        } else {
            showStatus('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showStatus('Error speaking text', 'error');
    } finally {
        button.disabled = false;
    }
}

function showStatus(message, type = 'info') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    setTimeout(() => {
        status.textContent = '';
        status.className = 'status';
    }, 3000);
} 