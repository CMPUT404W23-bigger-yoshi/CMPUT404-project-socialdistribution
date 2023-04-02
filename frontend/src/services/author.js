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

export const getUserDetails = async (authorUrl) => {
  // Check if it is a url or id
  let isUrl = true;
  try {
    URL(authorUrl);
  } catch (_) {
    isUrl = false;
  }

  if (
    authorUrl.match('bigger-yoshi') ||
    authorUrl.match('localhost') ||
    !isUrl
  ) {
    console.log(`/authors/${authorUrl.split('/').pop(-1)}`);
    return axios.get(`/authors/${authorUrl.split('/').pop(-1)}`);
  }
  const encoded = encodeURIComponent(`${authorUrl}`);
  return axios.get(`/authors/foreign-inbox/${encoded}`);
};

export const getUserById = async (authorId) => {
  return axios.get(`/authors/${authorId}`);
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

export const approveFollowRequest = async (authorId, followObject) => {
  return await axios.post(`/authors/${authorId}/inbox/`, followObject);
};

export const acceptFollowRequest = async (authorId, foreignAuthorId) => {
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

export const getFollowersCount = async (authorUrl) => {
  if (authorUrl.match(window.location.host)) {
    const res = await axios.get(
      `/authors/${authorUrl.split('/').pop(-1)}/followers/count`
    );
    return res.data.count;
  }
  const encoded = encodeURIComponent(`${authorUrl}/followers/`);
  const res = await axios.get(`/authors/foreign-inbox/${encoded}`);
  return res.data.items.length;
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
    return axios.post(`/authors/${toFollow.id.split('/').pop(-1)}/inbox`, {
      ...data
    });
  }
  const encoded = encodeURIComponent(`${toFollow.id}/inbox`);
  return axios.post(`/authors/foreign-inbox/${encoded}`, { ...data });
};

export const getFollowRequests = (authorId) => {
  return axios.get(`/authors/${authorId}/follow-requests`);
};
