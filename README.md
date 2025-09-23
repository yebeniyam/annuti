# Bendine - Food and Beverage Management System

Bendine is a comprehensive restaurant management system that streamlines operations from menu management to point of sale, inventory, and reporting.

## Features

- **User & Role Management**
- **Menu Management** with COGS calculation
- **Inventory Management** with real-time tracking
- **Point of Sale (POS)** with table management
- **Vendor & Purchase Management**
- **Reporting & Analytics**
- **Mobile Waiter App** (React Native)
- **Admin Dashboard**

## Tech Stack

- **Frontend**: React (Hosted on cPanel)
- **Backend**: Python FastAPI (Hosted on Render)
- **Database/Auth/Realtime/Storage**: Supabase
- **Mobile**: React Native

## Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.9+)
- PostgreSQL (via Supabase)
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yebeniyam/annuti.git
   cd annuti
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

4. Set up environment variables:
   - Create `.env` files in both `backend` and `frontend` directories
   - Refer to `.env.example` in each directory for required variables

5. Start the development servers:
   - Backend: `uvicorn main:app --reload`
   - Frontend: `npm start`

## Project Structure

```
annuti/
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   ├── tests/            # Backend tests
│   ├── requirements.txt  # Python dependencies
│   └── main.py          # Entry point
│
├── frontend/             # React frontend
│   ├── public/          # Static files
│   ├── src/             # Source code
│   ├── package.json     # Frontend dependencies
│   └── ...
│
├── mobile/              # React Native mobile app
│   ├── android/        # Android specific code
│   ├── ios/            # iOS specific code
│   ├── src/            # Shared app code
│   └── ...
│
├── docs/               # Documentation
├── .github/           # GitHub workflows
├── .gitignore
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter)

Project Link: [https://github.com/yebeniyam/annuti](https://github.com/yebeniyam/annuti)
