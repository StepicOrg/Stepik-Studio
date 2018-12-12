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

        $.ajax({
            beforeSend: getCookie,
            type: "POST",
            url: window.location.pathname + urlink,
            data: {'item_id': itemId},
            success: function (data) {
                elem.after(data);
            },
        });
    });
});