// Onload script of buffer.html
d3.json("http://localhost:8619/[buffer]?list").then(function(names) {
    init_handlers()
    update(names, 'keywords')
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
            this.value = squeeze(this.value)
            d3.select("#_description")
                .text(this.value)
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
    console.log(`Select name: ${name}`)
        // Display the paper
    src = `http://localhost:8619/[buffer]?name=${name}`
    d3.select("#pdf_iframe")
        .attr("src", src)
}