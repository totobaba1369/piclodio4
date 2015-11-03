# How to use it :

# 1) Visit http://radio.fr
# 2) Find your radio
# 3) Use this script to find the http stream

# Examples :
# ./getStreamUrl europe1
# ./getStreamUrl fgunderground

curl -s http://$1.radio.fr/ | grep -Eo 'streamUrl":"[^"]*'|sed 's/streamUrl":"//'
