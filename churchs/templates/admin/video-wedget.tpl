{% load cust_filters %}

<el-card :body-style="{ padding: '0px' }" class="widget_container {{ class }}">
    <el-tag type="info">{{ label }}</el-tag>
    {% if signed_url %}
        <video src="{{ signed_url }}"  x5-playsinline="" playsinline="" webkit-playsinline="" controls="controls" ></video>
        {% if public %}
            <el-button type="default" @click="openMsg('{{ public_url }}')">获取公共链接<br>get public link</el-button>
        {% endif %}
    {% else %}
        <el-card 
            type="info"
            v-loading="true"
            element-loading-text="转码中..."
            element-loading-spinner="el-icon-loading"
            element-loading-background="rgba(0, 0, 0, 0.8)"
        ></el-card>
        <el-button type="default" @click="openMsg('还没有链接(after transcode)')">获取公共链接<br>get public link</el-button>
    {% endif %}

</el-card>
