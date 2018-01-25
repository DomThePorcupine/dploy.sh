import React, { Component } from 'react'
import { List, Label } from 'semantic-ui-react'
import { Link } from 'react-router-dom'

// Custom home css
import '../styles/home.css'

var axios = require('axios')

class Home extends Component {
  state = {'deployments': [] }
  componentDidMount() {
    console.log('works')
    axios.get('http://127.0.0.1:8000/deployments/', {withCredentials: true}).then(response => {
      this.setState({'deployments': JSON.parse(response.data)})
    })
  }

  render() {
    return (
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
    );
  }
}

export default Home;
