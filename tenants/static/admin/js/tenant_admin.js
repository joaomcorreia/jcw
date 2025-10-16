// Tenant Admin JavaScript Enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Add frontend connect button to the tenant change form
    addFrontendConnectButton();
    
    // Enhance preview functionality
    enhancePreviewSection();
    
    // Add copy domain functionality
    addCopyDomainButton();
});

function addFrontendConnectButton() {
    // Check if we're on a tenant change page and have the frontend URL
    if (typeof window.tenant_frontend_url !== 'undefined' && window.tenant_frontend_url) {
        const form = document.querySelector('.change-form');
        if (form) {
            // Create actions bar
            const actionsBar = document.createElement('div');
            actionsBar.className = 'tenant-actions-bar';
            
            // Get tenant info
            const nameField = document.querySelector('#id_name');
            const domainField = document.querySelector('#id_domain');
            
            const tenantName = nameField ? nameField.value : 'Tenant';
            const tenantDomain = domainField ? domainField.value : '';
            
            actionsBar.innerHTML = `
                <div class="tenant-info">
                    <h3>${tenantName}</h3>
                    <div class="domain-info">${tenantDomain}</div>
                </div>
                <div class="tenant-actions">
                    <a href="${window.tenant_frontend_url}" 
                       target="_blank" 
                       class="tenant-frontend-button"
                       title="Open ${tenantName} frontend in new tab">
                       Connect to Frontend
                    </a>
                </div>
            `;
            
            // Insert before the form
            form.parentNode.insertBefore(actionsBar, form);
        }
    }
}

function enhancePreviewSection() {
    const previewField = document.querySelector('.field-get_admin_preview_html');
    if (previewField) {
        const previewContent = previewField.querySelector('.readonly');
        if (previewContent) {
            // Add click-to-expand functionality for preview images
            const images = previewContent.querySelectorAll('img');
            images.forEach(img => {
                img.style.cursor = 'pointer';
                img.addEventListener('click', function() {
                    openImageModal(this.src);
                });
            });
        }
    }
}

function addCopyDomainButton() {
    const domainField = document.querySelector('#id_domain');
    if (domainField) {
        const copyButton = document.createElement('button');
        copyButton.type = 'button';
        copyButton.innerHTML = '📋 Copy';
        copyButton.style.cssText = `
            margin-left: 10px;
            padding: 5px 10px;
            border: 1px solid #ccc;
            background: #f8f9fa;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        `;
        
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(domainField.value).then(function() {
                copyButton.innerHTML = '✓ Copied!';
                copyButton.style.background = '#d4edda';
                copyButton.style.color = '#155724';
                
                setTimeout(function() {
                    copyButton.innerHTML = '📋 Copy';
                    copyButton.style.background = '#f8f9fa';
                    copyButton.style.color = '';
                }, 2000);
            });
        });
        
        domainField.parentNode.appendChild(copyButton);
    }
}

function openImageModal(imageSrc) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        cursor: pointer;
    `;
    
    // Create modal image
    const modalImg = document.createElement('img');
    modalImg.src = imageSrc;
    modalImg.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    `;
    
    modal.appendChild(modalImg);
    
    // Close modal on click
    modal.addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Add to body
    document.body.appendChild(modal);
}

// Make frontend URL available globally if it exists
if (typeof django !== 'undefined' && django.jQuery) {
    django.jQuery(document).ready(function($) {
        // Extract frontend URL from template context
        const frontendUrlElement = document.querySelector('[data-frontend-url]');
        if (frontendUrlElement) {
            window.tenant_frontend_url = frontendUrlElement.getAttribute('data-frontend-url');
        }
    });
}