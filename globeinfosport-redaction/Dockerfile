FROM node:20-alpine AS dependencies
WORKDIR /app
COPY package*.json ./
RUN npm install

FROM dependencies AS development
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

FROM dependencies AS build
COPY . .
RUN npm run build
