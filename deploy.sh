# Commands to move files onto the box and then ssh in to see what's up.

cd ~/Web/Box
scp -r static/* box:static/
# scp httpd.py JSONContent.py HTMLContent.py Hardware.py box:~
ssh box
