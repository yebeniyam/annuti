# Bendine Frontend

This is the frontend for the Bendine Food and Beverage Management System, built with React and TypeScript.

## Getting Started

### Prerequisites

- Node.js (v16+)
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

2. Create a `.env` file in the root directory and add your environment variables:
   ```
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_SUPABASE_URL=your_supabase_url
   REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

3. Start the development server:
   ```bash
   npm start
   # or
   yarn start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Available Scripts

- `npm start` - Start the development server
- `npm test` - Run tests
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Project Structure

```
src/
├── assets/          # Static assets (images, fonts, etc.)
├── components/      # Reusable UI components
├── pages/           # Page components
├── services/        # API services
├── store/           # Redux store configuration
├── styles/          # Global styles and themes
└── utils/           # Utility functions and helpers
```

## Tech Stack

- React 18
- TypeScript
- Redux Toolkit
- Material-UI
- React Router
- Axios
- Formik & Yup
- ESLint & Prettier
