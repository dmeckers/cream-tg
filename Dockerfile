FROM node:14-alpine AS build

LABEL MAINTAINER="dmeckers"

WORKDIR /app

RUN apk update && apk upgrade

COPY package*.json ./

RUN npm install && apk add --no-cache ffmpeg

COPY . .

RUN addgroup -S workers && adduser -S worker -G workers

RUN chown -R worker:workers /app

RUN npm i -g typescript

USER worker

EXPOSE 8000
EXPOSE 1935

RUN cd /app && tsc

ENTRYPOINT ["node", "/app/dist/tg-bot.js"]
