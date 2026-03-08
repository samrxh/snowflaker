# 1. Use an official Node.js image as the base
FROM node:18-alpine

# 2. Set the "working directory" inside the container
WORKDIR /app

# 3. Copy the 'package.json' file and install dependencies
COPY package.json .
RUN npm install

# 4. Copy the rest of your code into the container
COPY . .

# 5. Start the app
CMD ["npm", "start"]