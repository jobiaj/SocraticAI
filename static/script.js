document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.input-form');
    const textarea = document.querySelector('textarea');
    const button = document.querySelector('button[type="submit"]');
    
    form.addEventListener('submit', function(e) {
        if (textarea.value.trim() === '') {
            e.preventDefault();
            alert('Please enter a question to begin your learning journey.');
            return;
        }
        
        button.disabled = true;
        button.textContent = 'Exploring...';
    });
    
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            form.submit();
        }
    });
    
    if (window.location.search || document.querySelector('.dialogue-history')) {
        textarea.focus();
    }
});