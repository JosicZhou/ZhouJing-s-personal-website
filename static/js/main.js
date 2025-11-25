// Main JavaScript for Zhou Jing's Website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initNavigation();
    initAnimations();
    initSmoothScrolling();
    
    console.log('Zhou Jing\'s website loaded successfully!');
});

// Navigation functionality
function initNavigation() {
    const navbar = document.querySelector('.navbar');
    
    // Add scroll effect to navbar
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Active nav link highlighting
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPage = window.location.pathname;
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
}

// Animation functionality
function initAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.highlight-card, .project-card, .experience-item, .education-item');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Utility functions
function showLoading(element) {
    if (element) {
        element.innerHTML = '<span class="loading"></span>';
    }
}

function hideLoading(element, originalContent) {
    if (element) {
        element.innerHTML = originalContent;
    }
}

// Form validation helper
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Contact form functionality (for future use)
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            showLoading(submitBtn);
            
            // Simulate form submission
            setTimeout(() => {
                hideLoading(submitBtn, originalText);
                alert('Thank you for your message! I\'ll get back to you soon.');
                this.reset();
            }, 2000);
        });
    }
}

// Language switching functionality
function switchLanguage(lang) {
    // This function will be enhanced when backend language switching is implemented
    console.log(`Switching to language: ${lang}`);
}

// Performance optimization
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error occurred:', e.error);
    // In production, you might want to send this to an error tracking service
});

// Analytics helper (for future use)
function trackEvent(eventName, eventData = {}) {
    // Google Analytics or other tracking service integration
    console.log(`Event tracked: ${eventName}`, eventData);
}

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    // Skip to main content on Tab (accessibility)
    if (e.key === 'Tab' && !e.shiftKey && document.activeElement === document.body) {
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.focus();
        }
    }
});

// Mobile menu handling
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking a link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            });
        });
    }
}

// Initialize mobile menu on DOM load
document.addEventListener('DOMContentLoaded', initMobileMenu);

// Export functions for potential external use
window.ZhouJingWebsite = {
    trackEvent,
    switchLanguage,
    validateEmail,
    showLoading,
    hideLoading
};
