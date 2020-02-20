// Onload script of buffer.html
init_handlers()
clear_currents()

d3.json("http://localhost:8619/[buffer]?list").then(function(names) {
    update_buffer_names(names)
})

console.log("Buffer html onload success.")

function squeeze(src) {
    // Squeeze [src] string
    // Change all enter into space
    des = src.replace(/\n/g, " ")
        // Squeeze double-spaces
    while (des.includes("  ")) {
        des = des.replace(/  /g, " ")
    }

    // Squeeze space around ",", ":" and "."
    des = des.replace(/: /g, ":").replace(/ :/g, ":").replace(/::/g, ":")
    des = des.replace(/, /g, ",").replace(/ ,/g, ",").replace(/,,/g, ",")
    des = des.replace(/\. /g, ".").replace(/ \./g, ".").replace(/\.\./g, ".")

    // Stack i.e.
    des = des.replace(/i\.e\./g, "---ie---")
    des = des.replace(/et al\./g, "---etal---")
    des = des.replace(/e\.g\./g, "---eg---")

    // Add space after ",", ":" and "."
    // Remove leading spcace
    des = des.replace(/\./g, ".\n").replace(/:/g, ": ").replace(/,/g, ", ").replace(/^ /g, "")

    // Resume i.e.
    des = des.replace(/---ie---/g, "i.e. ")
    des = des.replace(/---etal---/g, "et al. ")
    des = des.replace(/---eg---/g, "e.g. ")

    // Deal tail
    if (des.endsWith("\n")) {
        des = des.slice(0, -1)
    }
    if (des.endsWith(", ")) {
        des = des.slice(0, -2)
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
    // Commit button handler
    d3.select("#commit")
        .on("click", function() {
            commit_current()
        })

    // Auto regulize string in current_title, current_keywords, current_description
    // current_title
    d3.select("#current_title")
        .on("change", function() {
            this.value = squeeze(this.value)
            d3.select("#_title")
                .text(this.value)
        })

    // current_keywords
    function keywords_onchange() {
        // Keywords onchange event
        t = document.getElementById("current_keywords")
        s = squeeze(t.value) + ","
        t.value = s
        j = 0
        ss = `${j}-{`
        for (var i = 0; i < s.length; i++) {
            if (s[i] == ",") {
                j += 1
                ss += `}, ${j}-{`
            } else {
                ss += s[i]
            }
        }
        ss.replace(/{ /g, "{")
        if (ss.endsWith("{")) {
            ss = ss.slice(0, -1)
        }
        d3.select("#_keywords")
            .text(ss)
    }

    d3.selectAll(".KeywordsButton")
        .on("click", function() {
            s = `${this.innerText}, `
            document.getElementById("current_keywords").value += s
            keywords_onchange()
        })

    d3.select("#current_keywords")
        .on("change", function() {
            keywords_onchange()
        })

    // current_description
    function description_onchange() {
        // Keywords onchange event
        t = document.getElementById("current_description")
        s = squeeze(t.value)
        t.value = s
        j = 0
        ss = `${j}-`
        c = 0
        for (var i = 0; i < s.length; i++) {
            if (s[i] == "[") {
                c += 1
            }
            if (c > 0) {
                ss += s[i]
            }
            if (s[i] == "]") {
                c -= 1
                if (c == 0) {
                    j += 1
                    ss += `, ${j}-`
                }
            }
        }
        d3.select("#_description")
            .text(ss)
    }

    d3.selectAll(".DescriptionButton")
        .on("click", function() {
            s = `\n[${this.innerText}].\n`
            document.getElementById("current_description").value += s
            description_onchange()
        })

    d3.select('#current_description')
        .on("change", function() {
            description_onchange()
        })
}

function update_buffer_names(names, keywords) {
    // Update buffered names
    // names: File names in buffer server

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

    console.log("Buffered file names updated.")
}

function name_selection(name) {
    // Handle [name] selection event.
    // name: name selected.
    // yield: update PDF and clear_currents
    console.log(`Select name: ${name}`)

    // Update PDF
    src = `http://localhost:8619/[buffer]?name=${name}`
    d3.select("#pdf_iframe")
        .attr("src", src)

    // clear_currents
    clear_currents()

    // Update file name
    d3.select("#_name")
        .text(name)

}

function commit_current() {
    // Commit current contents
    name = document.getElementById("buffer_names").value
    if (name.length == 0) {
        console.log("No file selected.")
        return
    }
    title = document.getElementById("current_title").value
    keywords = document.getElementById("current_keywords").value
    description = document.getElementById("current_description").value

    url = `http://localhost:8619/[buffer]?commit&name=${name}`

    console.log(url)
    $.post(url, {
            date: String(new Date()),
            title: title,
            keywords: keywords,
            description: description
        },
        function(data, status) {
            console.log(`Posting to ${url}`)
            console.log("Data: " + data + "\nStatus: " + status)
        });
}