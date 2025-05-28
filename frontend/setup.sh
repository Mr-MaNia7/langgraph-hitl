#!/bin/bash

# Install dependencies
pnpm install

# Create necessary directories
mkdir -p src/components/ui
mkdir -p src/lib

# Initialize PostCSS
echo 'module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}' > postcss.config.js

echo "Setup complete! You can now run 'pnpm dev' to start the development server." 