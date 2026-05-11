# Stage 1 : build (sera utilise par MT dans DR-11)
FROM node:20-alpine AS builder

WORKDIR /app

# Build placeholder pour Sprint 1 - sera complete par MT
RUN mkdir -p /app/dist && echo "<html><body><h1>Restaurant Reservation App</h1><p>Frontend placeholder - waiting for DR-11</p></body></html>" > /app/dist/index.html

# Stage 2 : serve avec nginx
FROM nginx:alpine

# Copier la page placeholder depuis le builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copier la config nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
