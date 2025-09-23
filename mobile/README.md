# Bendine Mobile App

Mobile application for waitstaff to manage orders and tables, built with React Native.

## Prerequisites

- Node.js (v16+)
- npm or yarn
- React Native CLI
- Xcode (for iOS development)
- Android Studio (for Android development)

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

2. Set up environment variables:
   - Create a `.env` file in the root directory
   - Copy the contents from `.env.example` and update with your configuration

3. Start the development server:
   ```bash
   # For iOS
   npx react-native run-ios
   
   # For Android
   npx react-native run-android
   ```

## Project Structure

```
src/
├── assets/          # Images, fonts, and other static files
├── components/      # Reusable UI components
├── navigation/      # Navigation configuration
├── screens/         # App screens
├── services/        # API and business logic
└── utils/           # Helper functions and constants
```

## Tech Stack

- React Native
- TypeScript
- React Navigation
- Redux Toolkit
- React Native Paper
- Axios
- React Native Vector Icons
