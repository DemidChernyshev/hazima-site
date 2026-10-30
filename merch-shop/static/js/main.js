document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('promo-modal');

    // Показываем через 3 секунды, если не закрывали
    if (modal && !localStorage.getItem('hazima_club')) {
        setTimeout(() => {
            modal.style.display = 'flex';
        }, 3000);
    }

    const closeBtn = document.getElementById('close-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            localStorage.setItem('hazima_club', 'true');
        });
    }

    const form = document.getElementById('promo-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Сайламә! Ты в клубе Hazima. Промокод на первый заказ: HAZIMA10');
            modal.style.display = 'none';
            localStorage.setItem('hazima_club', 'true');
        });
    }
});