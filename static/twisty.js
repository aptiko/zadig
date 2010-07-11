function toggleMenu(dtElement) {
    var ddElement = dtElement.parentNode.getElementsByTagName("dd")[0];
    if(ddElement.style.visibility != 'visible')
        ddElement.style.visibility = 'visible';
    else
        ddElement.style.visibility = 'hidden';
    return false;
}

function showShowables(element) {
    var elementsToShow = getElementsByClassName("showable", "", element);
    for (var i=0; i<elementsToShow.length; i++) {
        elementsToShow[i].style.visibility = 'visible';
    }
}

function hideShowables(element) {
    var elementsToShow = getElementsByClassName("showable", "", element);
    for (var i=0; i<elementsToShow.length; i++) {
        elementsToShow[i].style.visibility = 'hidden';
    }
}
