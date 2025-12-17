// Main JavaScript functionality

document.addEventListener('DOMContentLoaded', () => {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a');

    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.getAttribute('id');
                    navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href').includes(`#${id}`)) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        },
        {
            threshold: 0.6,
        }
    );
    sections.forEach(section => observer.observe(section));
});

    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');
                
                // Update active tab button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Show/hide tab content
                document.querySelectorAll('.upload-option').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(`${tabId}-upload-option`).classList.add('active');
            });
        });
    }

    // File upload handling
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const analyzeBtn = document.getElementById('analyze-btn');

    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#4361ee';
            uploadArea.style.background = '#f8f9ff';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#ddd';
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
            
            // Display file name
            uploadArea.innerHTML = `
                <i class="fas fa-check-circle" style="color: #28a745;"></i>
                <p>File selected: ${file.name}</p>
                <span>Click to change file</span>
            `;
            
            analyzeBtn.disabled = false;
        }
    };