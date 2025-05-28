# Confirmation Agent Frontend

This is the frontend application for the Confirmation Agent, built with React, TypeScript, and Chakra UI.

## Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)

## Setup

1. Install dependencies:

```bash
pnpm install
```

2. Start the development server:

```bash
pnpm dev
```

The application will be available at `http://localhost:5173`.

## Features

- Modern, responsive UI built with Chakra UI
- Real-time chat interface with the Confirmation Agent
- Support for confirmation flows and clarifications
- TypeScript for better type safety
- Vite for fast development and building

## Development

The frontend communicates with the FastAPI backend running on `http://localhost:8000`. Make sure the backend is running before starting the frontend application.

## Building for Production

To build the application for production:

```bash
pnpm run build
```

The built files will be in the `dist` directory.
