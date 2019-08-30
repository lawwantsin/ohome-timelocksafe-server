# Commands to move files onto the box and then ssh in to see what's up.

cd ~/Web/Box
scp -r static/* box:static/
scp JSONContent.py HTMLContent.py Hardware.py httpd.py box:~
ssh box
