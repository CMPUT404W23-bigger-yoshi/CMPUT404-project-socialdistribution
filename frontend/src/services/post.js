import axios from 'axios';

export function getPost(authorId, postId) {
  return axios.get(`/authors/${authorId}/posts/${postId}`);
}

export function getPosts(authorId) {
  return axios.get(`/authors/${authorId}/posts`);
}
