# Stage 1: Dependencies & Builder
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package definitions
COPY package.json package-lock.json* ./

# Install dependencies using high-speed mirror and pre-install SWC binaries
RUN npm config set registry https://registry.npmmirror.com && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm install && \
    npm install --force --save-optional @next/swc-linux-x64-gnu@14.2.11 @next/swc-linux-x64-musl@14.2.11

# Copy source code
COPY . .

# Environment settings for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV BACKEND_URL=http://backend:8281

# Build Next.js
RUN npm run build

# Stage 2: Production Runner
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=8280
ENV BACKEND_URL=http://backend:8281

COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.mjs ./next.config.mjs

EXPOSE 8280

CMD ["npm", "start"]
