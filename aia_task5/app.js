var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

const MongoClient = require('mongodb').MongoClient;
var cookieParser = require('cookie-parser');
var exphbs  = require('express-handlebars');

const config = require('./config'), box = require('./box');
var indexRouter = require('./routes/index');
var actionsRouter = require('./routes/actions');
console.log(config);

var app = express();

// view engine setup
app.engine('handlebars', exphbs());
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'handlebars');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({extended : false}));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/a/', actionsRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) { next(createError(404)); });

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

MongoClient.connect(
    config.database.url, {promiseLibrary : Promise}, (err, client) => {
      if (err) {
        logger.warn(`Failed to connect to the database. ${err.stack}`);
      }
      // save for later & generate some data
      app.locals.db = client.db(config.database.name);
      box.generate_data(app);
    });

module.exports = app;
