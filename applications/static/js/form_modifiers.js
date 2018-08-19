function make_field_typeahead(field_id, path_to_json) {
    $.ajax({
        type: "GET",
        url: path_to_json,
        dataType: "json"
    }).done(function (res) {
        $("#id_" + field_id).typeahead({source: res});
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.error("AJAX call failed: " + textStatus + ", " + errorThrown);
    });
}


function conditional_field(field_to_hide, field_to_track, f_eval_to_show, parent_num = 1) {
    var parent = field_to_hide;
    for(var i=0; i < parent_num; i++){
	    parent = parent.parent();
    }
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
