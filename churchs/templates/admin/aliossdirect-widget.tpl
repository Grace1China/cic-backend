{% load cust_filters %}
{% comment %} <form name=theform> {% endcomment %}
{% comment %} <input type="radio" name="myradio" value="local_name" checked=true/> 上传文件名字保持本地文件名字 {% endcomment %}
{% comment %} <input type="radio" name="myradio" value="random_name" /> 上传文件名字是随机文件名, 后缀保留 {% endcomment %}
{% comment %} </form> {% endcomment %}
<div class="widget_field">

<div class="ossfile"></div>
<a href="{{ file_url }}" class='ossurl'>{{ file_url | tofilename }}</a>
<div class="container">
	<a class="selectfiles" href="javascript:void(0);" class='btn'>选择文件</a>
	<a class="postfiles" href="javascript:void(0);" class='btn'>开始上传</a>
	<input class="file-url fileurl" name="{{ name }}" type="hidden" value="{{ file_url }}" >
</div>

<pre class="console"></pre>
</div>


<script>
if (`{{ name  }}`.indexOf('__prefix__') < 0){
	{% comment %} console.log("{{ name | str2varname }}") {% endcomment %}
	$(document).ready(function(){

			HTMLCollection.prototype.toArray=function(){
                return [].slice.call(this);
            };
			inline_div = document.getElementById('{{ name }}'.replace('-{{ fieldname }}',''))  //-alioss_video
			field_div= inline_div.getElementsByClassName('field-{{ fieldname }}')
            widget_fields = field_div[0].getElementsByClassName('widget_field')
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
			//现在有一个外层的id 唯一标识了  inline record
			//但是在这个里面有不同的字段，都是用到了alioss
			//我所要做的是要把当前widget的内容找出来。1 首先要找到 inline-record.   2 再就是要找到某一个字段 3就找到不同的内置的控件
	});
}

</script>
