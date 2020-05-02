FROM myubuntu:v2
RUN pip install --upgrade pip

WORKDIR /app

COPY . /app
RUN pip install -r requirments.txt

EXPOSE 4000

ENTRYPOINT ['python']

CMD ['app.py']
