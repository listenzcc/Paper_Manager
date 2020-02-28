// Useful tools

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

// Method for regularize [src] string
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