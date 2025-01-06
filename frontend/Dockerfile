FROM node:18

WORKDIR /usr/src/app

COPY out .

RUN npm install -g http-server

EXPOSE 80

CMD ["http-server", "-p", "80", "-c-1"]
