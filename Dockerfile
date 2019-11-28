FROM httpd:2.4.41
RUN apt-get update && apt-get install -y \
    libapache2-mod-wsgi  \
    python-pip \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install Flask

RUN a2dissite default
RUN a2dissite default-ssl
RUN a2enmod wsgi

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2

COPY src /var/www/src

#Creamos el virtual host
COPY resources/docker/app /etc/apache2/sites-available/appflask
RUN chown -R www-data:www-data /var/www/src
RUN chown www-data:www-data /etc/apache2/sites-available/appflask
RUN a2ensite appflask

EXPOSE 80
CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]
COPY ./html/ /usr/local/apache2/htdocs/
