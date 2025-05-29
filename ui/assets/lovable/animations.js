/* Lovable.ai Animations for AniData VPN
 * Adds subtle animations and effects to enhance the UI experience
 */

// Configuration
const config = {
    buttonHoverScale: 1.05,
    buttonPressScale: 0.98,
    transitionSpeed: '0.3s',
    hoverElevation: '0px 6px 16px rgba(108, 92, 231, 0.25)',
    normalElevation: '0px 2px 8px rgba(108, 92, 231, 0.15)',
    cardHoverTransform: 'translateY(-5px)',
    statusIndicatorPulse: true,
    enableGradientShift: true
};

// Apply animations when document is ready
document.addEventListener('DOMContentLoaded', () => {
    applyButtonAnimations();
    applyCardAnimations();
    applyStatusIndicatorEffects();
    applyGradientEffects();
    addTransitionEffectsToNavigation();
});

// Button animations
function applyButtonAnimations() {
    const buttons = document.querySelectorAll('button, .action-button');
    
    buttons.forEach(button => {
        // Store original box-shadow
        const originalShadow = getComputedStyle(button).boxShadow;
        
        // Add hover effect
        button.addEventListener('mouseenter', () => {
            button.style.transform = `scale(${config.buttonHoverScale})`;
            button.style.boxShadow = config.hoverElevation;
            button.style.transition = `all ${config.transitionSpeed} ease`;
        });
        
        // Add mouse leave effect
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'scale(1)';
            button.style.boxShadow = originalShadow;
            button.style.transition = `all ${config.transitionSpeed} ease`;
        });
        
        // Add click effect
        button.addEventListener('mousedown', () => {
            button.style.transform = `scale(${config.buttonPressScale})`;
            button.style.transition = 'all 0.1s ease';
        });
        
        // Reset after click
        button.addEventListener('mouseup', () => {
            button.style.transform = `scale(${config.buttonHoverScale})`;
            button.style.transition = `all ${config.transitionSpeed} ease`;
        });
    });
}

// Card and panel animations
function applyCardAnimations() {
    const cards = document.querySelectorAll('.card, .panel, .server-item');
    
    cards.forEach(card => {
        const originalShadow = getComputedStyle(card).boxShadow;
        const originalTransform = getComputedStyle(card).transform;
        
        // Add hover effect
        card.addEventListener('mouseenter', () => {
            card.style.transform = config.cardHoverTransform;
            card.style.boxShadow = config.hoverElevation;
            card.style.transition = `all ${config.transitionSpeed} ease`;
        });
        
        // Add mouse leave effect
        card.addEventListener('mouseleave', () => {
            card.style.transform = originalTransform;
            card.style.boxShadow = originalShadow;
            card.style.transition = `all ${config.transitionSpeed} ease`;
        });
    });
}

// Status indicator animations
function applyStatusIndicatorEffects() {
    const statusIndicators = document.querySelectorAll('.status-indicator, #statusIndicator');
    
    if (config.statusIndicatorPulse) {
        statusIndicators.forEach(indicator => {
            // Only apply pulse to connected status
            if (indicator.getAttribute('status') === 'connected') {
                // Create pulsing animation
                const keyframes = `
                    @keyframes pulse {
                        0% { box-shadow: 0 0 0 0 rgba(56, 178, 172, 0.4); }
                        70% { box-shadow: 0 0 0 10px rgba(56, 178, 172, 0); }
                        100% { box-shadow: 0 0 0 0 rgba(56, 178, 172, 0); }
                    }
                `;
                
                // Add style element with keyframes
                const style = document.createElement('style');
                style.textContent = keyframes;
                document.head.appendChild(style);
                
                // Apply animation
                indicator.style.animation = 'pulse 2s infinite';
            }
            
            // Apply different animation for connecting status
            if (indicator.getAttribute('status') === 'connecting') {
                // Create pulsing animation
                const keyframes = `
                    @keyframes blink {
                        0% { opacity: 1; }
                        50% { opacity: 0.6; }
                        100% { opacity: 1; }
                    }
                `;
                
                // Add style element with keyframes
                const style = document.createElement('style');
                style.textContent = keyframes;
                document.head.appendChild(style);
                
                // Apply animation
                indicator.style.animation = 'blink 1.5s infinite';
            }
        });
    }
}

// Gradient shift effect for primary elements
function applyGradientEffects() {
    if (!config.enableGradientShift) return;
    
    const gradientElements = document.querySelectorAll('.primary-button, .gradient-bg');
    
    gradientElements.forEach(element => {
        // Create gradient shift animation
        const keyframes = `
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
        `;
        
        // Add style element with keyframes
        const style = document.createElement('style');
        style.textContent = keyframes;
        document.head.appendChild(style);
        
        // Apply larger gradient background
        element.style.backgroundSize = '200% 200%';
        element.style.animation = 'gradientShift 8s ease infinite';
    });
}

// Add transition effects to navigation elements
function addTransitionEffectsToNavigation() {
    const navItems = document.querySelectorAll('.nav-item, .tab-button');
    
    navItems.forEach(item => {
        // Add transition effects
        item.style.transition = `all ${config.transitionSpeed} ease`;
        
        // Add hover effect
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'translateY(-2px)';
        });
        
        // Add mouse leave effect
        item.addEventListener('mouseleave', () => {
            item.style.transform = 'translateY(0)';
        });
    });
}

// Helper function to create wave effect on click
function createRippleEffect(event) {
    const button = event.currentTarget;
    
    // Create ripple element
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    button.appendChild(ripple);
    
    // Position the ripple
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    // Style the ripple
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    
    // Remove after animation completes
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Apply ripple effect to buttons
function applyRippleEffect() {
    const buttons = document.querySelectorAll('button, .action-button');
    
    buttons.forEach(button => {
        button.addEventListener('click', createRippleEffect);
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
    });
    
    // Add required CSS for ripple
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple {
            to {
                transform: scale(2.5);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize ripple effect
applyRippleEffect();