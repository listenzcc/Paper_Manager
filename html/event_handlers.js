// DOM event handlers
console.log('event handlers starts.')

// CommitButton onclick handler
// POST Name, title, keywords and descriptions to buffer_commit_url
function commit_currents() {
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
    $.post(url,
        // POST
        {
            // kkkxxxx: kkk is prefix to note keyword, xxxx is the keyword
            kkkdate: (new Date()).valueOf(),
            kkktitle: title,
            kkkkeywords: keywords,
            kkkdescription: description
        },
        // Handle response
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

// Name onclick handler
// GET name from buffer_get_url
// GET contents from buffer_parse_url
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

console.log('event handlers success.')