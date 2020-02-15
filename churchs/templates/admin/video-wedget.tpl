{% load cust_filters %}
<el-card :body-style="{ padding: '0px' }" class="widget_container">
{% if signed_url %}
    <el-tag type="info">{{ label }}</el-tag>
    <video src="{{ signed_url }}"  x5-playsinline="" playsinline="" webkit-playsinline="" controls="controls" ></video>
    <el-button type="primary">获取公共链接<br>get public link</el-button>
{% endif %}
</el-card>