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

export const getUserDetails = (authorUrl) => {
  if (authorUrl.match(window.location.host)) {
    return axios.get(`/authors/${authorUrl.split('/').pop()}`);
  }
  const encoded = encodeURIComponent(`${authorUrl}`);
  return axios.get(`/authors/foreign-inbox/${encoded}`);
};

export const getUserById = async (authorId) => {
  return axios.get(`/authors/${authorId}`);
};

export const updateCurrentUserDetails = async (authorId, data) => {
  const authorIdVal = authorId.split('/').pop();
  return await axios.post(`/authors/${authorIdVal}`, data);
};

export const searchMultipleUsers = async (username) => {
  return await axios.get(`/authors/${username}/search/multiple`);
};

export const acceptFollowRequest = async (authorId, foreignAuthorId) => {
  return await axios.put(`/authors/${authorId}/followers/${foreignAuthorId}`);
};

export const unfollowUser = async (authorId, foreignAuthorId) => {
  const authorIdVal = authorId.split('/').pop();
  return await axios.delete(
    `/authors/${authorIdVal}/followers/${foreignAuthorId}`
  );
};

export const getFollowersCount = async (authorUrl) => {
  if (authorUrl.match(window.location.host)) {
    const res = await axios.get(
      `/authors/${authorUrl.split('/').pop()}/followers/count`
    );
    return res.data.count;
  }
  const encoded = encodeURIComponent(`${authorUrl}/followers/`);
  const res = await axios.get(`/authors/foreign-inbox/${encoded}`);
  return res.data.items.length;
};

export const checkFollowing = async (authorUrl, foreignAuthorUrl) => {
  if (foreignAuthorUrl.match(window.location.host)) {
    const res = await axios.get(
      `/authors/${foreignAuthorUrl.split('/').pop()}/followers/${authorUrl}`
    );
    return res.data;
  }
  const encoded = encodeURIComponent(`${foreignAuthorUrl}/followers/`);
  const res = await axios.get(`/authors/foreign-inbox/${encoded}`);
  return {
    found:
      res.data.items.some((item) => item.url === authorUrl) ||
      res.data.items.some((item) => item.id === authorUrl)
  };
};

export const sendFollowRequest = async (follower, toFollow) => {
  const data = {
    type: 'Follow',
    summary: `${follower?.displayName} wants to follow ${toFollow?.displayName}`,
    actor: {
      type: 'author',
      ...follower
    },
    object: {
      type: 'author',
      ...toFollow
    }
  };
  if (toFollow.id.match(window.location.host)) {
    return axios.post(`/authors/${toFollow.id.split('/').pop()}/inbox/`, {
      ...data
    });
  }
  const encoded = encodeURIComponent(
    `${toFollow.id.replace(/[/]$/, '')}/inbox`
  );
  return axios.post(`/authors/foreign-inbox/${encoded}`, { ...data });
};

export const getFollowRequests = (authorId) => {
  return axios.get(`/authors/${authorId}/follow-requests`);
};
