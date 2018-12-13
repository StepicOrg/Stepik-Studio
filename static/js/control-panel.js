$(document).ready(function () {
    //appends/removes list of items
    $(document).on("click", ".item-button", function (e) {
        const elem = $(this);

        if (elem.next().hasClass("item-group")) {
            elem.next().remove(); //after() uses for appending
            return false;
        }

        const urlink = $(this).data("urllink");
        const itemId = $(this).data("item-id");
        const itemType = $(this).data("item-type");

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
                    elem.after(data);
                }
            },
        });
    });
});