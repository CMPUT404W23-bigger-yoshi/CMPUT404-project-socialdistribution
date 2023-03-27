import axios from 'axios';
import { getCurrentUserDetails } from './author';

axios.defaults.baseURL = '/api';

export function getPost(authorId, postId) {
  return axios.get(`/authors/${authorId}/posts/${postId}`);
}

export function getPosts(authorId) {
  return axios.get(`/authors/${authorId}/posts`);
}

export async function generatePostId(authorId, postContent) {
  try {
    const userDetails = await getCurrentUserDetails(authorId);
    const data = {
      ...postContent,
      author: userDetails.data,
      published: new Date().toISOString(),
      origin: '',
      source: '',
      description: ''
    };
    const config = {
      method: 'post',
      url: `/authors/${authorId}/posts`,
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify(data)
    };
    return await axios(config);
  } catch (error) {
    console.log(error);
  }
}

export async function getAllPosts(authorId) {
  const config = {
    method: 'get',
    url: `/authors/${authorId}/posts`,
    headers: {}
  };
  return axios(config);
}

export async function deletePost(authorId, postId) {
  console.log('deletePost', authorId, postId);
  const config = {
    method: 'delete',
    url: `/authors/${authorId}/posts/${postId}`,
    headers: {}
  };
  return axios(config);
}

export async function updatePost(
  authorId,
  postId,
  newPostContent,
  oldPostContent
) {
  // authorId = last part of author url
  // postId = last part of post url
  const newAuthorId = authorId.split('/').pop();
  const newPostId = postId.split('/').pop();
  try {
    // made a data variable with the changed post content keys only
    // i.e. the difference between the old and new post content
    const data = Object.keys(newPostContent).reduce((acc, key) => {
      if (newPostContent[key] !== oldPostContent[key]) {
        acc[key] = newPostContent[key];
      }
      return acc;
    }, {});
    const config = {
      method: 'post',
      url: `/authors/${newAuthorId}/posts/${newPostId}`,
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify(data)
    };
    return await axios(config);
  } catch (error) {
    console.log(error);
  }
}

export async function getInbox(authorId) {
  const config = {
    method: 'get',
    url: `/authors/${authorId}/inbox`
  };
  return axios(config);
}

export async function getLikes(authorId, postId) {
  return await axios.get(`/authors/${authorId}/posts/${postId}/likes`);
}

export async function likePost(authorId, postId) {
  return await axios.put(`/authors/${authorId}/posts/${postId}/likes`);
}

export async function unlikePost(authorId, postId) {
  const config = {
    method: 'delete',
    url: `/authors/${authorId}/posts/${postId}/likes`,
    headers: {}
  };
  return axios(config);
}

export async function makeComment(comment, authorId) {
  return await axios.post(`/authors/${authorId}/comments`, comment);
}
