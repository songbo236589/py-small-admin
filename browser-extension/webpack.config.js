const { merge } = require('webpack-merge');
const { commonConfig } = require('./webpack.common.js');

const config = merge(commonConfig, {
  mode: 'development',
  devtool: 'inline-source-map',
  optimization: {
    minimize: false,
  },
});

module.exports = config;
