import {createBrowserRouter, RouterProvider,} from "react-router-dom";
import Login from './components/Login/Login';
import './App.css';
import Register from "./components/Register/Register";

const router = createBrowserRouter([
  {
    path: "/",
    element: <div>Home</div>,
  },
  {
    path: "/login",
    element: <Login/>,
  },
  {
    path: "/register",
    element: <Register/>,
  }
]);


function App() {
  return (
    <RouterProvider router={router}/>
  );
}

export default App;
