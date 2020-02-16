{% load cust_filters %}
<div class="widget_field">
    <div class="ossfile"></div>
    <div class='preview'></div>
    <input type="hidden" value="{{ public }}" name="nouse"/>

    <div class="container" style="text-align: center;">
        <el-button type="default"  class="selectfiles"  plain>上传{{ vbn  }}(Upload)<i class="el-icon-upload el-icon--right"></i></el-button>
        {% if public %}
            <el-button type="default" @click="openMsg('{{ public_url }}')">公共链接<br>public link</el-button>

        {% elif signed_url %}
            <el-button type="default" @click="openMsg('{{ signed_url }}')">1天链接<br>1 day link</el-button>
        {% endif %}
        
        <input class="file-url fileurl" name="{{ name }}" type="hidden" value="{{ file_url }}" />
        <input class='x-oss-object-acl' type='hidden' value = '{{ acl }}'/>
    </div>
    <pre class="console"></pre>
</div>
<script>
console.log('widget.tpl')
if (`{{ name  }}`.indexOf('__prefix__') < 0){
	$(document).ready(function(){

			HTMLCollection.prototype.toArray=function(){
                return [].slice.call(this);
            };
			inline_div = document.getElementById('{{ name }}'.replace('-{{ fieldname }}',''))  //-alioss_video

			item= inline_div.querySelector('.field-{{ fieldname }} .widget_field')
            //widget_fields = field_div.getElementsByClassName('widget_field')
            //widget_fields.toArray().forEach(function(item){

                preview = item.getElementsByClassName('preview')[0] 
                if('{{ fieldname }}'.indexOf('video')>0){
                    preview.innerHTML='<video src={{ signed_url }} controls>'
                    
                } if ('{{ fieldname }}'.indexOf('image')>0){
                    preview.innerHTML='<img src={{ signed_url }}>'
                }

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
    
            //})
			//现在有一个外层的id 唯一标识了  inline record
			//我所要做的是要把当前widget的内容找出来。1 首先要找到 inline-record.   2 再就是要找到某一个字段 3就找到不同的内置的控件
	});
}

</script>
