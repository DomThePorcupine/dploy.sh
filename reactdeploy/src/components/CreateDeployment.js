import React, { Component } from 'react'
import { Form, Grid, Segment, Message, Icon } from 'semantic-ui-react'

// Grab our custom css
import '../styles/cdeps.css'

// Need the axios lib for making a post reqest
var axios = require('axios')


class CreateDeployment extends Component {
  state = { name: '', git_url: '', dir: '', cont_port: '', local_port: '', isActive: false }

  // Update fields
  handleChange = (e, { name, value }) => this.setState({ [name]: value })

  createNewDeployment = () => {
    this.setState({'isActive': true})
    const { name, git_url, dir, cont_port, local_port } = this.state
    axios.post('http://127.0.0.1:8000/deployments/', {
      name: name,
      git: git_url,
      dir: dir,
      run: false,
      cport: cont_port,
      lport: local_port
    }, {withCredentials: true}).then(response => {
      // Redirect to the details page
      this.setState({'isActive': false})
      this.props.history.push('/deployment/' + response.data.id)
    }, response => {
      // Handle the error in some way
    })
  }

  render() {
    const { name, git_url, dir, cont_port, local_port, isActive } = this.state
    return (
      
      <div className="createDeployment">
      <Message icon className={this.state.isActive ? '' : 'hidden'}>
          <Icon name='circle notched' loading />
          <Message.Content>
            <Message.Header>Just one second</Message.Header>
            Creating Deployment, please wait...
          </Message.Content>
        </Message>
      <h1>Create your next deployment! :D</h1>
      <Form onSubmit={this.createNewDeployment}>
      <Grid columns={3} divided>
        
          <Grid.Row stretched>
          <Grid.Column>
            <Segment><Form.Input className="box" placeholder='Name' name='name' value={name} onChange={this.handleChange}/></Segment>
            <Segment><Form.Input className="box" placeholder='Git Url' name='git_url' value={git_url} onChange={this.handleChange}/></Segment>
          </Grid.Column>
          <Grid.Column>
            <Segment><Form.Input className="box" placeholder='Directory' name='dir' value={dir} onChange={this.handleChange}/></Segment>
            <Segment><Form.Input className="box" placeholder='Container Port' name='cont_port' value={cont_port} onChange={this.handleChange}/></Segment>
          </Grid.Column>
          <Grid.Column>
            <Segment><Form.Input className="box" placeholder='Local Port' name='local_port' value={local_port} onChange={this.handleChange}/></Segment>
            <Segment><Form.Button className="submit" content='Submit' /></Segment>
            
          </Grid.Column>
          
          </Grid.Row>
        
      </Grid>
      </Form>
      </div>
    )
  }
}

export default CreateDeployment;