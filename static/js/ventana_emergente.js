// Obtener elementos del DOM
const mainImage = document.getElementById('mainImage');
const modal = document.getElementById('modal');
const closeModal = document.getElementById('closeModal');

// Abrir modal al hacer clic en la imagen principal
mainImage.addEventListener('click', () => {
    modal.classList.remove('hidden');
    modal.classList.add('visible');
});

// Cerrar modal al hacer clic en la "X"
closeModal.addEventListener('click', () => {
    modal.classList.remove('visible');
    modal.classList.add('hidden');
});

// Cerrar modal al hacer clic fuera del contenido
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        modal.classList.remove('visible');
        modal.classList.add('hidden');
    }
});