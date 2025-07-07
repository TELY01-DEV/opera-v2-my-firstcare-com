#!/usr/bin/env python3
"""
Quick enhancement script to add data validation to master data forms
This adds client-side validation for better user experience
"""

def add_form_validation():
    """Add JavaScript validation to master data forms"""
    
    validation_script = """
<script>
// Master Data Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-master-data-form]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Validate required fields
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    showFieldError(field, 'This field is required');
                    isValid = false;
                } else {
                    clearFieldError(field);
                }
            });
            
            // Validate code format (alphanumeric, no spaces)
            const codeFields = form.querySelectorAll('input[name="code"]');
            codeFields.forEach(function(field) {
                if (field.value && !/^[A-Za-z0-9]+$/.test(field.value)) {
                    showFieldError(field, 'Code must be alphanumeric with no spaces');
                    isValid = false;
                }
            });
            
            // Validate email format
            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(function(field) {
                if (field.value && !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(field.value)) {
                    showFieldError(field, 'Please enter a valid email address');
                    isValid = false;
                }
            });
            
            // Validate phone format (Thai format)
            const phoneFields = form.querySelectorAll('input[name="phone"]');
            phoneFields.forEach(function(field) {
                if (field.value && !/^[0-9]{8,10}$/.test(field.value.replace(/[-\\s]/g, ''))) {
                    showFieldError(field, 'Please enter a valid phone number (8-10 digits)');
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Scroll to first error
                const firstError = form.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    });
    
    function showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
});
</script>
"""
    
    print("Form validation script ready to be added to templates!")
    print("Add this to the end of your form.html template:")
    print(validation_script)

if __name__ == "__main__":
    add_form_validation()
