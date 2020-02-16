{% load cust_filters %}

{% if signed_url %}
<el-card :body-style="{ padding: '0px' }" class="widget_container">
    <el-tag type="info">{{ label }}</el-tag>
    <video src="{{ signed_url }}"  x5-playsinline="" playsinline="" webkit-playsinline="" controls="controls" ></video>
    {% if public %}
        <el-button type="default" @click="openMsg('{{ public_url }}')">获取公共链接<br>get public link</el-button>
    {% endif %}
</el-card>
{% endif %}
