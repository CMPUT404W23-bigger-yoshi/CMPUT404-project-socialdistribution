import axios from 'axios';

export const login = ({email, password}) => {
  return axios.post('/auth/login', {
    "email": email,
    "password": password
  });
}

export const register = ({email, password, confirmPassword}) => {
  return axios.post('/auth/register', {
    "email": email,
    "password": password,
    "confirmPassword": confirmPassword
  });
}
