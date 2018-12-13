$(document).ready(function () {
    //appends/removes list of items
    $(document).on("click", ".item-button", function (e) {
        const elem = $(this);

        if (elem.parent().next().hasClass("item-group")) {
            elem.parent().next().remove(); //after() uses for appending
            return false;
        }

        const urlink = $(this).data("urllink");
        const itemId = $(this).parent().data("item-id");
        const itemType = $(this).parent().data("item-type");

        $.ajax({
            beforeSend: getCookie,
            type: "POST",
            url: window.location.pathname + urlink,
            data: {
                'item_id': itemId,
                'requesting_item_type': itemType
            },
            success: function (data) {
                if (data) {
                    elem.parent().after(data);
                    $("[data-toggle=\"tooltip\"]").tooltip(); //enable tooltip on appended element
                }
            },
        });
    });

    //Export to PPro project
    $(document).on("click", ".export-prproj", function (e) {
        const itemId = $(this).parent().data("item-id");
        const itemType = $(this).parent().data("item-type");

        $.ajax({
            beforeSend: getCookie,
            type: "POST",
            url: window.location.pathname + "export/",
            data: {
                'item_id': itemId,
                'item_type': itemType
            }
        });
    });

    //Shows video content
    $(document).on("click", ".show-content", function () {
        const title = $(this).parent().find(".item-button").text();
        const url = $(this).data("urllink");

        $("#modalVideoTitle").text(title);
        $(".video-content").append("<video controls preload='none' width='100%'>" +
            "<source class='video' src=" + url + ">" +
            "</video>");
        $("#videoModalCenter").modal("show");
        $("video").get(0).play();
    });

    //Makes video content empty on modal hide
    $(document).on("hidden.bs.modal", "#videoModalCenter", function () {
        $("video").get(0).pause();
        $(".video-content").empty();
    });

    //Enable tooltips
    $("[data-toggle=\"tooltip\"]").tooltip()
});