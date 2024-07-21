function scroll(){
    $("html, body").animate({ scrollTop: $(document).height() }, 2000);
    return false;
}

$(document).ready(function() {
    $('input:first').focus();
});

$.notify.addStyle('minipilot', {
    html: "<div><span data-notify-text/></div>",
    classes: {
        base: {
            "white-space": "nowrap",
            "background-color": "rgb(220 255 30)",
            "border": "1px solid",
            "border-color": "rgb(9 26 35)",
            "padding": "8px"
        },
        superblue: {
            "color": "white",
            "background-color": "blue"
        }
    }
});