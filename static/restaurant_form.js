'use strict'

const imageInput = document.getElementById('itemImages');
const imagePreview = document.getElementById('imagePreview');

// Preview images
imageInput.addEventListener('change', function(event) {
    imagePreview.innerHTML = '';
    const files = event.target.files;
    if (files.length < 3) {
        alert('You must upload at least 3 images.');
    } else {
        for (const file of files) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                imagePreview.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    }
});

// Handle form submission (Add/Edit item)
function handleSubmit() {
    const itemName = document.getElementById('itemName').value;
    const itemDescription = document.getElementById('itemDescription').value;
    const itemPrice = document.getElementById('itemPrice').value;
    const files = imageInput.files;

    if (files.length < 3) {
        alert('Please upload at least 3 images.');
        return;
    }

    const formData = new FormData();
    formData.append('itemName', itemName);
    formData.append('itemDescription', itemDescription);
    formData.append('itemPrice', itemPrice);

    for (const file of files) {
        formData.append('itemImages', file);
    }

    // Assuming we're sending data to a server endpoint (adjust URL accordingly)
    fetch('/add-or-edit-item', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => alert('Item added/edited successfully!'))
      .catch(error => console.error('Error:', error));
}