import axios from 'axios';

export const login = ({ email, password }) => {
  return axios.post('/auth/login', {
    email,
    password
  });
};

export const register = ({ email, password, confirmPassword }) => {
  return axios.post('/auth/register', {
    email,
    password,
    confirmPassword
  });
};
