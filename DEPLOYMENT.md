# Bendine - Food and Beverage Management System

Bendine is a comprehensive restaurant management system that streamlines operations from menu management to point of sale, inventory, and reporting.

## Deployment Instructions

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the environment variables from `render.yaml`
5. Deploy the service

### Frontend (cPanel)

1. Build the React app for production:
   ```bash
   npm run build
   ```
2. Upload the contents of the `build` folder to your cPanel File Manager
3. Point your domain to the uploaded files
4. Make sure to set up proper environment variables for the API URL

### Mobile App

The mobile app can be built for iOS and Android using React Native CLI or Expo.

## Environment Variables

### Backend (.env)
```
DATABASE_URL=your_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Frontend (.env)
```
REACT_APP_API_URL=your_backend_api_url
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_KEY=your_supabase_key
```

## Tech Stack

- **Frontend**: React (Hosted on cPanel)
- **Backend**: Python FastAPI (Hosted on Render)
- **Database/Auth/Realtime/Storage**: Supabase
- **Mobile**: React Native (for Waiter App)

## Features

- **User & Role Management**
- **Menu Management** with COGS calculation
- **Inventory Management** with real-time tracking
- **Point of Sale (POS)** with table management
- **Vendor & Purchase Management**
- **Reporting & Analytics**
- **Mobile Waiter App** (React Native)
- **Admin Dashboard**

## API Documentation

Once deployed, API documentation is available at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc documentation

## Support

For support, contact the development team.