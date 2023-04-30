FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./scraper /code/scraper

CMD ["playwright", "install"]

CMD ["uvicorn", "scraper.main:app", "--host", "0.0.0.0", "--port", "80"]

# docker run -it -p 80:80 -v /tmp /tmp {image-name}