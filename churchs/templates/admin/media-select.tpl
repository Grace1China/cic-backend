{% load cust_filters %}
<div> {{ label }} </div>
<media-sele 
    ref="{{ name }}" 
    name="{{ name }}" 
    value="{{ value }}"  
    :ptyp="'{{ typ }}'" 
    :ro="ro" 
    @click="popupCenter('/media_browse/?type={{ typ }}&from={{ name }}','媒体库',900,600)"  
    @clickp="preview" @clickd="deletep" >
</media-sele>
