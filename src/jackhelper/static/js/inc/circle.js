function getCircleFrame(
    id, 
    width, 
    height, 
    percent, 
    internal_text=null,
    show_internal_text=true,
    progress_color='4caf50',
) {
    /**
     * Generates an HTML template with a circle chart.
     * @param  {[String]} id []
     * @param  {[String]} id []
     * @param  {[String]} id []
     * @param  {[String]} id []
     * @param  {[String]} id []
     * @param  {[String]} id []
     * @param  {[String]} id []
     */
    
    const cx = width / 2;
    const cy = height / 2;
    const min_side = Math.min(width, height);
    const r = Math.floor(min_side / 2) - (Math.floor(min_side / 2) * 20 / 100);
    const stroke_width = ((width + height) / 2 * 10) / 100;
    const progress_stroke_width = stroke_width - (stroke_width * 30) / 100;

    const internal_text_display = show_internal_text ? 'block' : 'none';
    const internal_text_font_size = min_side - (min_side * 85) / 100;

    const circumference = 2 * Math.PI * r;
    var offset = circumference - (percent / 100) * circumference;

    if (percent > 100) {
        var offset = 0;
    }

    const circle_frame = `
        <div id="circle-${id}" class="circle-container" style="width: ${width}px; height: ${height}px;">
            <svg width="${width}" height="${height}">
                <circle cx="${cx}" cy="${cy}" r="${r}" 
                        class="circle-bg" style="stroke-width: ${stroke_width}; fill: none;"></circle>
                <circle cx="${cx}" cy="${cy}" r="${r}" 
                        class="circle-progress" style="
                            stroke-width: ${progress_stroke_width}; 
                            fill: none; 
                            stroke-dasharray: ${circumference}; 
                            stroke-dashoffset: ${offset};
                            stroke: #${progress_color};
                        "></circle>
            </svg>
            
            <div class="percentage" 
                 style="display: ${internal_text_display}; 
                 font-size: ${internal_text_font_size}px">
                ${internal_text || percent + "%"}
            </div>
        </div>`;

    return circle_frame;
}
