See:  http://forum.tinycorelinux.net/index.php?topic=21821.0
See:  https://github.com/BertoldVdb/sdtool/


#set copy flag
>/mnt/mmcblk0p2/tce/copy2fs.flg
sudo reboot


#get the SD locker tool
wget "https://github.com/BertoldVdb/sdtool/blob/master/static/arm-sdtool?raw=true" -O arm-sdtool
chmod +x arm-sdtool
sudo ./arm-sdtool /dev/mmcblk0 status


#unmount data partition after extensions are loaded
echo umount /mnt/mmcblk0p2 >> /opt/bootlocal.sh
filetool.sh -bv


#remaster the core to mount the data partition read-only
sudo mount /dev/mmcblk0p1
cd ~
sudo mkdir extract
cd extract
zcat /mnt/mmcblk0p1/9.0.3v7.gz | sudo cpio -i -H newc -d
sudo sed -i -e 's#OPTIONS="noauto,users,exec"#OPTIONS="ro,noload,noauto,users,exec"#g' ./usr/sbin/rebuildfstab
sudo find | sudo cpio -o -H newc | gzip --best > ../9.0.3v7.gz
sudo cp -f ../9.0.3v7.gz /mnt/mmcblk0p1/9.0.3v7.gz && rm ../9.0.3v7.gz
sudo rm -f -r ~/extract/*
zcat /mnt/mmcblk0p1/9.0.3.gz | sudo cpio -i -H newc -d
sudo sed -i -e 's#OPTIONS="noauto,users,exec"#OPTIONS="ro,noload,noauto,users,exec"#g' ./usr/sbin/rebuildfstab
sudo find | sudo cpio -o -H newc | gzip --best > ../9.0.3.gz
sudo rm /mnt/mmcblk0p1/9.0.3.gz
sudo cp -f ../9.0.3.gz /mnt/mmcblk0p1/9.0.3.gz && rm ../9.0.3.gz
sudo rm -f -r ~/extract/*
cd ..
rmdir extract
sudo umount /mnt/mmcblk0p1


#lock the SD card
sudo umount /mnt/mmcblk0p2
sudo ./arm-sdtool /dev/mmcblk0 lock
#sudo reboot or just pull the power plug...


#making changes after you locked it read-only
sudo ./arm-sdtool /dev/mmcblk0 unlock
mount /mnt/mmcblk0p2
sudo mount -o remount,rw /mnt/mmcblk0p2
#now make the change
filetool.sh -bv
sudo umount /mnt/mmcblk0p2
sudo ./arm-sdtool /dev/mmcblk0 lock
