var express = require('express');
var router = express.Router();

const config = require('../config'), box = require('../box');

function getRandomArbitrary(min, max) {
  return Math.random() * (max - min) + min;
}

function unwrap_or_new(req, res) {
  if ("__session" in req.cookies) {
    console.log("CURRENT SESSION", req.cookies["__session"]);
  } else {
    // prefixed with [0.] --> to know that's only debug token
    res.cookie('__session',
               getRandomArbitrary(0, 1).toString(16).toUpperCase());
  }
  return req, res, req.cookies["__session"];
}

function unwrap_msg(req, res) {
  var msg = null;
  if ("__msg" in req.cookies) {
    msg = req.cookies["__msg"];
    res.clearCookie("__msg");
    console.log("[[[MSG]]]", msg);
  }
  return req, res, msg;
}

////////////////////////////////////////////////////////////////////////////////

router.get('/', function(req, res, next) {
  req, res, session = unwrap_or_new(req, res);
  req, res, msg = unwrap_msg(req, res);
  res.cookie('__last_page', "/");

  box.get_history_for_session(req.app, session, function(history) {
    box.get_products(req.app, function(products) {
      res.render('index', {
        title : 'Memegro (home)',
        products : products,
        history : history,
        msg : msg
      });
    });
  });
});

router.get('/checkout', function(req, res, next) {
  req, res, session = unwrap_or_new(req, res);
  req, res, msg = unwrap_msg(req, res);
  res.cookie('__last_page', "/checkout");

  box.get_history_for_session(req.app, session, function(history) {
    if (history.length === 0) {
      res.redirect("/");
    } else {
      box.get_products(req.app, function(products) {
        res.render('checkout', {
          title : 'Memegro (checkout)',
          products : products,
          history : history,
          msg : msg
        });
      });
    }
  });
});

module.exports = router;
