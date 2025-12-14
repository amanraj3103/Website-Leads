// Form handling and validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('leadForm');
    const submitBtn = document.getElementById('submitBtn');
    const formMessage = document.getElementById('formMessage');

    // Form validation
    function validateForm() {
        let isValid = true;
        
        // Clear previous errors
        document.querySelectorAll('.form-error').forEach(el => {
            el.textContent = '';
        });
        
        // Validate name
        const name = document.getElementById('name').value.trim();
        if (!name) {
            showError('name-error', 'Please enter your full name');
            isValid = false;
        }
        
        // Validate phone
        const phone = document.getElementById('phone').value.trim();
        if (!phone) {
            showError('phone-error', 'Please enter your phone number');
            isValid = false;
        } else if (!/^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/.test(phone)) {
            showError('phone-error', 'Please enter a valid phone number');
            isValid = false;
        }
        
        // Validate email
        const email = document.getElementById('email').value.trim();
        if (!email) {
            showError('email-error', 'Please enter your email address');
            isValid = false;
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            showError('email-error', 'Please enter a valid email address');
            isValid = false;
        }
        
        // Validate place
        const place = document.getElementById('place').value.trim();
        if (!place) {
            showError('place-error', 'Please enter your place of residence');
            isValid = false;
        }
        
        // Validate consent checkbox
        const consentCheckbox = document.getElementById('consentCheckbox');
        if (!consentCheckbox.checked) {
            showError('consent-error', 'You must consent to the Privacy Policy to submit your information');
            isValid = false;
        }
        
        return isValid;
    }
    
    function showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
        }
    }
    
    function showMessage(type, message) {
        formMessage.className = `form-message ${type}`;
        formMessage.textContent = message;
        formMessage.style.display = 'block';
        
        // Scroll to message
        formMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Auto-hide success message after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                formMessage.style.display = 'none';
            }, 5000);
        }
    }
    
    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            showMessage('error', 'Please fill in all required fields correctly.');
            return;
        }
        
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        submitBtn.querySelector('.button-text').textContent = 'Submitting...';
        
        // Hide previous messages
        formMessage.style.display = 'none';
        
        // Collect form data
        const formData = {
            service: 'Job Europe',
            work: 'Truck Driver',
            name: document.getElementById('name').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            email: document.getElementById('email').value.trim(),
            place: document.getElementById('place').value.trim(),
            timestamp: new Date().toISOString()
        };
        
        try {
            // Send data to backend
            const response = await fetch('/api/submit-lead', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json().catch((parseError) => {
                console.error('Failed to parse JSON response:', parseError);
                return {};
            });
            
            console.log('API Response:', {
                status: response.status,
                ok: response.ok,
                result: result
            });
            
            if (!response.ok) {
                console.error('Response not OK:', response.status, result);
                throw new Error(result.error || `Server error: ${response.status}`);
            }
            
            // Check if the response indicates success
            if (result.success === true || result.success === 'true') {
                // Success
                console.log('Success! Showing success message');
                showMessage('success', '✅ Thank you! Your information has been submitted successfully. Our team will contact you within 24 hours.');
                form.reset();
            } else {
                // Response was OK but success is false or missing
                console.error('Response OK but success is not true:', result);
                throw new Error(result.error || result.message || 'Failed to save lead data');
            }
            
            // Reset button
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
            submitBtn.querySelector('.button-text').textContent = 'Submit Information';
        } catch (error) {
            console.error('Form submission error:', error);
            
            // Check if it's a network error
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                showMessage('error', '❌ Unable to connect to server. Please make sure the backend server is running on port 5000, or contact us directly at +91 8590060508.');
            } else {
                showMessage('error', `❌ ${error.message || 'Sorry, there was an error submitting your information. Please try again or contact us directly.'}`);
            }
            
            // Reset button
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
            submitBtn.querySelector('.button-text').textContent = 'Submit Information';
        }
    });
    
    // Real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            const errorId = this.id + '-error';
            const errorElement = document.getElementById(errorId);
            if (errorElement) {
                errorElement.textContent = '';
            }
        });
    });
    
    // Handle consent checkbox validation
    const consentCheckbox = document.getElementById('consentCheckbox');
    if (consentCheckbox) {
        consentCheckbox.addEventListener('change', function() {
            const errorElement = document.getElementById('consent-error');
            if (errorElement && this.checked) {
                errorElement.textContent = '';
            }
        });
    }
    
    // Privacy Policy Modal Handling
    const privacyModal = document.getElementById('privacyModal');
    const openPrivacyModalBtn = document.getElementById('openPrivacyModal');
    const closePrivacyModalBtn = document.getElementById('closePrivacyModal');
    const acceptPrivacyModalBtn = document.getElementById('acceptPrivacyModal');
    const privacyModalOverlay = privacyModal.querySelector('.privacy-modal-overlay');
    
    function openPrivacyModal() {
        privacyModal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
    
    function closePrivacyModal() {
        privacyModal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    }
    
    // Open modal when clicking the Privacy Policy link
    if (openPrivacyModalBtn) {
        openPrivacyModalBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            openPrivacyModal();
        });
    }
    
    // Close modal when clicking close button
    if (closePrivacyModalBtn) {
        closePrivacyModalBtn.addEventListener('click', closePrivacyModal);
    }
    
    // Close modal when clicking "I Understand" button
    if (acceptPrivacyModalBtn) {
        acceptPrivacyModalBtn.addEventListener('click', function() {
            closePrivacyModal();
            // Optionally auto-check the consent checkbox
            if (consentCheckbox) {
                consentCheckbox.checked = true;
                // Clear any error message
                const errorElement = document.getElementById('consent-error');
                if (errorElement) {
                    errorElement.textContent = '';
                }
            }
        });
    }
    
    // Close modal when clicking overlay
    if (privacyModalOverlay) {
        privacyModalOverlay.addEventListener('click', closePrivacyModal);
    }
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && privacyModal.classList.contains('active')) {
            closePrivacyModal();
        }
    });
    
    // Prevent modal from closing when clicking inside modal content
    const modalContent = privacyModal.querySelector('.privacy-modal-content');
    if (modalContent) {
        modalContent.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all animated elements
    document.querySelectorAll('.animate-fade-in-up').forEach(el => {
        observer.observe(el);
    });
    
    // Info Cards Carousel (Mobile Only)
    const infoCarousel = document.getElementById('infoCarousel');
    const carouselDots = document.querySelectorAll('.carousel-dot');
    let carouselInterval = null;
    let currentSlide = 0;
    const totalSlides = 3;
    let isMobile = window.innerWidth <= 768;
    
    function updateCarouselDots(activeIndex) {
        carouselDots.forEach((dot, index) => {
            if (index === activeIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    function goToSlide(slideIndex) {
        if (!infoCarousel || !isMobile) return;
        
        currentSlide = slideIndex;
        const cardWidth = infoCarousel.offsetWidth;
        infoCarousel.scrollTo({
            left: slideIndex * cardWidth,
            behavior: 'smooth'
        });
        updateCarouselDots(slideIndex);
    }
    
    function nextSlide() {
        if (!isMobile) return;
        currentSlide = (currentSlide + 1) % totalSlides;
        goToSlide(currentSlide);
    }
    
    function startCarousel() {
        if (!isMobile || carouselInterval) return;
        carouselInterval = setInterval(nextSlide, 4000); // Auto-advance every 4 seconds
    }
    
    function stopCarousel() {
        if (carouselInterval) {
            clearInterval(carouselInterval);
            carouselInterval = null;
        }
    }
    
    // Handle dot clicks
    carouselDots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            stopCarousel();
            goToSlide(index);
            startCarousel();
        });
    });
    
    // Handle scroll events to update dots
    if (infoCarousel) {
        infoCarousel.addEventListener('scroll', () => {
            if (!isMobile) return;
            const scrollPosition = infoCarousel.scrollLeft;
            const cardWidth = infoCarousel.offsetWidth;
            const newSlide = Math.round(scrollPosition / cardWidth);
            
            if (newSlide !== currentSlide) {
                currentSlide = newSlide;
                updateCarouselDots(newSlide);
            }
        });
        
        // Pause carousel on touch/interaction
        infoCarousel.addEventListener('touchstart', stopCarousel);
        infoCarousel.addEventListener('touchend', () => {
            setTimeout(startCarousel, 3000); // Resume after 3 seconds
        });
        
        infoCarousel.addEventListener('mouseenter', stopCarousel);
        infoCarousel.addEventListener('mouseleave', startCarousel);
    }
    
    // Handle window resize
    function handleResize() {
        const wasMobile = isMobile;
        isMobile = window.innerWidth <= 768;
        
        if (wasMobile !== isMobile) {
            stopCarousel();
            if (isMobile) {
                // Reset to first slide on mobile
                goToSlide(0);
                startCarousel();
            } else {
                // Reset scroll position on desktop
                if (infoCarousel) {
                    infoCarousel.scrollLeft = 0;
                }
                updateCarouselDots(0);
            }
        }
    }
    
    window.addEventListener('resize', handleResize);
    
    // Initialize carousel on mobile
    if (isMobile) {
        goToSlide(0);
        startCarousel();
    }
});

