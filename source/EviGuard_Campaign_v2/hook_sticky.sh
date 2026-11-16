#!/bin/sh
# udhcpc hook for a 'sticky' host: configures the address on bound/renew and KEEPS it on deconfig/release,
# modelling a host that continues to use its address after its authorization is revoked.
case "$1" in
  bound|renew) ip addr flush dev "$interface" scope global; ip addr add "$ip/24" dev "$interface" ;;
esac
exit 0
