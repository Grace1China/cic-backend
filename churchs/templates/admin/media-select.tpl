{% load cust_filters %}
{% comment %} <media-base-selctl ref="{{ name }}" name="{{ name }}" value="{{ value }}" :src="{{ src }}" :ro="ro" @click="popupCenter('/media_browse/?type=images&from=admin','媒体库',900,600)"  @clickp="preview" @clickd="ro=undefined"/> {% endcomment %}
{% comment %} <button-counter></button-counter> {% endcomment %}
{% comment %} <el-button onclick="alert('')"></el-button> {% endcomment %}
<media-sele ref="{{ name }}" name="{{ name }}" value="{{ value }}"  :ro="ro" @click="popupCenter('/media_browse/?type=images&from=admin','媒体库',900,600)"  @clickp="preview" @clickd="ro=undefined"></media-sele>

{% comment %} :src="{{ src }}" {% endcomment %}