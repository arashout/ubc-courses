mkdir -p build

# yarn add typescript # Might need to run this the first time
yarn webpack
yarn bookmarklet build/bundle.js build/bookmarklet.js
python3 scripts/build_and_replace.py