FROM alpine:latest
RUN apk add --no-cache curl
RUN apk add --no-cache --upgrade bash
COPY ./init_script /init
RUN chmod +x /init/init.sh
CMD ["/init/init.sh"]
