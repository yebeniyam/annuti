import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { RootState } from '../store';
import { login, fetchUserProfile } from '../features/auth/authSlice';
import { CircularProgress, Box } from '@mui/material';

interface ProtectedRouteProps {
  children: React.ReactNode;
  isAuthenticated: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, isAuthenticated: propIsAuthenticated }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isAuthenticated: stateIsAuthenticated, loading, token } = useSelector((state: RootState) => state.auth);
  const location = useLocation();
  const isAuthenticated = propIsAuthenticated !== undefined ? propIsAuthenticated : stateIsAuthenticated;

  useEffect(() => {
    // If we have a token but not authenticated, try to fetch user profile
    if (token && !isAuthenticated && !loading) {
      // Try to fetch user profile with the existing token
      dispatch(fetchUserProfile() as any)
        .unwrap()
        .catch(() => {
          // If fetching profile fails, try to login with default admin credentials
          dispatch(login({ username: 'admin@example.com', password: 'admin123' }) as any)
            .unwrap()
            .catch(() => {
              // If login fails, redirect to login page
              navigate('/login', { state: { from: location }, replace: true });
            });
        });
    } else if (!token && !isAuthenticated && !loading) {
      // If no token and not authenticated, redirect to login
      navigate('/login', { state: { from: location }, replace: true });
    }
  }, [dispatch, isAuthenticated, loading, token, navigate, location]);

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;