import React, { Component } from 'react';
import { Button, Message, Icon } from 'semantic-ui-react';

// Import our custom css
import '../styles/dep.css'


var axios = require('axios')

class Depoyment extends Component {
  state = {'deployment': {}, isActive: false, running: false, message: '' }
  componentDidMount() {
    axios.get('http://127.0.0.1:8000/deployments/' + this.props.match.params.id, {withCredentials: true}).then(response => {
      var ndep = JSON.parse(response.data)[0]
      console.log(ndep.fields)
      this.setState({'deployment': ndep.fields})
      this.setState({'running': this.state.deployment.is_running})
    })
  }

  startContainer = () => {
    this.setState({'message': 'Starting container...'})
    this.setState({'isActive': true})
    axios.get('http://127.0.0.1:8000/deployments/' + this.props.match.params.id + '/start/', {withCredentials: true}).then(response => {
      console.log(response.data)
      var res = response.data
      if (res.message === 'success') {
        this.setState({'running': true})
      }
      this.setState({'isActive': false})
    }, response => {
      console.log(response)
    })
  }

  stopContainer = () => {
    this.setState({'message': 'Stoping container...'})
    this.setState({'isActive': true})
    axios.get('http://127.0.0.1:8000/deployments/' + this.props.match.params.id + '/stop/', {withCredentials: true}).then(response => {
      console.log(response.data)
      var res = response.data
      if (res.message === 'success') {
        this.setState({'running': false})
      }
      this.setState({'isActive': false})
    })
  }

  buildContainer = () => {
    this.setState({'message': 'Building container...'})
    this.setState({'isActive': true})
    axios.get('http://127.0.0.1:8000/deployments/' + this.props.match.params.id + '/build/', {withCredentials: true}).then(response => {
      console.log(response.data)
      this.setState({'isActive': false})
    })
  }
  deleteDeployment = () => {
    axios.delete('http://127.0.0.1:8000/deployments/' + this.props.match.params.id + '/delete/', {withCredentials: true}).then(response => {
      this.props.history.push('/')
    })
  }

  render() {
    const { deployment, running, message } = this.state
    return (
      <div className="deployment">
        <Message icon className={this.state.isActive ? '' : 'hidden'}>
          <Icon name='circle notched' loading />
          <Message.Content>
            <Message.Header>Just one second</Message.Header>
            {message}
          </Message.Content>
        </Message>
        <h1>Name: {deployment.name_text} <Button onClick={this.deleteDeployment} style={{float:'right'}} icon><Icon name='trash'  /></Button></h1>
        
        <h3>Git URL: {deployment.git_url_text}</h3>
        <h3>Path: {deployment.dir_text}</h3>
        <h3>Status: {running ? "Running":"Stopped"}
        <Button className="btn" color="green" onClick={this.startContainer}>Start</Button>
        <Button className="btn" color="red" onClick={this.stopContainer}>Stop</Button>
        <Button className="btn" color="blue" onClick={this.buildContainer}>Build</Button>
        </h3>
        <h3>Webhook URL: /webhooks/{deployment.webhook_text}<Button className="btn" color="blue">Test</Button></h3>
      </div>
    );
  }
}

export default Depoyment;
