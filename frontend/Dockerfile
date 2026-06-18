# Frontend image: a MULTI-STAGE build.
#   Stage 1 (node)  -> compile the React app into static files.
#   Stage 2 (nginx) -> serve those files + proxy /api to the backend.
# Only stage 2 ends up in the final image, so it stays tiny (no Node/node_modules).

# ---- Stage 1: build ----
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build          # outputs static files to /app/dist

# ---- Stage 2: serve ----
FROM nginx:alpine
# Our nginx config (SPA routing + /api proxy to the backend container).
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copy just the built assets from stage 1.
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
