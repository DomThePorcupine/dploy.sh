import React, { Component } from 'react'
import { Menu } from 'semantic-ui-react'
import {
  BrowserRouter as Router,
  Route,
  Link
} from 'react-router-dom'
// Import our own components
import Login from '../components/Login'
import Home from '../components/Home'
import Deployment from '../components/Deployment'
import CreateDeployment from '../components/CreateDeployment'

// Import our custom css
import './App.css'

class App extends Component {

  render() {
    return (
      <Router>
        <div>
        <Menu>
          <Menu.Item><Link to="/">Home</Link></Menu.Item>
          <Menu.Item><Link to="/login">Login</Link></Menu.Item>
          <Menu.Item><Link to="/deployment">New Deployment</Link></Menu.Item>
        </Menu>
        <Route exact path="/" component={Home}/>
        <Route path="/login" component={Login}/>
        <Route path="/deployment/:id" component={Deployment}/>
        <Route exact path="/deployment" component={CreateDeployment}/>
        </div>
      </Router>
    );
  }
}

export default App;
