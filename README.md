docker build -t mcc .
docker run  -p 8443:443 -p 8880:80 mcc
