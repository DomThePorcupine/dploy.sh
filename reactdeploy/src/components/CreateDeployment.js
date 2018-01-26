import React, { Component } from 'react'
import { Form, Grid, Segment, Message, Icon } from 'semantic-ui-react'

// Grab our custom css
import '../styles/cdeps.css'

// Need the axios lib for making a post reqest
var axios = require('axios')


class CreateDeployment extends Component {
  state = { name: '', git_url: '', dir: '', cont_port: '', 
            local_port: '', isActive: false, 
            message:'Creating Deployment, please wait...',
            bad_git: false, m_header: 'Just one second' }

  // Update fields
  handleChange = (e, { name, value }) => {
    if(name === 'git_url') {
      this.setState({'bad_git': false })
    }
    this.setState({ [name]: value })
  }

  createNewDeployment = () => {
    this.setState({'isActive': true})
    const { name, git_url, dir, cont_port, local_port } = this.state
    axios.post('http://api.dploy.sh.doms.land/deployments/', {
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
    }, error => {
      this.setState({'m_header': 'ERROR.'})
      this.setState({'message': error.response.data.message})
      if(error.response.data.reason === 'bad_git_url') {
        this.setState({'bad_git': true})
      }
      // Finally turn off the error after 2 seconds
      setTimeout(function(){this.setState({'isActive': false})}.bind(this),2000)
    })
  }

  render() {
    const { name, git_url, dir, cont_port, local_port, message, m_header } = this.state
    return (
      
      <div className="createDeployment">
      <Message icon className={this.state.isActive ? '' : 'hidden'}>
          <Icon name='circle notched' loading />
          <Message.Content>
            <Message.Header>{m_header}</Message.Header>
            {message}
          </Message.Content>
        </Message>
      <h1>Create your next deployment! :D</h1>
      <Form onSubmit={this.createNewDeployment}>
      <Grid columns={3} divided>
        
          <Grid.Row stretched>
          <Grid.Column>
            <Segment><Form.Input className="box" placeholder='Name' name='name' value={name} onChange={this.handleChange}/></Segment>
            <Segment color={this.state.bad_git ? 'red' : ''}><Form.Input className="box" placeholder='Git Url' name='git_url' value={git_url} onChange={this.handleChange}/></Segment>
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