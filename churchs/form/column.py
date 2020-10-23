from churchs.models.columnContent import ContentColumn
from django import forms

import logging
from churchs.widget import MediaBaseWidget
loger = logging.getLogger('church.all')

from django.db.models import Q

import pickle
class ColChangeListForm(forms.ModelForm):
    parentCol = forms.ModelChoiceField(
         queryset=ContentColumn.objects.none(), required=False)
    cover = forms.CharField(label="", widget=MediaBaseWidget(
        label='封面', typ='images'), required=False)
    
    class Meta:
        model = ContentColumn
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # loger.info(kwargs)
        super(ColChangeListForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['parentCol'].queryset = ContentColumn.objects.filter(church=self.instance.church).filter(~Q(id=self.instance.id))
            
        # self.fields['parentCol'].empty_values = list((None, '', [], (), {},0))

  


class ContentColumnForm(forms.ModelForm):

    cover = forms.CharField(label="", widget=MediaBaseWidget(label='封面', typ='images'), required=False)
    parentCol = forms.ModelChoiceField(label='父专栏', queryset=ContentColumn.objects.none(), required=False)

    # parentCol = forms.ModelChoiceField()
    class Meta:
        model = ContentColumn
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ContentColumnForm, self).__init__(*args, **kwargs)
    def __init__(self, *args, **kwargs):
        super(ContentColumnForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['parentCol'].queryset = ContentColumn.objects.filter(church=self.instance.church).filter(~Q(id=self.instance.id))
        elif kwargs['initial']:
            self.fields['parentCol'].queryset = ContentColumn.objects.filter(church=kwargs['initial']['church'].id)

# 
# def create_model_form(request,admin_class):
#     '''动态生成Model Form'''
# 
#     # 修改样式
#     def __new__(cls, *args, **kwargs):
#         #print(cls.base_fields)     OrderedDict([('name', <django.forms.fields.CharField object at 0x000001385625DA90>)]),
#         for field_name,field_obj in cls.base_fields.items():
#             # 根据 cls.base_field 的特性给每个字段加上样式
#             cls.base_fields[field_name].widget.attrs['class'] = 'form-control'
# 
#         return forms.ModelForm.__new__(cls)
# 
#     class Meta:
#         model = admin_class.model        # 通过admin_class动态获取model
#         # fields = ('name', 'qq')        # 可以获取指定字段
#         # age = forms.IntegerField()     # 还可以添加字段
#         parentCol = forms.ModelChoiceField(
#             queryset=ContentColumn.objects.all(), required=False)
#         fields = '__all__'               # '__all__'获取所有字段
# 
#     attrs = {'Meta':Meta}
# 
#     _model_form_class = type("DynamicModelForm", (forms.ModelForm,), attrs)     # 第一个参数是类名，第二个参数是元组，填写父类，最后必须添加逗号，
#                                                                                 #  第三个参数字典形式的Meta类
#     # 方法一定要 setattr  
#     setattr(_model_form_class,'__new__',__new__)
#     return _model_form_class    # 返回的是一个类