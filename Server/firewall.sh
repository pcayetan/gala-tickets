#!/bin/sh
### BEGIN INIT INFO
# Provides: firewall
# Required-Start:
# Required-Stop:
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Firewall
# Description: Firewall for eticket app
### END INIT INFO

# Redirects port 80 to 8080
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

