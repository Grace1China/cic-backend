(function($) {
    $(document).on('formset:added', function(event, $row, formsetName) {
        console.log('-----------formset:added--------------')
        console.log(formsetName)
        console.log($row)

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
                acl = item.getElementsByClassName('x-oss-object-acl')[0]

                var upfact = UploaderFactory(selectfiles,container,ossfile,postfiles,pconsole,myradio,fileurl,acl);
                console.log('-----------formset:added--------------')
                upfact().init()
    
            })
        }

        media_select_ctrl = $row[0].getElementsByClassName('media_select')
        if (media_select_ctrl.length <=0){
            media_select_ctrl = $row[0].getElementsByTagName('media-sele')
        }
        // 
        for(i = 0 ; i < media_select_ctrl.length ; i++){
            // media_select_ctrls[i].addEventListener("click", function(){formVue.popupCenter('/media_browse/?type=images&from=admin','媒体库',900,600)}, false);

            new mediaSele().$mount(media_select_ctrl[i])
            
            ctrl2 = $row[0].getElementsByClassName('media_select')
            new mediaSele().$mount(ctrl2[0])
            ctrl2[0].addEventListener("click", function(){formVue.popupCenter('/media_browse/?type=images&from=admin','媒体库',900,600)}, false);

            // hovercard = media_select_ctrls[i].getElementsByClassName('.extra-bar.hovercard')
            // hovercard.addEventListener("click", function(){formVue.popupCenter('/media_browse/?type=images&from=admin','媒体库',900,600)}, false);
        }
    });

    $(document).on('formset:removed', function(event, $row, formsetName) {
        // Row removed
    });
})(django.jQuery);