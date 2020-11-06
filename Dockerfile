FROM python:3.6.8
LABEL luxmundi backend
ENV PYTHONUNBUFFERED 1
# RUN mkdir /luxmundi
# RUN pwd
# RUN ls
WORKDIR /cic-backend
# RUN pwd
# RUN ls
COPY requirements.txt requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
COPY . .
EXPOSE 8000
CMD [ "python", "manage.py","runserver"]
