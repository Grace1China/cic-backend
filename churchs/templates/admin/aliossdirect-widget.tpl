{% load cust_filters %}
{% comment %} <form name=theform> {% endcomment %}
{% comment %} <input type="radio" name="myradio_{{ name | str2varname }}" value="local_name" checked=true/> 上传文件名字保持本地文件名字 {% endcomment %}
{% comment %} <input type="radio" name="myradio_{{ name | str2varname }}" value="random_name" /> 上传文件名字是随机文件名, 后缀保留 {% endcomment %}
{% comment %} </form> {% endcomment %}
<div id = "widget_{{ name | str2varname }}">

<div id="ossfile_{{ name | str2varname }}">你的浏览器不支持flash,Silverlight或者HTML5！</div>
<a href="{{ file_url }}" class='ossurl'>{{ file_url | tofilename }}</a>
<div id="container_{{ name | str2varname }}">
	<a id="selectfiles_{{ name | str2varname }}" href="javascript:void(0);" class='btn'>选择文件</a>
	<a id="postfiles_{{ name | str2varname }}" href="javascript:void(0);" class='btn'>开始上传</a>
	<input class="file-url"  id="fileurl_{{ name | str2varname }}" name="{{ name }}" type="hidden" value="{{ file_url }}" >

</div>

<pre id="console_{{ name | str2varname }}"></pre>
</div>


<script>
if (`{{ name | str2varname }}`.indexOf('__prefix__') < 0){
			console.log("{{ name | str2varname }}")

	$(document).ready(function(){
		var upfact_{{ name | str2varname }} = UploaderFactory(
		'selectfiles_{{ name | str2varname }}','container_{{ name | str2varname }}','ossfile_{{ name | str2varname }}','postfiles_{{ name | str2varname }}','console_{{ name | str2varname }}','myradio_{{ name | str2varname }}','fileurl_{{ name | str2varname }}','widget_{{ name | str2varname }}'
		);
	
		upfact_{{ name | str2varname }}().init()
	});
}

</script>
