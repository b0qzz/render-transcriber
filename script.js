// This relative path is all we need.
const API_ENDPOINT = "/transcribe/";

// --- Get page elements ---
const fileInput = document.getElementById('file-input');
const transcribeBtn = document.getElementById('transcribe-btn');
const statusDiv = document.getElementById('status');
const resultBox = document.getElementById('result-box');

// --- Button click event ---
transcribeBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) {
        statusDiv.textContent = 'Please select an audio file first.';
        return;
    }

    transcribeBtn.disabled = true;
    statusDiv.textContent = 'Uploading file to the cloud server...';
    resultBox.textContent = 'Processing... This may take a moment.';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const transcription = data.transcription;

        if (transcription && transcription.trim() !== "") {
            resultBox.textContent = transcription;
            statusDiv.textContent = 'Transcription complete!';
        } else {
            resultBox.textContent = '--- No speech was detected (or all speech was filtered out by the rules) ---';
            statusDiv.textContent = 'Transcription finished, but no output was generated.';
        }

    } catch (error) {
        console.error('Error:', error);
        statusDiv.textContent = `Error: ${error.message}`;
        resultBox.textContent = 'Failed to get transcription.';
    } finally {
        transcribeBtn.disabled = false; // Re-enable the button
    }
});