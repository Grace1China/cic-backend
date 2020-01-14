(function($) {
    $(document).on('formset:added', function(event, $row, formsetName) {
        console.log('-----------formset:added--------------')
        console.log(formsetName)

        if (formsetName == 'churchs-media-content_type-object_id') {
            // Do something

            HTMLCollection.prototype.toArray=function(){
                return [].slice.call(this);
            };
            widget_fields = $row[0].getElementsByClassName('widget_field')
            widget_fields.toArray().forEach(function(item){
                selectfiles = item.getElementsByClassName('selectfiles')[0] 
                container = item.getElementsByClassName('container')[0]
                ossfile = item.getElementsByClassName('ossfile')[0] 
                postfiles = item.getElementsByClassName('postfiles')[0] 
    
                pconsole = item.getElementsByClassName('console')[0] 
                myradio = item.getElementsByClassName('myradio')[0] 
                fileurl = item.getElementsByClassName('fileurl')[0] 
                selectfiles = item.getElementsByClassName('selectfiles')[0] 
                var upfact = UploaderFactory(selectfiles,container,ossfile,postfiles,pconsole,myradio,fileurl);
                console.log('-----------formset:added--------------')
                upfact().init()
    
            })
        }
    });

    $(document).on('formset:removed', function(event, $row, formsetName) {
        // Row removed
    });
})(django.jQuery);