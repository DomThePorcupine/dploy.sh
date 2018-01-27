import React, { Component } from 'react'
import { List, Label, Segment } from 'semantic-ui-react'
import { Link } from 'react-router-dom'

// Custom home css
import '../styles/home.css'

// Get our API url
import { API } from './api'

var axios = require('axios')

class Home extends Component {
  state = {'deployments': [], 'isActive': false, 'isSad': false }
  componentDidMount() {
    axios.get(API + '/deployments/', {withCredentials: true}).then(response => {
      
      if(JSON.parse(response.data).length === 0) {
        console.log('tre')
        this.setState({'isSad': true})
      }
      this.setState({'deployments': JSON.parse(response.data)})
      this.setState({'isActive':false})
    }, error => {
      console.log(error)
      // Handle the case that the user is not authenticated
      if(error.response.status === 403) {
        this.setState({'isActive': true})
      }
    })
  }

  render() {
    return (
      <div className="home">
        <div className={this.state.isActive ? 'notification' : 'hidden'}>
          <Segment color='red' >Please <Link to='/login'>login</Link> to view deployments.</Segment>
        </div>
        <div className={this.state.isSad ? 'sad' : 'hidden'}>
          <p>:'( You don't have any deployments</p>
        </div>
        <List animated verticalAlign='middle'>
          {this.state.deployments.map(function(item){
            return <List.Item key={item.pk} >
              <List.Content className="home">
                <div>
                <Link to={`/deployment/${item.pk}`} ><List.Header className="large-text"><span role="img" className="small-text" aria-label="foobar">😎</span> {item.fields.name_text}</List.Header></Link>
                <Label className="col" size='medium' color={item.fields.is_running ? 'green' : 'red'} as='a' tag>{item.fields.is_running ? 'Running': 'Stopped'}</Label>
                </div>
              </List.Content>
            </List.Item>;
          })}
        </List>
      </div>
    );
  }
}

export default Home;
