function loadingSpinner(color) {
    /**
     * Adds a loading spinner to the HTML element.
     * @param {String} color 'Loading spinner color'
     */

    const loading_spinner =  `
        <svg class="spinner" viewBox="0 0 50 50">
            <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5" style="stroke: ${color};">
            </circle>
        </svg>`
    return loading_spinner;
};


function makeScrollable(element_id, elements_class=null) {
    /**
     * Makes any HTML element scrollable.
     * @param {String} element_id
     * @param {String} elements_class
     */

    if (elements_class) {
        var scrollables_list = Array.from(document.getElementsByClassName(elements_class));
    } else {
        var scrollables_list = [document.getElementById(element_id)];
    };
    scrollables_list.forEach(scrollable => {
        scrollable.addEventListener('wheel', (event) => {
            if (event.deltaY !== 0) {
                scrollable.scrollLeft += event.deltaY;
                event.preventDefault();
            };
        }); 
    });
};


function getValue(selector) {
    /**
     * Returns any selector value if it isn't undefined.
     * @param {String} element_id
     */

    var value = $(selector).val();
    return value === "" ? undefined : value;
};


function numberToContinentalStyle(value) {
    /**
     * Translates numbers to the "Continental style" (from "1200300.40" to "1 200 300,40").
     * @param {String} element_id
     */

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
};


function getCookie(name) {
    /**
     * Obtains client cookie by name.
     * @param {String} name 'Cookie name'
     */

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
};


function getDaysInMonth(year, month) {
    return new Date(year, month + 1, 0).getDate();
};


function fullnameToInitials(fullname, last_name_index=0) {
    /**
     * Converts person fullname to initials (example: "Silaev Nikita Dmitrievich" -> "Silaev N. D.").
     * @param {String} fullname [person fullname]
     * @param {String} last_name_index [index of person last name in fullname]
     */

    var converted_name_parts = [];
    let splitted_fullname = fullname.split(' ');
    splitted_fullname.forEach((name_part, name_part_index) => {
        if (name_part_index !== last_name_index) {
            var name_part = name_part[0] + '.'
        };
        converted_name_parts.push(name_part);
    });

    const name_initials = converted_name_parts.join(' ');
    return name_initials;
};


function isNumeric(str) {
    const num = Number(str);
    return !isNaN(str) && str.trim() !== '' && isFinite(num);
};