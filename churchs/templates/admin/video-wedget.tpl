{% load cust_filters %}
<div class="widget_container">

<video src="{{ signed_url }}"  x5-playsinline="" playsinline="" webkit-playsinline="" controls="controls" ></video>
{% if public %}
{% endif %}
<div type="text" class="button">获取公共链接(get public link)</div>
</div>