import axios from 'axios';
import { getUserDetails } from './author';
axios.defaults.baseURL = '/api';

export function getPost(authorId, postId) {
  return axios.get(`/authors/${authorId}/posts/${postId}`);
}

export function getPosts(authorUrl) {
  if (authorUrl.match(window.location.host)) {
    return axios.get(`/authors/${authorUrl.split('/').pop()}/posts/`);
  }
  const encoded = encodeURIComponent(`${authorUrl}/posts`);
  return axios.get(`/authors/foreign-inbox/${encoded}`);
}

export async function generatePostId(author, postContent) {
  try {
    const data = {
      ...postContent,
      author,
      published: new Date().toISOString(),
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
  return axios.get(`${authorId}/inbox?size=100&page=1`);
}

export function sendtoInbox(authorId, postObj) {
  if (authorId.match(window.location.host)) {
    return axios.post(
      `authors/${authorId.split('authors/').pop().split('/')[0]}/inbox/`,
      postObj
    );
  }
  const encoded = encodeURIComponent(`${authorId}/inbox`);
  return axios.post(`/authors/foreign-inbox/${encoded}`, postObj);
}

export function getHomeFeed() {
  return axios.get('/authors/posts');
}

export async function getLikes(postUrl) {
  if (postUrl.match(window.location.host)) {
    return await axios.get(`${postUrl}/likes`);
  }
  const encoded = encodeURIComponent(`${postUrl}/likes`);
  return await axios.get(`/authors/foreign-inbox/${encoded}`);
}

export async function likePost(likeObj) {
  const postUrl = likeObj.object;
  if (postUrl.match(window.location.host)) {
    return axios.post(
      `authors/${postUrl.split('authors/').pop().split('/')[0]}/inbox/`,
      likeObj
    );
  }
  const encoded = encodeURIComponent(`${postUrl.split('/posts')[0]}/inbox`);
  return axios.post(`/authors/foreign-inbox/${encoded}`, likeObj);
}

export function makeComment(commentObj) {
  const postUrl = commentObj.object;
  if (postUrl.match(window.location.host)) {
    return axios.post(
      `authors/${postUrl.split('authors/').pop().split('/')[0]}/inbox/`,
      commentObj
    );
  }
  const encoded = encodeURIComponent(`${postUrl.split('/posts')[0]}/inbox/`);
  return axios.post(`/authors/foreign-inbox/${encoded}`, commentObj);
}

export async function getComments(postUrl) {
  if (postUrl.match(window.location.host)) {
    return await axios.get(`${postUrl}/comments`);
  }
  const encoded = encodeURIComponent(`${postUrl}/comments`);
  return await axios.get(`/authors/foreign-inbox/${encoded}`);
}

export async function getCommentLikes(commentUrl) {
  if (commentUrl.match(window.location.host)) {
    return await axios.get(`${commentUrl}/likes`);
  }
  const encoded = encodeURIComponent(`${commentUrl}/likes`);
  return await axios.get(`/authors/foreign-inbox/${encoded}`);
}
