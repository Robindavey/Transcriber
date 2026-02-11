let latestResult = "";
let fileRefreshInterval = null;

function startLiveFileUpdates() {
    // Refresh file list every 2 seconds
    if (fileRefreshInterval) clearInterval(fileRefreshInterval);
    fileRefreshInterval = setInterval(loadFiles, 2000);
}

async function uploadFile() {
    const fileInput = document.getElementById("audioFile");
    const status = document.getElementById("status");
    const spinner = document.getElementById("spinner");
    const output = document.getElementById("output");
    const downloadBtn = document.getElementById("downloadBtn");

    if (fileInput.files.length === 0) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.innerText = "Processing file... This can take a few minutes.";
    spinner.classList.remove("hidden");
    output.innerText = "";
    downloadBtn.classList.add("hidden");

    try {
        const response = await fetch(`/upload/${project}`, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        spinner.classList.add("hidden");

        if (data.error) {
            status.innerText = "Error: " + data.error;
            return;
        }

        if (data.type === "audio") {
            status.innerText = "Done! Audio transcribed.";
            latestResult = data.result;
            output.innerText = latestResult;
            downloadBtn.classList.remove("hidden");
        } else if (data.type === "text") {
            status.innerText = "Done! Text file copied to raw text.";
            latestResult = data.result;
        } else if (data.type === "unsupported") {
            status.innerText = "✓ " + data.message;
        }
        
        loadFiles(); // Refresh file list
    } catch (err) {
        spinner.classList.add("hidden");
        status.innerText = "Failed: " + err;
    }
}

function downloadResult() {
    // First try to get processed notes, else use transcription
    fetch(`/project/${project}/notes`)
        .then(response => response.json())
        .then(data => {
            if (data.notes) {
                downloadText(data.notes, "fullNotes.txt");
            } else {
                downloadText(latestResult, "transcription.txt");
            }
        })
        .catch(() => {
            downloadText(latestResult, "transcription.txt");
        });
}

function downloadText(content, filename) {
    const blob = new Blob([content], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
// Add to script.js

async function generateTTS() {
    const status = document.getElementById("tts-status");
    const spinner = document.getElementById("tts-spinner");
    const downloadBtn = document.getElementById("downloadTTSBtn");
    
    status.innerText = "Generating audio... Please wait.";
    spinner.classList.remove("hidden");
    downloadBtn.classList.add("hidden");
    
    try {
        const response = await fetch(`/generate-tts/${project}`, {
            method: "POST"
        });
        
        const data = await response.json();
        spinner.classList.add("hidden");
        
        if (data.error) {
            status.innerText = "Error: " + data.error;
            return;
        }
        
        status.innerText = "Audio generated successfully!";
        downloadBtn.classList.remove("hidden");
        loadFiles(); // Refresh file list
    } catch (err) {
        spinner.classList.add("hidden");
        status.innerText = "Failed: " + err;
    }
}

function downloadTTS() {
    fetch(`/download-tts/${project}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Download failed');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'podcast_audio.wav';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        })
        .catch(err => {
            alert('Download failed: ' + err.message);
        });
}