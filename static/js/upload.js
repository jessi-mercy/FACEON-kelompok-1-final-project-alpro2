// File upload and prediction handling for faceon

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const previewImage = document.getElementById('preview-image');
    const analyzeBtn = document.getElementById('analyze-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const cameraBtn = document.getElementById('camera-btn');
    const loadingElement = document.getElementById('loading');

    // Upload button handler
    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => fileInput.click());
    }

    // File upload handling
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#9370DB';
            uploadArea.style.background = 'rgba(147, 112, 219, 0.1)';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#ADB5BD';
            uploadArea.style.background = '';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelection(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
    }

    function handleFileSelection(file) {
        if (file) {
            const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
            if (!validTypes.includes(file.type)) {
                alert('Please upload a valid image file (JPEG, PNG)');
                return;
            }
            
            if (file.size > 16 * 1024 * 1024) {
                alert('File size must be less than 16MB');
                return;
            }
            
            // Display preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
                const placeholder = uploadArea.querySelector('.image-placeholder-box');
                if (placeholder) {
                    placeholder.style.display = 'none';
                }
                analyzeBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    }

    // Camera button handler (will be handled by camera.js)
    if (cameraBtn) {
        cameraBtn.addEventListener('click', function() {
            const cameraModal = document.getElementById('camera-modal');
            if (cameraModal) {
                cameraModal.style.display = 'flex';
            }
        });
    }

    // Close camera modal
    const closeCameraBtn = document.getElementById('close-camera');
    if (closeCameraBtn) {
        closeCameraBtn.addEventListener('click', function() {
            const cameraModal = document.getElementById('camera-modal');
            if (cameraModal) {
                cameraModal.style.display = 'none';
            }
        });
    }

    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!fileInput.files || !fileInput.files.length) {
                alert('Please select an image file first');
                return;
            }

            const formData = new FormData();
            formData.append('image', fileInput.files[0]);

            try {
                // Show loading
                loadingElement.style.display = 'block';
                analyzeBtn.disabled = true;

                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.emotion) {
                    // Redirect to results page
                    const confidence = typeof data.confidence === 'number' ? data.confidence : parseFloat(data.confidence);
                    window.location.href = `/result?emotion=${encodeURIComponent(data.emotion)}&confidence=${confidence}`;
                } else {
                    throw new Error(data.error || 'Prediction failed');
                }

            } catch (error) {
                console.error('Error:', error);
                alert('Error analyzing image: ' + error.message);
            } finally {
                loadingElement.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        });
    }

});