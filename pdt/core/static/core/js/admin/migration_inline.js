(function($) {
    "use strict";
    setTimeout(function() {
        $('.migration_step_type').change(function() {
            var Mode = require("ace/mode/" + $(this).val()).Mode;
            $(this).parents('.grp-module').find('.ace_editor')[0].env.editor.getSession().setMode(new Mode())
        })
    }, 10)
})(django.jQuery);
