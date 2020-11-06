mkdir -p build

# yarn add typescript # Might need to run this the first time
yarn webpack
yarn bookmarklet build/bundle.js build/bookmarklet.js
python3 scripts/build_and_replace.py

aws s3 cp build/index.html s3://ubc-courses-frontend