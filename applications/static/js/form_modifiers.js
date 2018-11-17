function make_field_typeahead(field_id, path_to_json, options) {
    $.ajax({
        type: "GET",
        url: path_to_json,
        dataType: "json"
    }).done(function (res) {
        var opt = {source: res};
        if (options) opt = Object.assign(opt, options);
        $("#id_" + field_id).typeahead(opt);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.error("AJAX call failed: " + textStatus + ", " + errorThrown);
    });
}


function conditional_field(field_to_hide, field_to_track, f_eval_to_show) {
    var parent = field_to_hide.parent('div');
    field_to_track.on('change', function () {
        if (f_eval_to_show()) {
            parent.fadeIn();
        } else {
            parent.fadeOut();
            field_to_hide.val('');
        }
    });
    if (!f_eval_to_show()) {
        parent.hide()
    }


}
