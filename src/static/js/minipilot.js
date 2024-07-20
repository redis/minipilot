function scroll(){
    $("html, body").animate({ scrollTop: $(document).height() }, 2000);
    return false;
}

$(document).ready(function() {
    $('input:first').focus();
});