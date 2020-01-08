(function($) {
    $(document).on('formset:added', function(event, $row, formsetName) {
        console.log('-----------formset:added--------------')
        console.log(formsetName)
        if (formsetName == 'medias') {
            // Do something
            var upfact = UploaderFactory(
                `selectfiles-${ $row[0].id }-video_alioss`,`container-${ $row[0].id }-video_alioss`,`ossfile-${ $row[0].id }-video_alioss`,`postfiles-${ $row[0].id }-video_alioss`,`console-${ $row[0].id }-video_alioss`,`myradio-${ $row[0].id }-video_alioss`
                );
            console.log('-----------formset:added--------------')

        
            upfact().init()
        }
    });

    $(document).on('formset:removed', function(event, $row, formsetName) {
        // Row removed
    });
})(django.jQuery);