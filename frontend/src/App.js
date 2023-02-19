import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './App.css';
import Login from './components/Login/Login';
import Profile from './components/Profile/Profile';

const router = createBrowserRouter([
  {
    path: '/',
    element: <div>Home</div>
  },
  {
    path: '/login',
    element: <Login type='Login' />
  },
  {
    path: '/register',
    element: <Login type='Register' />
  },
  {
    path: '/profile',
    element: <Profile />
  }
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
