import axios from 'axios'

export const login = ({ email, password }) => {
  return axios.post('/authors/login', {
    email,
    password
  })
}

export const register = ({ email, password, confirmPassword }) => {
  return axios.post('/authors/register', {
    email,
    password,
    confirmPassword
  })
}
