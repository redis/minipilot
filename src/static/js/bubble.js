var converter = new showdown.Converter();

function bubbles(endpoint, history, callback=undefined){
    var obj = jQuery.parseJSON(JSON.stringify(history));
    $.each(obj, function(key,value) {
        if (value.type == "HumanMessage")
            $( "#conversation" ).append('<div class="bubble bubble-right">' + value.content + '</div>');
        if (value.type == "AIMessage")
            $( "#conversation" ).append('<div class="bubble bubble-left">' + converter.makeHtml(value.content) + '</div>');
    });
    scroll();
    $('.bubble-left a').attr('target', '_blank');

    $("#chat").click(function(e){
        e.preventDefault();
        ttft = 0;
        now = Date.now();
        q = $("input").val()
        if (callback != undefined){callback();}
        $( "#conversation" ).append('<div class="bubble bubble-right">' + q + '</div>');
        bubble = $("<div>", {'class': "bubble bubble-left"}).appendTo("#conversation");
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
                    if (!ttft) {ttft = Date.now() - now;}
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
                bubble.find('a').attr('target', '_blank');
                etfl = Date.now() - now;
                bubble.attr('data-etfl', etfl);
                bubble.attr('data-ttft', ttft);
                bubble.append($('<hr class="my-3 has-background-light">'));
                bubble.append(`<p class="is-size-6 has-text-grey-dark">Time to first token is ${ttft}ms. Elapsed time first to last token is ${etfl}ms</p>`);
                $(document).scrollTop($(document).height());
            }
        });
        return false;
    });
}