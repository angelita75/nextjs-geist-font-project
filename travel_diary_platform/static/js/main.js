// Main JavaScript for Travel Diary Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize like buttons
    initializeLikeButtons();
    
    // Initialize comment forms
    initializeCommentForms();
    
    // Initialize map if present
    if (document.getElementById('map')) {
        initializeMap();
    }
    
    // Initialize file upload preview
    initializeFileUpload();
});

// Like functionality
function initializeLikeButtons() {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const diaryId = this.dataset.diaryId;
            const likeCountSpan = this.querySelector('.like-count');
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading"></span>';
            this.disabled = true;
            
            fetch('/diary/like', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `diary_id=${diaryId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    this.classList.add('liked');
                    this.innerHTML = `♥ ${data.like_count}`;
                } else {
                    this.classList.remove('liked');
                    this.innerHTML = `♡ ${data.like_count}`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.innerHTML = originalText;
                showAlert('Error updating like. Please try again.', 'danger');
            })
            .finally(() => {
                this.disabled = false;
            });
        });
    });
}

// Comment functionality
function initializeCommentForms() {
    const commentForms = document.querySelectorAll('.comment-form');
    
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const commentInput = this.querySelector('textarea[name="body"]');
            const commentsContainer = this.closest('.diary-entry').querySelector('.comments-list');
            
            // Show loading state
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading"></span> Posting...';
            submitBtn.disabled = true;
            
            fetch('/diary/comment', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Add new comment to the list
                    const commentHtml = `
                        <div class="comment">
                            <strong>You</strong>: ${data.comment}
                            <small class="text-muted d-block">Just now</small>
                        </div>
                    `;
                    commentsContainer.insertAdjacentHTML('beforeend', commentHtml);
                    commentInput.value = '';
                    showAlert('Comment added successfully!', 'success');
                } else {
                    showAlert('Error adding comment. Please try again.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error adding comment. Please try again.', 'danger');
            })
            .finally(() => {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            });
        });
    });
}

// Map functionality
function initializeMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;
    
    // Initialize Google Map
    const map = new google.maps.Map(mapElement, {
        zoom: 10,
        center: { lat: 40.7128, lng: -74.0060 }, // Default to NYC
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });
    
    // Load risk points
    loadRiskPoints(map);
    
    // Add search functionality
    const searchBox = new google.maps.places.SearchBox(document.getElementById('location-search'));
    
    searchBox.addListener('places_changed', function() {
        const places = searchBox.getPlaces();
        if (places.length === 0) return;
        
        const place = places[0];
        if (place.geometry && place.geometry.location) {
            map.setCenter(place.geometry.location);
            map.setZoom(15);
        }
    });
}

// Load risk points from API
function loadRiskPoints(map) {
    fetch('/alerts/api/risks')
        .then(response => response.json())
        .then(risks => {
            risks.forEach(risk => {
                // For demo purposes, we'll use random coordinates
                // In a real app, you'd geocode the location string
                const lat = 40.7128 + (Math.random() - 0.5) * 0.1;
                const lng = -74.0060 + (Math.random() - 0.5) * 0.1;
                
                const marker = new google.maps.Marker({
                    position: { lat, lng },
                    map: map,
                    title: risk.category,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 8,
                        fillColor: getRiskColor(risk.category),
                        fillOpacity: 0.8,
                        strokeColor: '#fff',
                        strokeWeight: 2
                    }
                });
                
                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div>
                            <h6>${risk.category}</h6>
                            <p><strong>Location:</strong> ${risk.location}</p>
                            <p>${risk.description}</p>
                            <small class="text-muted">${new Date(risk.timestamp).toLocaleDateString()}</small>
                        </div>
                    `
                });
                
                marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                });
            });
        })
        .catch(error => {
            console.error('Error loading risk points:', error);
        });
}

// Get color based on risk category
function getRiskColor(category) {
    const colors = {
        'theft': '#dc3545',
        'scam': '#fd7e14',
        'health': '#ffc107',
        'transport': '#0dcaf0',
        'weather': '#6f42c1',
        'other': '#6c757d'
    };
    return colors[category.toLowerCase()] || colors.other;
}

// File upload preview
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            const previewContainer = document.getElementById('file-preview');
            if (!previewContainer) return;
            
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `
                        <div class="mt-3">
                            <img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px;">
                            <p class="small text-muted mt-1">${file.name}</p>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.innerHTML = `
                    <div class="mt-3">
                        <div class="alert alert-info">
                            <strong>File selected:</strong> ${file.name}
                        </div>
                    </div>
                `;
            }
        });
    });
}

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Form validation helpers
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
