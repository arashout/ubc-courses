mkdir -p client_build

# yarn add typescript # Might need to run this the first time
yarn webpack
yarn bookmarklet client_build/bundle.js client_build/bookmarklet.js
python3 scripts/build_and_replace.py