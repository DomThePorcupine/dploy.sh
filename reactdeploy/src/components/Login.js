import React, { Component } from 'react'
import { Form, Message, Icon } from 'semantic-ui-react'
import '../styles/login.css'
var axios = require('axios')

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class Login extends Component {
  state = { name: '', pass: '', isActive: false, err: 'Trying to log you in.'}
  handleChange = (e, { name, value }) => this.setState({ [name]: value })
  handleSubmit = () => {
    this.setState({'isActive': true})
    const { name, pass } = this.state

    axios.post('http://api.dploy.sh.doms.land/login/', {username:name,password:pass}, {withCredentials: true}).then(response => {
      if(response.data.message === 'success') {
        this.props.history.push('/')
        return
      } else {
        this.setState({'err': 'Authentication failed!'})
        setTimeout(function(){
          this.setState({'isActive': false})
        }.bind(this), 1000)
      }
    }, response => {
      return false
    })
  }

  render() {
    const { name, pass } = this.state
    return (
      <div className="login">
        <h1>Login to manage containers :)</h1>
        <Message icon className={this.state.isActive ? '' : 'hidden'}>
          <Icon name='circle notched' loading />
          <Message.Content>
            <Message.Header>Just one second</Message.Header>
            {this.state.err}
          </Message.Content>
        </Message>
        <Form onSubmit={this.handleSubmit}>
          <Form.Group>
            <Form.Input className="box" placeholder='Name' name='name' value={name} onChange={this.handleChange}/>
            <Form.Input className="box" type="password" placeholder='Password' name='pass' value={pass} onChange={this.handleChange}/>
            
            <Form.Button className="submit" content='Submit' />
          </Form.Group>
        </Form>
      </div>
    );
  }
}

export default Login;
