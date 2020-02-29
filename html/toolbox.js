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

// Method for regularize [src] string
function squeeze(src) {
    // Change each "\n" into space.
    des = src.replace(/\n/g, " ")

    // Remove leading spaces
    while (des.startsWith(" ")) {
        des = des.slice(1)
    }

    // Squeeze double-spaces
    // while (des.includes("  ")) {
    //     des = des.replace(/  /g, " ")
    // }
    des = des.replace(/\s{1,}/g, " ")

    // Delete space around each ",", ":" and ".".
    des = des.replace(/\s{0,},\s{0,}/g, ",")
    des = des.replace(/\s{0,}\.\s{0,}/g, ".")
    des = des.replace(/\s{0,}:\s{0,}/g, ":")

    // Stack i.e.
    des = des.replace(/i\.e\./g, "---ie---")
    des = des.replace(/et al\./g, "---etal---")
    des = des.replace(/e\.g\./g, "---eg---")

    // Add space after "," and ":"
    des = des.replace(/,/g, ", ").replace(/:/g, ": ")

    // Add "\n" after "."
    des = des.replace(/\./g, "\.\n")

    // Resume i.e.
    des = des.replace(/---ie---/g, "i.e. ")
    des = des.replace(/---etal---/g, "et al. ")
    des = des.replace(/---eg---/g, "e.g. ")

    return des
}

function format_title(src) {
    des = ""
    isUp = true
    for (var i = 0; i < src.length; i++) {
        if (isUp) {
            des += src[i].toUpperCase()
            isUp = false
        } else {
            des += src[i]
        }
        if (src[i] == " ") {
            isUp = true
        }
    }
    return des
}

console.log('toolbox invite success.')