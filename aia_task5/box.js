const funcs = {
  async generate_data(app) {
    ///////////////// DEBUG /////////////////
    const products = app.locals.db.collection('products');
    products.deleteMany({});
    products.dropIndexes();
    products.createIndex({product_id : 1}, {unique : true});
    products.insertMany(
        [
          {product_id : '1', name : "meme1"},
          {product_id : '2', name : "meme2"},
          {product_id : '3', name : "meme3"},
          {product_id : '4', name : "meme4"},
          {product_id : '5', name : "meme5"},
          {product_id : '6', name : "meme6"},
        ],
        function(
            err,
            docs) { console.log("[+] `products`: dodano przykladowe dane"); });

    const history = app.locals.db.collection('history');
    history.deleteMany({});
    history.dropIndexes();
    history.createIndex({product_id : 1, session : 1, type : 1},
                        {unique : true});
    ///////////////// DEBUG /////////////////
  },

  async get_history_for_session(app, session, callback = function(_) {}) {
    const history = app.locals.db.collection('history');
    history.aggregate([
        {$match:
            {type : 2, session : session}
        },
        {$lookup: {
            from: "products",
            localField: "product_id",
            foreignField: "product_id",
            as: "fromItems"}
        },
        {$replaceRoot:
            {newRoot: { $mergeObjects: [ 
                { $arrayElemAt: [ "$fromItems", 0 ] }, "$$ROOT" ] } }
        },
        {$project:
            {fromItems: 0}
        }], function(err, docs) {
            docs.toArray(function(err, docs) {
              console.log("[.] `history`: zawartosc koszyka dla session=`" + session +
                          "`");
              console.log(docs);
              callback(docs);
            });
        });
  },

  async add_history_mutex(app, session, product_id, type = 1,
                          callback = function(_) {}) {
    var timestamp = Math.floor(Date.now());
    const history = app.locals.db.collection('history');
    history.insertMany([ {
                         time : timestamp,
                         product_id : product_id,
                         session : session,
                         type : type
                       } ],
                       function(err, docs) {
                         console.log(
                             "[+] `history`: zalozono mutex na product_id=`" +
                             product_id.toString() + "`");
                         callback(docs);
                       });
  },

  async get_history_winner(app, product_id, callback = function(_) {}) {
    const history = app.locals.db.collection('history');
    history.find({$query : {product_id : product_id}, $orderby : {time : -1}},
                 function(err, docs) {
                   console.log("[+] `history`: wybieram zwyciesce");
                   docs.toArray().then(function(docs) {
                     console.log("=====>", docs);
                     callback(docs);
                   });
                 });
  },

  async del_history_mutex(app, session, product_id = null,
                          callback = function(_) {}) {
    var query = {};
    if (product_id === null) {
      query = {session : session};
    } else {
      query = {session : session, product_id : product_id};
    }
    const history = app.locals.db.collection('history');
    history.deleteMany(query, function(err, docs) {
      console.log("[+] `history`: usuwam na zlecenie session=`" + session +
                  "`");
      callback(docs);
    });
  },

  async del_products(app, product_id = [], callback = function(_) {}) {
    const products = app.locals.db.collection('products');
    products.deleteMany({product_id : {$in : product_id}}, function(err, docs) {
      console.log("[+] `products`: usuwamy product_id=`" +
                  product_id.toString() + "`");
      callback(docs);
    });
  },

  async get_products(app, callback = function(_) {}) {
    const products = app.locals.db.collection('products');
    products.find({}).toArray(function(err, docs) {
      console.log(docs);
      callback(docs);
    });
  },
};

module.exports = funcs;
