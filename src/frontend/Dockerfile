FROM node:lts-alpine

ADD . /app

WORKDIR /app

COPY package*.json ./

RUN npm install

CMD ["npm", "run", "dev"]