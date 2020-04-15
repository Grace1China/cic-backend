{% load cust_filters %}

{% if value %}
<p class="file-upload">目前: <a href="{{ value }}">{{ name }}/a> 
<span class="clearable-file-input">
<input type="checkbox" name="{{ field }}-clear" id="{{field}}-clear_id"> 
<label for="{{ field }}-clear_id">清除</label>
</span>
<br>
修改:
{% endif %}
<el-button type="success" plain @click='popupCenter("media_browse","查找媒体",900,600)'>选择文件</el-button>
   
