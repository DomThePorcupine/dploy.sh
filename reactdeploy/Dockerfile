# We need a very very basic
# container, so use slim
FROM node:9.4.0-slim

# Make a directory for our
# source
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy over our important
# files
COPY server/package.json .
COPY server/package-lock.json .
COPY server/app.js .
COPY build ./pub

# Install our dependencies
RUN npm install

# Open up our port
EXPOSE 7075

# Start our app
CMD [ "npm", "start"]