FROM python:3.6-alpine

# make sure the package repository is up to date
RUN apk update \
 && apk upgrade \
 && apk add bash \
 && rm -rf /var/cache/*/* \
 && echo "" > /root/.ash_history

# change default shell from ash to bash
RUN sed -i -e "s/bin\/ash/bin\/bash/" /etc/passwd

ENV LC_ALL=en_US.UTF-8

RUN adduser -D bvb

WORKDIR /home/bvb

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app app
COPY migrations migrations
COPY bvb02.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP bvb02.py

#RUN chown -R dev01:dev01 ./
USER bvb

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
