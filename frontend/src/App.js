import React from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './App.css'
import Login from './components/Login/Login'
const router = createBrowserRouter([
  {
    path: '/',
    element: <div>Home</div>
  },
  {
    path: '/login',
    element: <Login type="Login" />
  },
  {
    path: '/register',
    element: <Login type="Register" />
  }
])

function App() {
  return <RouterProvider router={router} />
}

export default App
