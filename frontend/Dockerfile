# Stage 1: Build React Application
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies first (to leverage docker cache)
COPY package*.json ./
RUN npm install

# Copy source files
COPY . .

# Build application
ENV VITE_API_URL=http://localhost:8000
RUN npm run build

# Stage 2: Serve production assets with Nginx
FROM nginx:alpine

# Copy compiled assets from Stage 1
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration to support SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
