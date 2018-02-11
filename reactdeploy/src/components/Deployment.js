import React, { Component } from 'react';
import { Button, Message, Icon, Label, Modal, Header } from 'semantic-ui-react';

// Import our custom css
import '../styles/dep.css'

// Get our API url
import { API } from './api'

import axios from 'axios'

axios.defaults.xsrfCookieName = 'XSRF-TOKEN'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class Depoyment extends Component {
  
  state = {openmodal: false, key: '', 'deployment': {}, isActive: false, running: false, message: '',  }

  componentDidMount() {
    axios.get(API + '/deployments/' + this.props.match.params.id +'/', {withCredentials: true}).then(response => {
      var ndep = JSON.parse(response.data)[0]
      this.setState({'deployment': ndep.fields})
      this.setState({'running': this.state.deployment.is_running})
    })
  }

  fetchKey = () => {
    
    axios.get(API + '/deployments/' + this.props.match.params.id + '/key/', {withCredentials: true}).then(response => {
      var res = response.data
      this.setState({'key': res.ssh_key})
      this.setState({'openmodal': true})
    }, error => {
      // Do something
    })
  }

  startContainer = () => {
    this.setState({'message': 'Starting container...'})
    this.setState({'isActive': true})
    axios.get(API + '/deployments/' + this.props.match.params.id + '/start/', {withCredentials: true}).then(response => {
      var res = response.data
      if (res.message === 'success') {
        this.setState({'running': true})
      }
      this.setState({'isActive': false})
    }, error => {
      setTimeout(function(){
        this.setState({'message': error.response.data.message})
      }.bind(this), 1000)
      
      setTimeout(function(){
        this.setState({'isActive': false})
      }.bind(this), 4000)
    })
  }

  stopContainer = () => {
    this.setState({'message': 'Stoping container...'})
    this.setState({'isActive': true})
    axios.get(API + '/deployments/' + this.props.match.params.id + '/stop/', {withCredentials: true}).then(response => {
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
    axios.get(API + '/deployments/' + this.props.match.params.id + '/build/', {withCredentials: true}).then(response => {
      this.setState({'isActive': false})
    })
  }
  deleteDeployment = () => {
    axios.delete(API + '/deployments/' + this.props.match.params.id + '/delete/', {withCredentials: true}).then(response => {
      this.props.history.push('/')
    })
  }

  testWebhook = () => {
    this.setState({'message': 'Testing webhook...'})
    this.setState({'isActive': true})
    axios.post(API + '/webhooks/' + this.state.deployment.webhook_text + '/', {withCredentials: true}).then(response => {
      this.setState({'isActive': false})
    })
  }

  close = () => this.setState({ openmodal: false })

  render() {
    const { openmodal, deployment, running, message, key } = this.state
    return (
      <div className="deployment">
        <Modal open={openmodal} basic>
          <Header icon='lock' content='Paste this key into github' />
          <Modal.Content>
            <div className="sshkey">{key}</div>
          </Modal.Content>
          <Modal.Actions>
            <Button color='green' onClick={this.close}>
              <Icon name='checkmark' /> Done
            </Button>
          </Modal.Actions>
        </Modal>
        <Message icon className={this.state.isActive ? '' : 'hidden'}>
          <Icon name='circle notched' loading />
          <Message.Content>
            <Message.Header>Just one second</Message.Header>
            {message}
          </Message.Content>
        </Message>
        <h1>Name: {deployment.name_text} <Button onClick={this.deleteDeployment} style={{float:'right'}} icon><Icon name='trash'  /></Button></h1>
        
        <h3>Git URL: {deployment.git_url_text}
        <Label className="btn" size='small' color='pink' as='a' tag>{deployment.git_branch_text}</Label>
        </h3>
        <h3>Path: {deployment.dir_text}</h3>
        <h3>Status: {running ? "Running":"Stopped"}
        <Button className="btn" color="green" onClick={this.startContainer}>Start</Button>
        <Button className="btn" color="red" onClick={this.stopContainer}>Stop</Button>
        <Button className="btn" color="blue" onClick={this.buildContainer}>Build</Button>
        </h3>
        <h3>Webhook URL: /webhooks/{deployment.webhook_text}/<Button onClick={this.testWebhook} className="btn" color="blue">Test</Button></h3>
        <Button onClick={this.fetchKey} >Show ssh-key</Button>
      </div>
    );
  }
}

export default Depoyment;
