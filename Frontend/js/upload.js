// Buka Kamera
const camera = document.getElementById("camera");
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        camera.srcObject = stream;
    })
    .catch(err => alert("Camera access denied"));

// Ambil Foto lalu kirim ke backend
function takePhoto() {
    let canvas = document.createElement("canvas");
    canvas.width = camera.videoWidth;
    canvas.height = camera.videoHeight;

    let ctx = canvas.getContext("2d");
    ctx.drawImage(camera, 0, 0);

    canvas.toBlob(blob => {
        uploadToBackend(blob, "camera_photo.jpg");
    }, "image/jpeg");
}

// Upload Manual
function uploadManual() {
    const file = document.getElementById("fileInput").files[0];
    if (!file) return alert("Please select a file first.");
    uploadToBackend(file, file.name);
}

// Function kirim file ke backend
function uploadToBackend(file, filename) {
    let form = new FormData();
    form.append("image", file, filename);

    fetch("http://localhost:8000/predict", {
        method: "POST",
        body: form
    })
    .then(res => res.json())
    .then(data => {
        // redirect ke result.html sambil bawa data
        const encoded = encodeURIComponent(JSON.stringify(data));
        window.location.href = `result.html?data=${encoded}`;
    })
    .catch(err => alert("Upload error: " + err));
}
