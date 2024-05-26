var converter = new showdown.Converter();

function bubbles(endpoint, history, callback=undefined){
    var obj = jQuery.parseJSON(JSON.stringify(history));
    $.each(obj, function(key,value) {
        if (value.type == "HumanMessage")
            $( "#conversation" ).append('<div class="box bubble-right">' + value.content + '</box>');
        if (value.type == "AIMessage")
            $( "#conversation" ).append('<div class="box bubble-left">' + converter.makeHtml(value.content) + '</box>');
    });
    scroll();

    $("#chat").click(function(e){
        e.preventDefault();
        q = $("input").val()
        if (callback != undefined){callback();}
        $( "#conversation" ).append('<div class="box bubble-right">' + q + '</box>');
        bubble = $("<div>", {'class': "box bubble-left"}).appendTo("#conversation");
        dot = $("<div>", {'class': "dot-flashing"});
        dot.appendTo(bubble);
        scroll();
        var lastResponseLength = false;
        $.ajax({
            type: "POST",
            dataType: "text",
            url: endpoint,
            data : {q: encodeURIComponent(q)},
            processData: true,
            xhrFields: {
                // Getting on progress streaming response
                onprogress: function(e)
                {
                    var progressResponse;
                    var response = e.currentTarget.response;
                    if(lastResponseLength === false)
                    {
                        progressResponse = response;
                        lastResponseLength = response.length;
                    }
                    else
                    {
                        progressResponse = response.substring(lastResponseLength);
                        lastResponseLength = response.length;
                    }
                    bubble.html(converter.makeHtml(response));
                    $(document).scrollTop($(document).height());
                }
            },
            success: function(data) {
                $(document).ready(function(){$('a').attr('target', '_blank');});
            }
        });
        return false;
    });
}