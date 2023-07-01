const cardNumberInput = document.getElementById('card-number');

cardNumberInput.addEventListener('input', function (e) {
    const input = e.target.value.replace(/\D/g, '').substring(0, 16);
    const spacedInput = input.replace(/(.{4})/g, '$1 ');
    e.target.value = spacedInput.trim();
});


