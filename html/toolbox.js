// Useful tools
console.log('toolbox invite starts.')

// Profiles
server_url = "http://localhost:8612"

// Buffer list names, GET
buffer_list_url = `${server_url}/[buffer]?method=list`

// Papers get keywords, GET
papers_get_keywords_url = `${server_url}/[papers]?method=keywords`

// Papers get descriptions, GET
papers_get_descriptions_url = `${server_url}/[papers]?method=descriptions`

// Edit currents, POST
edit_currents_url = `${server_url}/[worker]?method=edit`

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

// todo: Add squeeze method for regularize paper title
// Add trim method for String class
// if (typeof(String.prototype.trim) === "undefined") {
String.prototype.trim = function() {
    return String(this).replace(/^\s+|\s+$/g, '');
};

// Add toTitleCase method for String class
String.prototype.toTitleCase = function() {
    s = String(this).trim().toLowerCase()
    d = ""
    up = true
    for (var i = 0; i < s.length; i++) {
        if (up) {
            d += s[i].toUpperCase()
            up = false
        } else {
            d += s[i]
        }
        if (s[i] == " ") {
            up = true
        }
    }
    return d
};

// Method for regularize words splits,
// line up [src] and split words with commas
function words_split(src) {
    // Convert "\n"s into ","s
    src = src.replace(/\n/g, ",")

    // Convert "\s"s into spaces
    src = src.replace(/\s/g, " ")

    // Remove multiple-spaces
    src = src.replace(/\s{1,}/g, " ")

    // Split words
    words = src.split(",")

    des = ""
    for (var i = 0; i < words.length; i++) {
        des += words[i].toTitleCase()
        des += ", "
    }

    return des.slice(0, -2)

}

console.log('toolbox invite success.')