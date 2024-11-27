function showModalWindow(windowID, height, heading, content, accept_text, accept_action) {
    if (height) {
        $('#' + windowID + ' ' + '.modal-window').css('height', height);
    }
    if (heading) {
        $('#' + windowID + ' ' + '.modal-heading h2').html(heading);
    }
    if (content) {
        $('#' + windowID + ' ' + '.modal-content').css('display', 'inline-block');
        $('#' + windowID + ' ' + '.modal-content').html('<p>' + content + '</p>');
    }
    if (accept_text && accept_action) {
        $('#' + windowID + ' ' + '.modal-buttons').css('display', 'flex');
        $('#' + windowID + ' ' + '.modal-buttons .accept').css('display', 'block')
        $('#' + windowID + ' ' + '.modal-buttons .accept').html('<p>' + accept_text + '</p>');
        $('#' + windowID + ' ' + '.modal-buttons .accept').attr(
            'onclick', 'hideModalWindow("standartModal");' + '; ' + accept_action
        );
    } else {
        $('#' + windowID + ' ' + '.modal-buttons .accept').empty()
        $('#' + windowID + ' ' + '.modal-buttons .accept').attr('onclick', null)
        $('#' + windowID + ' ' + '.modal-buttons .accept').css('display', 'none')
    }

    $('#' + windowID).css('display', 'table')
}

function hideModalWindow(windowID) {
    $('#' + windowID).css('display', 'none')
}

$(document).mouseup(function (e) {
    if (e.target.classList[0] === 'inner'){
        windowID = $('.inner').parent().attr('id')
        $('#' + windowID).css('display', 'none')
    }
});