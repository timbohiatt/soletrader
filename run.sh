#Export the Local SoleTrader DB
pg_dump -Fc -h localhost -U svc_soletrader soletrader > soletrader.dump

#Set the GIT Comment from the CLI Argument.
GITComment="$1"

#Add Everything To Git.
git add . 
#Coomit the Git Changes
git commit -m "$GITComment" 
#Push the Git Chnages to the Master Heroku Branch and Deploy! 
git push heroku master


#Export Path Names for Flask App Before Executing
export FLASK_APP=btcMain.py
export FLASK_DEBUG=1
#Execute the Flask App
flask run



