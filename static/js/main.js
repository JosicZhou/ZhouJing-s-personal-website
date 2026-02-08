// Main JavaScript — Zhou Jing's Website (Apple-style minimal)

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initRevealOnScroll();
});

// ====== Navigation ======
function initNavigation() {
    const navbar = document.querySelector('.nav-apple');
    
    // Subtle scroll effect
    let lastScrollY = 0;
    window.addEventListener('scroll', function() {
        const scrollY = window.scrollY;
        if (scrollY > 10) {
            navbar.style.borderBottomColor = 'rgba(0,0,0,0.1)';
        } else {
            navbar.style.borderBottomColor = 'rgba(0,0,0,0.06)';
        }
        lastScrollY = scrollY;
    }, { passive: true });
}

// ====== Mobile Menu ======
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    const icon = document.getElementById('menuIcon');
    
    if (menu.classList.contains('active')) {
        closeMobileMenu();
    } else {
        menu.style.display = 'block';
        requestAnimationFrame(() => {
            menu.classList.add('active');
        });
        document.body.style.overflow = 'hidden';
        // Change to X icon
        icon.innerHTML = '<line x1="6" y1="6" x2="18" y2="18"></line><line x1="6" y1="18" x2="18" y2="6"></line>';
    }
}

function closeMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    const icon = document.getElementById('menuIcon');
    
    menu.classList.remove('active');
    document.body.style.overflow = '';
    // Restore hamburger icon
    icon.innerHTML = '<line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="18" x2="21" y2="18"></line>';
    
    setTimeout(() => {
        if (!menu.classList.contains('active')) {
            menu.style.display = 'none';
        }
    }, 350);
}

// ====== Reveal on Scroll ======
function initRevealOnScroll() {
    const elements = document.querySelectorAll('.reveal');
    
    if (!elements.length) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    });
    
    elements.forEach(el => observer.observe(el));
}

// ====== Utility ======
window.toggleMobileMenu = toggleMobileMenu;
window.closeMobileMenu = closeMobileMenu;
