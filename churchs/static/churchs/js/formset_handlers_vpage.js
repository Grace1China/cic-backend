(function($) {
    $(document).on('formset:added', function(event, $row, formsetName) {
        console.log('-----------formset:added--------------')
        console.log(formsetName)
        console.log($row)
        $row[0].getElementsByClassName('field-church')[0].getElementsByTagName('select')[0].value = req_user_church
        $row[0].getElementsByClassName('field-create_by')[0].getElementsByTagName('select')[0].value = req_user

        // if (formsetName == 'churchs-media-content_type-object_id') {
        //     // Do something

        //     HTMLCollection.prototype.toArray=function(){
        //         return [].slice.call(this);
        //     };
        //     widget_fields = $row[0].getElementsByClassName('widget_field')
        //     widget_fields.toArray().forEach(function(item){
        //         selectfiles = item.getElementsByClassName('selectfiles')[0] 
        //         container = item.getElementsByClassName('container')[0]
        //         ossfile = item.getElementsByClassName('ossfile')[0] 
        //         postfiles = item.getElementsByClassName('postfiles')[0] 
    
        //         pconsole = item.getElementsByClassName('console')[0] 
        //         myradio = item.getElementsByClassName('myradio')[0] 
        //         fileurl = item.getElementsByClassName('fileurl')[0] 
        //         selectfiles = item.getElementsByClassName('selectfiles')[0] 
        //         acl = item.getElementsByClassName('x-oss-object-acl')[0]

        //         var upfact = UploaderFactory(selectfiles,container,ossfile,postfiles,pconsole,myradio,fileurl,acl);
        //         console.log('-----------formset:added--------------')
        //         upfact().init()
    
        //     })
        // }

        // media_select_ctrl = $row[0].getElementsByClassName('media_select')
        // media_select_ctrl[0].getElementsByTagName('input')[0].value='__empty__'
        
        // for(i = 0 ; i < media_select_ctrl.length ; i++){
        //     media_select_ctrl[i].getElementsByTagName('input')[0].value='__empty__'
        //     //为了能作一次服务器保存。在保存的时候在form里进行处理
        // }
        // formVue.formSubmit('_continue',"{% trans 'Save and continue editing' %}",null)

    });

    $(document).on('formset:removed', function(event, $row, formsetName) {
        // Row removed
    });
})(django.jQuery);