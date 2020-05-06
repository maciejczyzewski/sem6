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

function redirect(req, res) {
  if (!("__last_page" in req.cookies)) {
    req.cookies["__last_page"] = "/";
  }
  res.redirect(req.cookies["__last_page"]);
}

////////////////////////////////////////////////////////////////////////////////

router.get('/add/:id', async (req, res, next) => {
  const product_id = req.params.id;
  req, res, session = unwrap_or_new(req, res);

  box.add_history_mutex(req.app, session, product_id, type = 1, function(_) {
    // FIXME: already in if type == 2 v session
    box.get_history_winner(req.app, product_id, function(d) {
      if (d[0].session.localeCompare(session) === 0) {
        box.add_history_mutex(req.app, session, product_id, type = 2,
                              function(_) {
                                console.log(">>>> OKAY <<<<");
                                res.cookie('__msg', "added!");
                                redirect(req, res); // okay
                              });
      } else {
        console.log(">>>> WRONG!!! <<<<");
        res.cookie('__msg', "someone was faster!");
        redirect(req, res); // wrong
      }
    });
  });
});

router.get('/del/:id', async (req, res, next) => {
  const product_id = req.params.id;
  req, res, session = unwrap_or_new(req, res);

  box.del_history_mutex(req.app, session, product_id,
                        function(_) { redirect(req, res); });
});

router.get('/clear', async (req, res, next) => {
  req, res, session = unwrap_or_new(req, res);

  box.del_history_mutex(req.app, session, null, function(_) {
    res.cookie('__msg', "everything cleared!");
    res.redirect("/");
  });
});

router.get('/pay', async (req, res, next) => {
  req, res, session = unwrap_or_new(req, res);

  box.get_history_for_session(req.app, session, function(d) {
    var arr = [];
    d.forEach(function(entry) { arr.push(entry.product_id); });
    console.log("----> PAY: ", arr);
    box.del_products(req.app, product_id = arr, function(_) {
      box.del_history_mutex(req.app, session, null, function(_) {
        res.cookie('__msg', "you payed! thx for using memegro!");
        res.redirect("/");
      });
    });
  });
});

module.exports = router;
