// Onload script of buffer.html
init_handlers()
clear_currents()

// Profiles
server_url = "http://localhost:8612"
buffer_list_url = `${server_url}/[buffer]?method=list`

function buffer_get_url(name) {
    return `${server_url}/[buffer]?method=get&name=${name}`
}

function buffer_commit_url(name) {
    return `${server_url}/[buffer]?method=commit&name=${name}`
}

function papers_get_by_title_url(title) {
    return `${server_url}/[papers]?method=get&title=${title}`
}

// Init buffer list
d3.json(buffer_list_url).then(function(names) {
    update_buffer_names(names)
    clear_currents()
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
    function title_onchange() {
        // Title onchange event
        t = document.getElementById("current_title")
        s = squeeze(t.value)
        t.value = s

        // Request
        url = papers_get_by_title_url(s)
        console.log(url)
        d3.json(url).then(function(c) {
            console.log(c)
        })
    }

    d3.select("#current_title")
        // Handle onchange of #current_title
        .on("change", function() {
            title_onchange()
        })

    // current_keywords
    function keywords_onchange() {
        // Keywords onchange event
        t = document.getElementById("current_keywords")
        s = squeeze(t.value) + ","
        t.value = s

        // Count keywords and write them into #_keywords
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
        // Add new keyword into #current_keywords
        .on("click", function() {
            s = `${this.innerText}, `
            document.getElementById("current_keywords").value += s
            keywords_onchange()
        })

    d3.select("#current_keywords")
        // Handle onchange of #current_keywords
        .on("change", function() {
            keywords_onchange()
        })

    // current_description
    function description_onchange() {
        // Keywords onchange event
        t = document.getElementById("current_description")
        s = squeeze(t.value)
        t.value = s

        // Count descriptions and write them to #_description
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
        // Add new description into #current_description
        .on("click", function() {
            s = `\n[${this.innerText}].\n`
            document.getElementById("current_description").value += s
            description_onchange()
        })

    d3.select('#current_description')
        // Handle onchange of #current_description
        .on("change", function() {
            description_onchange()
        })
}

function update_buffer_names(names, keywords) {
    // Update buffered names
    // names: File names in buffer server

    d3.select("#buffer_names")
        .selectAll("option")
        .remove()

    names = ["----"].concat(names)

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

    d3.select("#pdf_iframe")
        .attr("src", buffer_list_url)

    console.log("Buffered file names updated.")
}

function name_selection(name) {
    // Handle [name] selection event.
    // name: name selected.
    // yield: update PDF and clear_currents
    console.log(`Select name: ${name}`)

    // Update PDF
    d3.select("#pdf_iframe")
        .attr("src", buffer_get_url(name))

    // clear_currents
    clear_currents()

    // Update file name
    d3.select("#_name")
        .text(name)

    // Enable commit button if new name is selected
    document.getElementById("commit").disabled = false

}

function commit_current() {
    // Commit currents
    // Disable commit button
    document.getElementById("commit").disabled = true

    // Commit current contents
    // Get current name, title, keywords and description
    name = document.getElementById("buffer_names").value
    if (name.length == 0) {
        console.log("No file selected.")
        return
    }
    title = document.getElementById("current_title").value
    keywords = document.getElementById("current_keywords").value
    description = document.getElementById("current_description").value

    // Sent POST request
    url = buffer_commit_url(name)
    console.log(url)
    $.post(url, {
            date: (new Date()).valueOf(),
            title: title,
            keywords: keywords,
            description: description
        },
        function(data, status) {
            console.log(`Posting to ${url}`)
            console.log("Data: " + data + "\nStatus: " + status)
            alert(`Response: ${data}`)
                // Enable commit button
            document.getElementById("commit").disabled = false
        },
    );

    // Update buffer list
    // d3.json(buffer_list_url).then(function(names) {
    //     console.log(names)
    //     update_buffer_names(names)
    //     clear_currents()
    // })
}