# Commands to move files onto the box and then ssh in to see what's up.

cd ~/Web/Box
scp -r JSONContent.py HTMLContent.py Hardware.py httpd.py static box:~
