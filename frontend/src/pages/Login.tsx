import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  CircularProgress,
  Link,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import { login } from '../features/auth/authSlice';
import { RootState, AppDispatch } from '../store';

// Define the type for location state
interface LocationState {
  state?: {
    registrationSuccess?: boolean;
  };
}

// Define the type for location state
interface LocationState {
  state?: {
    registrationSuccess?: boolean;
  };
}

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const location = useLocation() as unknown as LocationState;
  const { loading, error } = useSelector((state: RootState) => state.auth);
  const registrationSuccess = location.state?.registrationSuccess;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await dispatch(login({ username: email, password })).unwrap();
      navigate('/'); // Redirect to dashboard after login
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            Bendine - Login
          </Typography>
          
          <form onSubmit={handleSubmit}>
            <TextField
              variant="outlined"
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              variant="outlined"
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            
            {registrationSuccess && (
              <Alert severity="success" sx={{ mb: 2 }}>
                Registration successful! Please log in.
              </Alert>
            )}
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
          </form>
          
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body2">
              Don't have an account?{' '}
              <Link component={RouterLink} to="/register" variant="body2">
                Sign up
              </Link>
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              <Link component={RouterLink} to="/" variant="body2">
                Back to Home
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};
export default LoginPage;