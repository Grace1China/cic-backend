{% load cust_filters %}
<input class="inlineContentValue" type="hidden" ref="{{ name }}" name="{{ name }}" value="{{ value }}" />
<div class="inlineContent" contenteditable="true" style="height: 100px;width: 540px;"> {{ value|safe }} </div>
