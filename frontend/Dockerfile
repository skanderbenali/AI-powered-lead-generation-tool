FROM node:18-alpine

WORKDIR /app

# Copy package files and install dependencies first (for better caching)
COPY package.json package-lock.json* ./
RUN npm config set fetch-retry-maxtimeout 120000 \
    && npm config set fetch-timeout 120000 \
    && npm install

# Copy application code
COPY . .

# Set environment for production mode
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Build the production application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application in production mode
CMD ["npm", "start"]
