# Use Node.js image to build the React app
FROM node:18-alpine as build
WORKDIR /app

# Install dependencies
COPY package.json .
COPY vite.config.js .
COPY src ./src
COPY public ./public
RUN npm install

# Build the production version
RUN npm run build

# Use Nginx to serve the static site
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]