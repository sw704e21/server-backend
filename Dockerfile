FROM python:3
RUN apt-get update
COPY ./src ./src
COPY ./requirements.txt ./requirements.txt
COPY ./setup.py ./setup.py
RUN pip install -r /requirements.txt
RUN mkdir /logs
EXPOSE 65432
RUN python3 setup.py
ENTRYPOINT ["python3"]
CMD ["/src/main.py"]