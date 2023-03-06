import axios from 'axios';

export const login = ({ username, password }) => {
  return axios.post('/authors/login', {
    username,
    password
  });
};

export const register = ({ username, password, confirmPassword }) => {
  return axios.post('/authors/register', {
    username,
    password,
    confirmPassword
  });
};

export const logout = async () => {
  return await axios.post('/authors/logout');
};

export const getCurrentUserId = async () => {
  return await axios.get('/authors/authenticated_user_id');
};

export const getCurrentUserDetails = async (authorId) => {
  return await axios.get(`/authors/${authorId}`);
};
