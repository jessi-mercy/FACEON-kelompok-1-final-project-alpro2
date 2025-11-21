// Ambil query param dari URL
const params = new URLSearchParams(window.location.search);
const data = params.get("data");

if (!data) {
    document.getElementById("result").innerText = "No Data Received.";
} else {
    const json = JSON.parse(decodeURIComponent(data));

    let html = `
        <p><b>File:</b> ${json.filename}</p>
        <p><b>Timestamp:</b> ${json.timestamp}</p>
        <h3>Predictions:</h3>
        <ul>
    `;

    const emotions = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"];

    json.predictions.forEach((p, i) => {
        const percent = (p * 100).toFixed(2);
        html += `<li>${emotions[i]}: ${percent}%</li>`;
    });

    html += "</ul>";

    document.getElementById("result").innerHTML = html;
}
