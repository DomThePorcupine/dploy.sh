var express = require('express')
var serveStatic = require('serve-static')

var app = express()

app.use(serveStatic('pub', {'index': ['index.html']}))

app.listen(7075)
