FROM python
 
WORKDIR /code
#  もしかしたら、./requirements.txtはなくて、requirements.txtだけでいいかもしれない。
COPY ./requirements.txt /code/requirements.txt
 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
 
COPY ./app /code/app
 
CMD ["uvicorn", "app.main:app","--reload", "--host", "0.0.0.0", "--port", "8000"]