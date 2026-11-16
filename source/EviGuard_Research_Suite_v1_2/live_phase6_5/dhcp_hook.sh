#!/bin/sh
# udhcpc invokes this with deconfig/bound/renew. Record the actual callback.
case "$1" in
  deconfig)
    ip addr flush dev "$interface" scope global
    printf '{"kind":"deconfig","interface":"%s","origin":"udhcpc-hook"}\n' "$interface" >> "$EVIGUARD_EVENTS" ;;
  bound|renew)
    ip addr flush dev "$interface" scope global
    ip addr add "$ip/24" dev "$interface"
    printf '{"kind":"%s","interface":"%s","ip":"%s","origin":"udhcpc-hook"}\n' "$1" "$interface" "$ip" >> "$EVIGUARD_EVENTS" ;;
esac
