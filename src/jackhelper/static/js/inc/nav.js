$(document).ready(function changeActivePageIcon() {
    selectedChapter = String(document.URL.split('/')[3]);
    if (selectedChapter == '') {
        selectedChapter = 'main'
    }
    $('#' + selectedChapter + '-page').addClass('active-page');
})


const navIcon = document.getElementById('nav-open');
const closeIcon = document.getElementById('nav-close');
const navbar = document.getElementById('navbar');

navIcon.addEventListener('click', () => {
    navbar.classList.add('open');
});
closeIcon.addEventListener('click', () => {
    navbar.classList.remove('open');
});
