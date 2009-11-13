function toggleMenu(dtElement) {
    var ddElement = dtElement.parentNode.getElementsByTagName("dd")[0];
    if(ddElement.style.visibility != 'visible')
        ddElement.style.visibility = 'visible';
    else
        ddElement.style.visibility = 'hidden';
    return false;
}
