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