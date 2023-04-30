FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./scraper /code/scraper

CMD ["playwright", "install"]

CMD ["python3", "/code/scraper/main.py"]



# install docker
# https://docs.docker.com/engine/install/ubuntu/

# clone source

# docker build -t scraper .
# docker run -it -p 80:80 -v /tmp:/tmp scraper