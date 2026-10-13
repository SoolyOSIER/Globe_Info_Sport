FROM node:20-alpine AS redaction-build
WORKDIR /app
COPY globeinfosport-redaction/package*.json ./
RUN npm install
COPY globeinfosport-redaction/ ./
ENV VITE_BASE_PATH=/redaction/ VITE_API_URL=/api/v1 VITE_VITRINE_URL=/
RUN npm run build

FROM node:20-alpine AS vitrine-build
WORKDIR /app
COPY globeinfosport-vitrine/package*.json ./
RUN npm install
COPY globeinfosport-vitrine/ ./
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=redaction-build /app/dist /var/www/redaction
COPY --from=vitrine-build /app/dist /var/www/vitrine
