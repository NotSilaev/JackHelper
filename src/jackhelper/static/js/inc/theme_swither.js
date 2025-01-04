const themeSwitcher = document.querySelector('.theme-swither');
const buttons = themeSwitcher.querySelectorAll('button');

const switchTheme = (theme) => {
    localStorage.setItem('theme', theme);

    document.body.className = theme;

    buttons.forEach(button => button.classList.remove('active-theme'));

    const activeButton = document.getElementById(theme);
    activeButton.classList.add('active-theme');
};

buttons.forEach(button => {
    button.addEventListener('click', () => {
        const theme = button.id;
        switchTheme(theme);
    });
});

const savedTheme = localStorage.getItem('theme') || 'light';
switchTheme(savedTheme);