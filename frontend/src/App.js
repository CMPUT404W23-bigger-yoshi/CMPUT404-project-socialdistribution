import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import './App.css';
import Login from './components/Login/Login';
import Home from './components/Home/Home';
import Logout from './components/Login/Logout';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />
  },
  {
    path: '/author/:id/posts/:postId',
    element: <Home />
  },
  {
    path: '/login',
    element: <Login type="Login" />
  },
  {
    path: '/logout',
    element: <Logout />
  },
  {
    path: '/register',
    element: <Login type="Register" />
  },
  {
    path: '/profile',
    element: <Home />
  },
  {
    path: '/author/:id/posts/:postId',
    element: <Home />
  },
  {
    path: '/private',
    element: <Home />
  },
  {
    path: '/notifications',
    element: <Home />
  },
  {
    path: '/settings',
    element: <Home />
  }
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
