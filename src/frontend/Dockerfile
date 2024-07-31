FROM node:lts-alpine

ADD . /app
WORKDIR /app
RUN npm install
RUN npx vite build .
