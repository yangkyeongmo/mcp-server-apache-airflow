#!/bin/bash
#
# update-hosts.sh - Sync /etc/hosts with VPN-resolved internal hostname
#
# ============================================================================
# WHY THIS SCRIPT EXISTS
# ============================================================================
# When connected to a VPN, DNS resolution for internal hostnames (like
# pidgey.ready-internal.net) works through the VPN tunnel. However, some
# applications or system services may bypass VPN DNS and fail to resolve
# these internal addresses.
#
# This script resolves the hostname via VPN DNS (using nslookup) and writes
# the IP directly to /etc/hosts, ensuring all applications can reach the
# internal server regardless of their DNS configuration.
#
# ============================================================================
# WHO NEEDS THIS
# ============================================================================
# - Developers connecting to internal Airflow instances via VPN
# - Users experiencing intermittent DNS resolution failures on VPN
# - macOS users where split-tunnel VPN doesn't route DNS properly
# - Anyone needing reliable access to internal services with dynamic IPs
#
# ============================================================================
# USAGE
# ============================================================================
# One-time update (requires sudo for /etc/hosts):
#   sudo ./update-hosts.sh
#
# Automated updates via cron (every 30 minutes):
#   sudo crontab -e
#   # Add this line:
#   */30 * * * * /path/to/update-hosts.sh >> /var/log/hosts-update.log 2>&1
#
# ============================================================================

set -e

HOSTNAME="pidgey.ready-internal.net"

# Resolve hostname using VPN DNS (nslookup routes through VPN tunnel)
echo "Resolving $HOSTNAME via VPN DNS..."
NEW_IP=$(nslookup "$HOSTNAME" 2>/dev/null | grep -A1 "Name:" | grep "Address:" | awk '{print $2}')

if [ -z "$NEW_IP" ]; then
    echo "ERROR: Failed to resolve $HOSTNAME"
    echo "       Make sure you are connected to the VPN."
    exit 1
fi

echo "Resolved to: $NEW_IP"

# Check current entry
CURRENT_IP=$(grep "$HOSTNAME" /etc/hosts 2>/dev/null | awk '{print $1}' || true)

if [ "$CURRENT_IP" = "$NEW_IP" ]; then
    echo "No update needed - /etc/hosts already has correct IP."
    exit 0
fi

# Remove old entry and add new one
grep -v "$HOSTNAME" /etc/hosts > /tmp/hosts.tmp
echo "$NEW_IP $HOSTNAME" >> /tmp/hosts.tmp

# Update /etc/hosts (requires sudo)
mv /tmp/hosts.tmp /etc/hosts

echo "SUCCESS: Updated /etc/hosts"
echo "         $HOSTNAME -> $NEW_IP"
[ -n "$CURRENT_IP" ] && echo "         (was: $CURRENT_IP)"
