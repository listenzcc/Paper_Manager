// Onload script of buffer.html
d3.json("http://localhost:8619/[buffer]?list").then(function(names) {
    init_handlers()
    update(names, 'keywords')
    clear_currents()
    console.log("Buffer html onload success.")
})

function squeeze(src) {
    // Squeeze more-than-one-spaces between words
    des = src
    while (des.includes("  ")) {
        des = des.replace(/  /g, " ")
    }
    // Squeeze more-than-one-comma between words
    while (des.includes(", ")) {
        des = des.replace(/, /g, ",")
    }
    while (des.includes(" ,")) {
        des = des.replace(/ ,/g, ",")
    }
    while (des.includes(",,")) {
        des = des.replace(/,,/g, ",")
    }
    return des
}

function clear_currents() {
    // Clear current_title, _keywords and _description.
    document.getElementById("current_title").value = ""
    document.getElementById("current_keywords").value = ""
    document.getElementById("current_description").value = ""
    d3.selectAll(".SummaryLabel")
        .text("")
    console.log('Currents cleared.')
}

function init_handlers() {
    // Initialize easy-to-use handlers

    // Title should not contain '\n'
    d3.select("#current_title")
        .on("change", function() {
            s = this.value.replace(/\n/g, " ")
            this.value = squeeze(s)
            d3.select("#_title")
                .text(this.value)
        })

    d3.select("#current_keywords")
        .on("change", function() {
            s = this.value.replace(/\n/g, ",")
            this.value = squeeze(s).replace(/,/g, ", ")
            d3.select("#_keywords")
                .text(this.value)
        })

    d3.select('#current_description')
        .on("change", function() {
            s = squeeze(this.value)
            this.value = s
            if (s.length > 500) {
                s = s.slice(0, 500) + "..."
            }
            d3.select("#_description")
                .text(s)
        })
}

function update(names, keywords) {
    // Update buffered names and known keywords
    // names: File names in buffer server
    // keywords: Keywords in paper server

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

    console.log("Buffer html update success.")
}

function name_selection(name) {
    // Operate when name selected.
    // name: name selected.
    // yield: update PDF and clear_currents
    console.log(`Select name: ${name}`)

    // Update PDF
    src = `http://localhost:8619/[buffer]?name=${name}`
    d3.select("#pdf_iframe")
        .attr("src", src)

    // clear_currents
    clear_currents()
}