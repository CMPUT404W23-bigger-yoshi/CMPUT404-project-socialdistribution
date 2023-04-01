import axios from 'axios';
import { getUserDetails } from './author';
axios.defaults.baseURL = '/api';

export function getPost(authorId, postId) {
  return axios.get(`/authors/${authorId}/posts/${postId}`);
}

export function getPosts(authorUrl) {
  if (authorUrl.match('bigger-yoshi')) {
    return axios.get(`/authors/${authorUrl.split('/').pop(-1)}/posts/`);
  }
  const encoded = encodeURIComponent(authorUrl);
  return axios.get(`/authors/foreign/${encoded}/posts`);
}

export async function generatePostId(author, postContent) {
  try {
    const data = {
      ...postContent,
      author,
      published: new Date().toISOString(),
      origin: '',
      source: '',
      description: ''
    };
    const config = {
      method: 'post',
      url: `${author.id}/posts/`,
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

export function getInbox(authorId) {
  return axios.get(`${authorId}/inbox`);
}

export async function getLikes(postUrl) {
  if (postUrl.match('bigger-yoshi')) {
    return await axios.get(`/authors/${postUrl.split('/').pop(-1)}/likes/`);
  }
  const encoded = encodeURIComponent(postUrl);
  return await axios.get(`/authors/foreign/${encoded}/likes`);
}

export async function likePost(likeObj) {
  const postUrl = likeObj.object;
  if (postUrl.match('bigger-yoshi')) {
    return axios.post(`/authors/${postUrl.split('/').pop(-3)}/inbox/`, likeObj);
  }
  const encoded = encodeURIComponent(postUrl);
  return axios.post(`/authors/foreign/${encoded}/foreign-inbox`, likeObj);
}

export async function makeComment(authorId, commentObj) {
  const config = {
    method: 'post',
    url: `/authors/${authorId}/inbox/`,
    headers: {
      'Content-Type': 'application/json'
    },
    data: JSON.stringify(commentObj)
  };
  return await axios(config);
}

export async function getComments(postUrl) {
  if (postUrl.match('bigger-yoshi')) {
    return await axios.get(`/authors/${postUrl.split('/').pop(-1)}/comments/`);
  }
  const encoded = encodeURIComponent(postUrl);
  return await axios.get(`/authors/foreign/${encoded}/comments`);
}
