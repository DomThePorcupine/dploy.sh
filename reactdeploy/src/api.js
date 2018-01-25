var axios = require('axios')

const login = (username, password) => {
  axios.post('http://127.0.0.1:8000/login/', {username:username,password:password}).then(response => {
    if(response.data.message === 'success') {
      console.log('all good')
      return true
    } else {
      return false
    }
  }, response => {
    return false
  })
}

module.exports = login