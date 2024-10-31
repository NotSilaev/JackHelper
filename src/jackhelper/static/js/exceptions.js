function exceptionsHandler(responseJSON) {
    /**
     * Intercepts exceptions and shows error modal window or validation error messages.
     * @param {Array} validation_errors Array of errors.
     */

    if (responseJSON) {
        errors = responseJSON['errors'];
        if (errors.length > 0) {
            return compileValidationErrorMessages(errors);
        }
    }
    return showModalWindow(
        windowID="standartModal", 
        height="170",
        heading="Ошибка", 
        content="Произошла неизвестная ошибка",
        accept_text='Понял',
        accept_action='null',
    )
}


function compileValidationErrorMessages(validation_errors) {
    /**
     * Sets error texts as a placeholder in invalid input fields.
     * @param {Array} validation_errors Array of errors.
     */

    validation_errors.forEach(error => {
        if (error['field']) {
            $('#' + error['field']).addClass('invalid-field');

            /** List of actions that will be performed after focusing on an invalid field */
            onfocus_actions = []
    
            /** Add a return of the value of the input field after focusing on it */
            current_value = $('#' + error['field']).val();
            onfocus_actions.push("$(this).val('" + current_value + "')");
            /** Set the value of the input field to null */
            $('#' + error['field']).val(null);
    
            /** Add a return of the placeholder of the input field after focusing on it */
            current_placeholder = $('#' + error['field']).attr('placeholder');
            onfocus_actions.push("$(this).attr('placeholder', '" + current_placeholder + "')");
            /** Set an error text as a field placeholder */
            $('#' + error['field']).attr('placeholder', error['text']);
            
            $('#' + error['field']).attr('onfocus', onfocus_actions.join('; '));
        } else {
            showModalWindow(
                windowID="standartModal", 
                height="200",
                heading="Ошибка", 
                content=error['text'],
                accept_text='Понял',
                accept_action='null',
            )
        }

    }); 
}