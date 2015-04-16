(function($){
    $(function() {
        $('a.grp-add-handler').click(function() {
            console.log($(window).trigger('load'))
        })
    });
})(django.jQuery);
