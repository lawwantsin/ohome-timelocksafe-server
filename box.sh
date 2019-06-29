#!/bin/sh

# This file should be called via nohup and it's output already redirected to
# a log file, but near the end of this script we should still truncate that
# file periodically.


echo "$0: Bringing up wlan0" >&2
while ! ifconfig wlan0 172.16.0.1 netmask 255.240.0.0 broadcast 172.31.255.255 up ; do
    sleep 1
    echo "$0: Bringing up wlan0" >&2
done


while [[ -z "$(pidof hostapd)" ]]; do
    echo "$0: Starting hostapd." >&2
    /usr/local/bin/hostapd -B /usr/local/etc/hostapd.conf
    sleep 2  # Wait for hostapd to fail, if it is going to.
done


mkdir -p /var/lib/misc  # For dnsmasq.
while [[ -z "$(pidof dnsmasq)" ]]; do
    echo "$0: Starting dnsmasq." >&2
    /usr/local/sbin/dnsmasq -C /usr/local/etc/dnsmasq.conf
    sleep 1  # Wait for dnsmasq to fail, if it's going to.
done


echo "$0: Restarting SSH." >&2
/usr/local/etc/init.d/openssh restart


# We start this in the script, which should also start inotify.
/home/tc/restart-httpd.py-on-inotify.sh


# Loop until killed (this script doesn't exit),
# truncating the log file if it gets big.
while : ; do
    if [[ $(stat -c "%s" '/home/tc/box.log') -gt 200000 ]]; then
        >'/home/tc/box.log'
        echo "$0: Truncated the log." >&2
    else
        echo "$0: Not truncating the log since it is smallar than 200 kB." >&2
    fi

    # Sleep 1 to 6.2 days.
    sleep $(($RANDOM*15+43200))
done


# Should never get here, but it's still more correct to wait for all jobs.
kill $(jobs -p)
wait
