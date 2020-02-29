// DOM operators
// Add, remove and change DOMs

console.log('dom_operator starts.')

// Update names
// GET names by [buffer_list_url]
// remove existing name options
// create names options 
function update_buffer_names() {
    d3.json(buffer_list_url).then(function(names) {
        // Remove old options
        d3.select("#buffer_names")
            .selectAll("option")
            .remove()

        // Add '----' entry
        names = ["----"].concat(names)

        // Add names into options
        d3.select("#buffer_names")
            .on("change", function() {
                name_selection(this.value);
            })
            .selectAll()
            .data(names)
            .enter()
            .append("option")
            .attr("value", function(d) { return d; })
            .text(function(d) { return d; });

        // Update #pdf_iframe
        // TODO: Make it more pretty, now it is ugly.
        d3.select("#pdf_iframe")
            .attr("src", buffer_list_url)

        console.log("Buffered file names updated.")
    })
}

// Update keywords
// GET keywords by [papers_get_keywords_url],
// remove existing keyword buttons
// create keyword buttons
function update_keywords() {
    d3.json(papers_get_keywords_url).then(function(keywords) {
        // Remove old buttons
        d3.select("#keyword_buttons")
            .selectAll("button")
            .remove()

        // Add keywords as buttons
        d3.select("#keyword_buttons")
            .selectAll("button")
            // Bound to keywords
            .data(keywords)
            .enter()
            // Add buttons
            .append("button")
            .attr("class", "KeywordsButton")
            .attr("value", function(d) { return d; })
            .text(function(d) { return d; })
            // Handle 'click' event
            .on("click", function() {
                s = `${this.innerText}, `
                document.getElementById("current_keywords").value += s
                keywords_onchange()
            })
            // Adding enhancement when mouseover
            .on("mouseover", function() {
                this.style.transform = ("scale(1.2, 1.2)")
            })
            .on("mouseout", function() {
                this.style.transform = ("")
            })
    })
}

// Update descriptions
// GET descriptions by [papers_get_descriptions_url],
// remove existing description buttons
// create description buttons
function update_descriptions() {
    d3.json(papers_get_descriptions_url).then(function(descriptions) {
        // Remove old buttons
        d3.select("#description_buttons")
            .selectAll("button")
            .remove()

        // Add descriptions as buttons
        d3.select("#description_buttons")
            .selectAll("button")
            // Bound to descriptions
            .data(descriptions)
            .enter()
            // Add buttons
            .append("button")
            .attr("class", "descriptionsButton")
            .attr("value", function(d) { return d; })
            .text(function(d) { return d; })
            // Handle 'click' event
            .on("click", function() {
                s = `## ${this.innerText}`
                document.getElementById("current_descriptions").value += s
                descriptions_onchange()
            })
            // Adding enhancement when mouseover
            .on("mouseover", function() {
                this.style.transform = ("scale(1.2, 1.2)")
            })
            .on("mouseout", function() {
                this.style.transform = ("")
            })
    })
}

// Clear currents
// clear current_title, current_keywords and current_description
// clear .SummayrLabel
function clear_currents() {
    document.getElementById("current_title").value = ""
    document.getElementById("current_keywords").value = ""
    document.getElementById("current_descriptions").value = ""
    d3.selectAll(".SummaryLabel")
        .text("")
    console.log('Currents cleared.')
}

// Displays of containers
// toggle visibility of containers
// based on checkboxes
function toggle_displays() {
    console.log('--')

    // Toggle title containers
    document.getElementById("current_title_container").hidden = !document.getElementById("current_title_checkbox").checked

    // Toggle keywords containers
    document.getElementById("current_keywords_container").hidden = !document.getElementById("current_keywords_checkbox").checked

    // Toggle descriptions containers
    document.getElementById("current_descriptions_container").hidden = !document.getElementById("current_descriptions_checkbox").checked
}

console.log('dom_operator success.')