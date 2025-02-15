document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.header__menu-toggle');
    const nav = document.querySelector('.header__nav');

    menuToggle.addEventListener('click', function() {
        nav.classList.toggle('header__nav--open');
    });
});