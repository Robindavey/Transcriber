let latestResult = "";

async function uploadFile() {
    const fileInput = document.getElementById("audioFile");
    const status = document.getElementById("status");
    const spinner = document.getElementById("spinner");
    const output = document.getElementById("output");
    const downloadBtn = document.getElementById("downloadBtn");

    if (fileInput.files.length === 0) {
        alert("Please select an audio file");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.innerText = "Processing audio... This can take a few minutes.";
    spinner.classList.remove("hidden");
    output.innerText = "";
    downloadBtn.classList.add("hidden");

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        spinner.classList.add("hidden");

        if (data.error) {
            status.innerText = "Error: " + data.error;
            return;
        }

        status.innerText = "Done!";
        latestResult = data.result;
        output.innerText = latestResult;
        downloadBtn.classList.remove("hidden");

    } catch (err) {
        spinner.classList.add("hidden");
        status.innerText = "Failed: " + err;
    }
}

function downloadResult() {
    if (!latestResult) return;

    const blob = new Blob([latestResult], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "notes.txt";  // user will choose location
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
// Add to script.js

async function generateTTS() {
    const status = document.getElementById("tts-status");
    const downloadBtn = document.getElementById("downloadTTSBtn");
    
    status.innerText = "Generating audio... Please wait.";
    downloadBtn.classList.add("hidden");
    
    try {
        const response = await fetch("/generate-tts", {
            method: "POST"
        });
        
        const data = await response.json();
        
        if (data.error) {
            status.innerText = "Error: " + data.error;
            return;
        }
        
        status.innerText = "Audio generated successfully!";
        downloadBtn.classList.remove("hidden");
        
    } catch (err) {
        status.innerText = "Failed: " + err;
    }
}

function downloadTTS() {
    window.location.href = "/download-tts";
}