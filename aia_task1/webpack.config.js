const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BrowserSyncPlugin = require('browser-sync-webpack-plugin');

// FIXME:
// node node_modules/node-sass/scripts/install.js

module.exports = {
    entry: [
        './assets/sass/index.scss'
    ],
    output: {
        path: __dirname + "/dist",
        filename: 'index.js'
    },
    module: {
        rules: [
            {
                test: /\.scss$/,
                exclude: /node_modules/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader'
                ]
            },
            {
                test: /\.(jpg|png|gif|woff|woff2|eot|ttf|svg)$/,
                loader: 'file-loader'
            }
        ]
    },
    watchOptions: {
        ignored: [
            /node_modules/,
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'index.css',
        }),
        new BrowserSyncPlugin({
            
            files: [
                'index.html',
                'assets/**/*.css'
            ],
            host: 'localhost',
            port: 3000,
            server: {
                baseDir: ['.']
            }
        })
    ]
};
