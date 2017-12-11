
GITComment="$1"

git add . 
git commit -m "$GITComment" 
git push heroku master


export FLASK_APP=btcMain.py
export FLASK_DEBUG=1
flask run



