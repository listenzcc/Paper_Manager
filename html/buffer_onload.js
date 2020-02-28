// Onload script of buffer.html

// Init buffer, keywords and descriptions
update_buffer_names()
update_keywords()
update_descriptions()
clear_currents()

init_handlers()

console.log("Buffer html onload success.")

// Initialize handlers
// Add handle to commit button
// Auto regulize string in current_title, current_keywords, current_description when they are changed
function init_handlers() {
    // Handle click of commit button
    d3.select("#commit")
        .on("click", function() {
            commit_currents()
        })

    // Handle onchange of #current_title
    d3.select("#current_title")
        .on("change", function() {
            title_onchange()
        })

    // Handle onchange of #current_keywords
    d3.select("#current_keywords")
        .on("change", function() {
            keywords_onchange()
        })

    // Handle onchange of #current_description
    d3.select('#current_descriptions')
        .on("change", function() {
            descriptions_onchange()
        })

    // Handle onchange of CheckBox
    d3.select('.CheckBox')
        .on("change", function() {
            toggle_displays()
        })

    // Toogle checkboxes
    d3.select("#current_title_logo")
        .on("click", function() {
            d = document.getElementById("current_title_checkbox")
            d.checked = !d.checked
            toggle_displays()
        })
    d3.select("#current_keywords_logo")
        .on("click", function() {
            d = document.getElementById("current_keywords_checkbox")
            d.checked = !d.checked
            toggle_displays()
        })
    d3.select("#current_descriptions_logo")
        .on("click", function() {
            d = document.getElementById("current_descriptions_checkbox")
            d.checked = !d.checked
            toggle_displays()
        })
}