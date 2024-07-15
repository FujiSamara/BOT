# Build stage
FROM node:lts-alpine as build-stage

ADD . /app
WORKDIR /app
RUN npm install
RUN npx vite build .

# Production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
