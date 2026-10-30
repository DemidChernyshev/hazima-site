// Плавные переходы + метрика на добавление в корзину
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.add-form');
    if (form && window.ym) {
        form.addEventListener('submit', () => {
            ym(XXXXXXXX, 'reachGoal', 'add_to_cart');
        });
    }

    const checkoutForm = document.querySelector('.checkout-form');
    if (checkoutForm && window.ym) {
        checkoutForm.addEventListener('submit', () => {
            ym(XXXXXXXX, 'reachGoal', 'order_submit');
        });
    }
});