// DOM Elements
const form = document.getElementById('verification-form');
const enabledSwitch = document.getElementById('enabled');
const typeSelect = document.getElementById('type');
const titleInput = document.getElementById('title');
const descriptionInput = document.getElementById('description');
const sendMethodSelect = document.getElementById('send_method');
const resetBtn = document.getElementById('reset-btn');
const previewTitle = document.getElementById('preview-title');
const previewDescription = document.getElementById('preview-description');

// Load configuration on page load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        // Update form with loaded config
        enabledSwitch.checked = config.VERIFICATION_ENABLED === 'true';
        typeSelect.value = config.VERIFICATION_TYPE || 'one_click';
        titleInput.value = config.VERIFICATION_TITLE || 'Verification Required';
        descriptionInput.value = config.VERIFICATION_DESCRIPTION || 'Please verify yourself to access the server';
        sendMethodSelect.value = config.VERIFICATION_SEND_METHOD || 'dm';
        
        // Update preview
        updatePreview();
    } catch (error) {
        console.error('Error loading config:', error);
        // Use default values
        updatePreview();
    }
});

// Update preview when form changes
enabledSwitch.addEventListener('change', updatePreview);
typeSelect.addEventListener('change', updatePreview);
titleInput.addEventListener('input', updatePreview);
descriptionInput.addEventListener('input', updatePreview);
sendMethodSelect.addEventListener('change', updatePreview);

function updatePreview() {
    previewTitle.textContent = titleInput.value || 'Verification Required';
    previewDescription.textContent = descriptionInput.value || 'Please verify yourself to access the server';
}

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Prepare data
    const config = {
        VERIFICATION_ENABLED: enabledSwitch.checked.toString(),
        VERIFICATION_TYPE: typeSelect.value,
        VERIFICATION_TITLE: titleInput.value,
        VERIFICATION_DESCRIPTION: descriptionInput.value,
        VERIFICATION_SEND_METHOD: sendMethodSelect.value
    };
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showMessage('Settings saved successfully!', 'success');
        } else {
            showMessage('Error saving settings: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error saving config:', error);
        showMessage('Error saving settings. Please try again.', 'error');
    }
});

// Reset to defaults
resetBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to reset to default settings?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/config/reset', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Reload the page to show default values
            location.reload();
        } else {
            showMessage('Error resetting settings: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error resetting config:', error);
        showMessage('Error resetting settings. Please try again.', 'error');
    }
});

// Show message to user
function showMessage(message, type) {
    // Remove any existing messages
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    
    // Add styles
    messageEl.style.position = 'fixed';
    messageEl.style.top = '20px';
    messageEl.style.right = '20px';
    messageEl.style.padding = '15px 20px';
    messageEl.style.borderRadius = '8px';
    messageEl.style.color = 'white';
    messageEl.style.fontWeight = '500';
    messageEl.style.zIndex = '1000';
    messageEl.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    
    if (type === 'success') {
        messageEl.style.backgroundColor = '#4caf50';
    } else {
        messageEl.style.backgroundColor = '#f44336';
    }
    
    // Add to document
    document.body.appendChild(messageEl);
    
    // Remove after 3 seconds
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

// Navigation handling
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        // Remove active class from all items
        document.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.classList.remove('active');
        });
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // In a full implementation, this would load different content
        // For this minimal example, we only have verification
    });
});