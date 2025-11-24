// Camera handling for real-time emotion detection in faceon

class CameraHandler {
    constructor() {
        this.video = document.getElementById('camera-video');
        this.canvas = document.getElementById('camera-canvas');
        this.captureBtn = document.getElementById('capture-btn');
        this.switchBtn = document.getElementById('switch-camera');
        this.stream = null;
        this.facingMode = 'user'; // 'user' for front camera, 'environment' for back
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        
        try {
            await this.startCamera();
            this.setupEventListeners();
            this.initialized = true;
        } catch (error) {
            console.error('Error initializing camera:', error);
            alert('Cannot access camera. Please check camera permissions.');
        }
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        if (this.video && this.video.srcObject) {
            this.video.srcObject = null;
        }
    }

    async startCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }

        const constraints = {
            video: {
                facingMode: this.facingMode,
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        };

        try {
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            if (this.video) {
                this.video.srcObject = this.stream;
            }
        } catch (error) {
            throw new Error(`Failed to start camera: ${error.message}`);
        }
    }

    setupEventListeners() {
        if (this.captureBtn) {
            this.captureBtn.addEventListener('click', () => this.captureImage());
        }
        if (this.switchBtn) {
            this.switchBtn.addEventListener('click', () => this.switchCamera());
        }
        
        // Handle video loading
        if (this.video) {
            this.video.addEventListener('loadeddata', () => {
                console.log('Camera ready');
            });
        }
    }

    captureImage() {
        if (!this.video || !this.canvas) return;
        
        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        context.drawImage(this.video, 0, 0);

        this.canvas.toBlob(async (blob) => {
            // Stop camera
            this.stop();
            
            // Hide modal
            const cameraModal = document.getElementById('camera-modal');
            if (cameraModal) {
                cameraModal.style.display = 'none';
            }
            
            // Update preview in upload area
            const reader = new FileReader();
            reader.onload = (e) => {
                const previewImage = document.getElementById('preview-image');
                const uploadArea = document.getElementById('upload-area');
                if (previewImage) {
                    previewImage.src = e.target.result;
                    previewImage.style.display = 'block';
                    const placeholder = uploadArea?.querySelector('.image-placeholder-box');
                    if (placeholder) {
                        placeholder.style.display = 'none';
                    }
                    const analyzeBtn = document.getElementById('analyze-btn');
                    if (analyzeBtn) {
                        analyzeBtn.disabled = false;
                    }
                    
                    // Create a file input with the captured image
                    const fileInput = document.getElementById('file-input');
                    if (fileInput && blob) {
                        const dataTransfer = new DataTransfer();
                        const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
                        dataTransfer.items.add(file);
                        fileInput.files = dataTransfer.files;
                    }
                }
            };
            reader.readAsDataURL(blob);
        }, 'image/jpeg', 0.8);
    }

    async switchCamera() {
        this.facingMode = this.facingMode === 'user' ? 'environment' : 'user';
        await this.startCamera();
    }

    async switchCamera() {
        this.facingMode = this.facingMode === 'user' ? 'environment' : 'user';
        await this.startCamera();
    }
    
    async analyzeImage(blob) {
        // This function is no longer needed as captureImage handles the flow
        // But kept for backward compatibility if needed
    }
}

// Global camera handler instance
let cameraHandler = null;

// Initialize camera when modal is opened
document.addEventListener('DOMContentLoaded', function() {
    const cameraModal = document.getElementById('camera-modal');
    const cameraBtn = document.getElementById('camera-btn');
    const closeCameraBtn = document.getElementById('close-camera');
    
    if (cameraBtn) {
        cameraBtn.addEventListener('click', async function() {
            if (cameraModal) {
                cameraModal.style.display = 'flex';
                
                // Initialize camera handler if not already initialized
                if (!cameraHandler) {
                    cameraHandler = new CameraHandler();
                }
                await cameraHandler.init();
            }
        });
    }
    
    if (closeCameraBtn) {
        closeCameraBtn.addEventListener('click', function() {
            if (cameraModal) {
                cameraModal.style.display = 'none';
                
                // Stop camera when closing
                if (cameraHandler) {
                    cameraHandler.stop();
                }
            }
        });
    }
});