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
}

export const getCurrentUserId = async () => {
  return await axios.get('/authors/authenticated_user_id');
}

export const getCurrentUserDetails = async (authorId) => {
  return await axios.get(`/authors/${authorId}`);
}

export const updateCurrentUserDetails = async (authorId, data) => {
  const userDetails = {
    ...data,
    type: 'author'
  }
  const config = {
    method: 'post',
    url: `/authors/${authorId}`,
    headers: {
      'Content-Type': 'application/json'
    },
    data: JSON.stringify(userDetails)
  }
  return axios(config);
}
