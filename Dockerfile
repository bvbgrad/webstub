FROM python:3.7-alpine
RUN apk update && apk upgrade && apk add bash
  
RUN adduser -D bvb02
WORKDIR home/bvb02
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY bvb02.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP bvb02.py

RUN chown -R bvb02:bvb02 ./
USER bvb02
 
EXPOSE 5000
CMD ["./boot.sh"]
