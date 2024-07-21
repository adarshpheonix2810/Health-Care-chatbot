function validateForm(event) {
    
    event.preventDefault();

    
    const name = document.getElementById('the-name').value.trim();
    const email = document.getElementById('the-email').value.trim();
    const phone = document.getElementById('the-phone').value.trim();
    const reason = document.getElementById('the-reason').value;
    const message = document.getElementById('the-message').value.trim();


    if (!name) {
        alert('Please enter your name.');
        return;
    }
    if (!email) {
        alert('Please enter your email address.');
        return;
    }
    if (!phone) {
        alert('Please enter your phone number.');
        return;
    }
    if (reason === "") {
        alert('Please select a reason for contact.');
        return;
    }
    if (!message) {
        alert('Please enter your message.');
        return;
    }

    alert('Thank you for your message! We will get back to you shortly.');
  
}


document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', validateForm);
});