import axios from 'axios';
import { getCurrentUserDetails } from './author';

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
    }
    const config = {
      method: 'post',
      url: `/authors/${authorId}/posts`,
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify(data)
    }
    return await axios(config);
  } catch (error) {
    console.log(error);
  }
}
