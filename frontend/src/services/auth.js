import axios from 'axios'

export const login = ({ username, password }) => {
  return axios.post('/authors/login', {
    username,
    password
  })
}

export const register = ({ username, password, confirmPassword }) => {
  return axios.post('/authors/register', {
    username,
    password,
    confirmPassword
  })
}
