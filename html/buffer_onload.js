// Onload script of buffer.html
// Profiles
server_url = "http://localhost:8612"

// Buffer list names, GET
buffer_list_url = `${server_url}/[buffer]?method=list`

// Papers get keywords, GET
papers_get_keywords_url = `${server_url}/[papers]?method=keywords`

// Papers get descriptions, GET
papers_get_descriptions_url = `${server_url}/[papers]?method=descriptions`

// Buffer get [name], GET
function buffer_get_url(name) {
    return `${server_url}/[buffer]?method=get&name=${name}`
}

// Buffer parse [name], GET
function buffer_parse_url(name) {
    return `${server_url}/[buffer]?method=parse&name=${name}`
}

// Buffer commit new [name], POST
function buffer_commit_url(name) {
    return `${server_url}/[buffer]?method=commit&name=${name}`
}

// Papers get [title], GET
function papers_get_by_title_url(title) {
    return `${server_url}/[papers]?method=get&title=${title}`
}

// Init displays
init_displays()

function init_displays() {
    console.log('init_displays')
    d3.select("#current_title_checkbox")
        .on("change", function() {
            document.getElementById("current_title_container").hidden = !this.checked
        })
    d3.select("#current_keywords_checkbox")
        .on("change", function() {
            document.getElementById("current_keywords_container").hidden = !this.checked
        })
    d3.select("#current_descriptions_checkbox")
        .on("change", function() {
            document.getElementById("current_descriptions_container").hidden = !this.checked
        })

    d3.select("#current_title_logo")
        .on("click", function() {
            d = document.getElementById("current_title_checkbox")
            d.checked = !d.checked
        })
}

// Init buffer, keywords and descriptions
update_buffer_names()
update_keywords()
update_descriptions()

init_handlers()
clear_currents()

console.log("Buffer html onload success.")

// Update keywords
// GET keywords by [papers_get_keywords],
// add keywords as buttons in #keywords_buttons
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

// GET descriptions by [papers_get_descriptions],
// add descriptions as buttons in #description_buttons
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
                s = `.[${this.innerText}].`
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

// Squeeze [src] string
function squeeze(src) {
    // Delete leading "."s
    while (src.startsWith(".") | src.startsWith(",") | src.startsWith(" ") | src.startsWith("\ ")) {
        src = src.slice(1)
    }
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

    des = des.replace(/,,/g, ",")


    // Deal ends
    while (des.endsWith("\n")) {
        des = des.slice(0, -1)
    }
    while (des.endsWith(", ")) {
        des = des.slice(0, -2)
    }
    return des
}

// Clear current_title, _keywords and _description.
function clear_currents() {
    document.getElementById("current_title").value = ""
    document.getElementById("current_keywords").value = ""
    document.getElementById("current_descriptions").value = ""
    d3.selectAll(".SummaryLabel")
        .text("")
    console.log('Currents cleared.')
}

// Initialize handlers
// Add handle to commit button
// Auto regulize string in current_title, current_keywords, current_description when they are changed
function init_handlers() {
    // Commit button handler
    d3.select("#commit")
        .on("click", function() {
            commit_current()
        })

    d3.select("#current_title")
        // Handle onchange of #current_title
        .on("change", function() {
            title_onchange()
        })

    d3.select("#current_keywords")
        // Handle onchange of #current_keywords
        .on("change", function() {
            keywords_onchange()
        })

    d3.select('#current_descriptions')
        // Handle onchange of #current_description
        .on("change", function() {
            descriptions_onchange()
        })
}

// Update buffered names
// GET names by [buffer_list_url],
// add names as options in #buffer_names
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

// Handle [name] selection event of buffer name option.
// name: name selected.
// yield: update PDF and clear_currents
function name_selection(name) {
    console.log(`Select name: ${name}`)

    // Update PDF
    d3.select("#pdf_iframe")
        .attr("src", buffer_get_url(name))

    // clear_currents
    clear_currents()

    // Parse name
    d3.json(buffer_parse_url(name)).then(function(info) {
        console.log(info)
        document.getElementById("current_title").value = info.title
        d3.select("#_doi")
            .text(info.doi)
        title_onchange()
    })

    // Enable commit button if new name is selected
    document.getElementById("commit").disabled = false
}

// Commit currents contents
// POST Name, title, keywords and descriptions,
// using [buffer_commit_url]
function commit_current() {
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
    description = document.getElementById("current_descriptions").value

    // Sent POST request
    url = buffer_commit_url(name)
    console.log(url)
    $.post(url, {
            // kkkxxxx: kkk is prefix to note keyword, xxxx is the keyword
            kkkdate: (new Date()).valueOf(),
            kkktitle: title,
            kkkkeywords: keywords,
            kkkdescription: description
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

// Keywords onchange handler
function keywords_onchange() {
    // Keywords onchange event
    t = document.getElementById("current_keywords")
    v = t.value.replace(/\n/g, ",")
    v = squeeze(v)
    if (v.length > 0) {
        v += ","
    }
    s = v

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
    ss = ss.replace(/{ /g, "{")
    if (ss.endsWith("{")) {
        ss = ss.slice(0, -1)
    }
    d3.select("#_keywords")
        .text(ss)
}

// Title onchange handler
function title_onchange() {
    // Title onchange event
    t = document.getElementById("current_title")
    title = squeeze(t.value)
    t.value = title
    d3.select("#_title")
        .text(title)

    // Parse [s] using JSON
    // Return keys and dict
    // keys: keys of dict
    // dict: whole dict
    function get_keys(s) {
        try {
            dict = JSON.parse(s)
            keys = Object.keys(dict)
            return [keys, dict]
        } catch (error) {
            return [
                [],
                []
            ]
        }
    }

    // Try to request contents by title: [title]
    url = papers_get_by_title_url(title)
    d3.json(url).then(function(contents) {
        // Parse contents
        [keywords, k] = get_keys(contents['keywords']);
        [descriptions, d] = get_keys(contents['descriptions'])
        console.log("Keywords: " + keywords)
        console.log("Descriptions: " + descriptions)

        // Update keywords
        document.getElementById("current_keywords").value = ""
        for (var i = 0; i < keywords.length; i++) {
            document.getElementById("current_keywords").value += keywords[i] + ','
        }
        keywords_onchange()

        // Update descriptions
        document.getElementById("current_descriptions").value = ""
        for (var i = 0; i < descriptions.length; i++) {
            k = descriptions[i]
            document.getElementById("current_descriptions").value += '[' + k + '].\n'
            document.getElementById("current_descriptions").value += d[k] + '\n'
        }
        descriptions_onchange()
    })
}

// Descriptions onchange handler
function descriptions_onchange() {
    // Keywords onchange event
    t = document.getElementById("current_descriptions")
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
    d3.select("#_descriptions")
        .text(ss)
}