
FROM acidjunk/web2py
COPY gestionale /home/www-data/web2py/applications/gestionale
RUN  chown -R www-data /home/www-data/web2py/applications/ && \
     pip install PyYAML openpyxl==2.5.14 && \
     locale-gen it_IT && \
     locale-gen it_IT.UTF-8 && \
     update-locale



