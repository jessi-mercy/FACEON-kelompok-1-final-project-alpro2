// File upload handling for faceon (FINAL FIXED VERSION)

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const previewImage = document.getElementById('preview-image');
    const analyzeBtn = document.getElementById('analyze-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const cameraBtn = document.getElementById('camera-btn');
    const loadingElement = document.getElementById('loading');

    // 1. Tombol Upload Biasa
    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => fileInput.click());
    }

    // 2. Logika Drag & Drop + Preview
    if (uploadArea && fileInput) {
        // Klik area kotak untuk buka file selector
        uploadArea.addEventListener('click', () => fileInput.click());
        
        // Efek visual saat drag file
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#9370DB';
            uploadArea.style.background = 'rgba(147, 112, 219, 0.1)';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#ADB5BD';
            uploadArea.style.background = '';
        });
        
        // Saat file dilepas (Drop)
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            // Reset style
            uploadArea.style.borderColor = '#ADB5BD';
            uploadArea.style.background = '';

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                // PENTING: Masukkan file ke input form agar ikut terkirim saat submit
                fileInput.files = files; 
                handleFileSelection(files[0]);
            }
        });
        
        // Saat file dipilih manual lewat tombol
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
    }

    // Fungsi Preview Gambar
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
            
            // Tampilkan preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
                
                // Sembunyikan placeholder icon kamera
                const placeholder = uploadArea.querySelector('.image-placeholder-box');
                if (placeholder) {
                    placeholder.style.display = 'none';
                }
                
                analyzeBtn.disabled = false; // Aktifkan tombol Analyze
            };
            reader.readAsDataURL(file);
        }
    }

    // Camera button handler (tetap sama)
    if (cameraBtn) {
        cameraBtn.addEventListener('click', function() {
            const cameraModal = document.getElementById('camera-modal');
            if (cameraModal) cameraModal.style.display = 'flex';
        });
    }

    const closeCameraBtn = document.getElementById('close-camera');
    if (closeCameraBtn) {
        closeCameraBtn.addEventListener('click', function() {
            const cameraModal = document.getElementById('camera-modal');
            if (cameraModal) cameraModal.style.display = 'none';
        });
    }

    // 3. Form Submission (BAGIAN UTAMA YANG DIPERBAIKI)
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            
            // Cek dulu apakah file sudah dipilih
            if (!fileInput.files || !fileInput.files.length) {
                e.preventDefault(); // Batalkan submit cuma kalau file kosong
                alert('Please select an image file first');
                return;
            }

            // JIKA FILE ADA: 
            // HAPUS LOGIKA FETCH / JSON.
            // Biarkan browser mengirim data secara alami ke Flask (Server Side Rendering).

            // Cukup tampilkan loading agar user tahu proses sedang berjalan
            if (loadingElement) loadingElement.style.display = 'block';
            if (analyzeBtn) analyzeBtn.disabled = true;
            
            // Selesai. Browser akan reload dan pindah ke halaman Result otomatis.
        });
    }
});