function loadingSpinner(color) {
    const loading_spinner =  `
        <svg class="spinner" viewBox="0 0 50 50">
            <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5" style="stroke: ${color};">
            </circle>
        </svg>`
    return loading_spinner;
}

function makeScrollable(element_id) {
    const scrollable = document.getElementById(element_id);
    scrollable.addEventListener('wheel', (event) => {
        if (event.deltaY !== 0) {
            scrollable.scrollLeft += event.deltaY;
        event.preventDefault();
        }
    });
}

function getValue(selector) {
    var value = $(selector).val();
    return value === "" ? undefined : value;
}

function numberToContinentalStyle(value) {
    if (value === null || value === undefined) {
        return "0";
    }

    let [integerPart, decimalPart] = value.toFixed(2).split('.');
    integerPart = parseInt(integerPart).toLocaleString('en').replace(/,/g, ' ');

    if (decimalPart !== '00') {
        return `${integerPart},${decimalPart}`;
    } else {
        return integerPart;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}