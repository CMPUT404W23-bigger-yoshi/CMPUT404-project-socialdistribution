import React, { useEffect } from 'react';
import { logout } from '../../services/auth';
import { useNavigate } from 'react-router-dom';

export default function Logout() {
  const navigate = useNavigate();
  useEffect(() => {
    const logoutUser = async () => {
      try {
        const response = await logout();
        if (response.status === 200) {
          console.log('Logged out');
        }
      } catch (error) {
        console.error(error);
      }
    };
    logoutUser().then(r => console.log(r));
    navigate('/login');
  }, []);
  return <div></div>;
}
