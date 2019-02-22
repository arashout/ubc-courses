const path = require('path');

module.exports = {
    entry: './client/index.ts',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'client_build')
    },
    resolve: {
        // Add `.ts` and `.tsx` as a resolvable extension.
        extensions: [".ts", ".tsx", ".js"]
    },
    module: {
        rules: [
            // all files with a `.ts` or `.tsx` extension will be handled by `ts-loader`
            {
                test: /\.tsx?$/,
                loader: "ts-loader"
            }
        ]
    },
    mode: 'production',
};