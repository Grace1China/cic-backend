from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'
    label = 'api'


    # def ready(self):
        # import  api.signals
    

    verbose_name = "前端程序接口"
    verbose_name_plural = "前端程序接口"