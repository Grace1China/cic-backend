{% load cust_filters %}
{% comment %} <div> {{ label }} </div> {% endcomment %}
<div >
    <input type="hidden" name="{{ name }}" value="{{ value }}" maxlength="250" required="required" id="id_title" class="vTextField">
    <img style="width: auto;height: 100px;" src="{{ value }}"/>
</div>
