import axios from 'axios';
axios.defaults.baseURL = '/api';

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

export const getUserDetails = async (authorId) => {
  return await axios.get(`/authors/${authorId}`);
};

export const updateCurrentUserDetails = async (authorId, data) => {
  const userDetails = {
    ...data,
    type: 'author'
  };
  const config = {
    method: 'post',
    url: `/authors/${authorId}`,
    headers: {
      'Content-Type': 'application/json'
    },
    data: JSON.stringify(userDetails)
  };
  return axios(config);
};

export const searchSingleUser = async (username) => {
  return await axios.get(`/authors/${username}/search`);
};

export const searchMultipleUsers = async (username) => {
  return await axios.get(`/authors/${username}/search/multiple`);
};

export const sendFollowRequest = async (authorId, followObject) => {
  return await axios.post(`/authors/${authorId}/inbox/`, followObject);
};

export const followUser = async (authorId, foreignAuthorId) => {
  return await axios.put(`/authors/${authorId}/followers/${foreignAuthorId}/`);
};

export const unfollowUser = async (authorId, foreignAuthorId) => {
  return await axios.delete(
    `/authors/${authorId}/followers/${foreignAuthorId}/`
  );
};

export const checkIfFollowing = async (authorId, foreignAuthorId) => {
  return await axios.get(`/authors/${authorId}/followers/${foreignAuthorId}/`);
};

export const getFollowersCount = async (authorId) => {
  return await axios.get(`/authors/${authorId}/followers/count/`);
};
