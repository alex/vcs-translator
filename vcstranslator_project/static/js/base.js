$(function() {
    var command_text = "command (e.g svn commit)...";
    if ($("#id_command").val() == command_text) {
        $("#id_command").css("color", "gray");
    }
    else {
        $("#id_command").css("color", "black");
    }
    $("#id_command").focus(function() {
        if ($(this).val() == command_text) {
            $(this).val("");
            $(this).css("color", "black");
        }
    }).blur(function() {
        if ($(this).val() == "") {
            $(this).val(command_text);
            $(this).css("color", "gray");
        }
    });
})
