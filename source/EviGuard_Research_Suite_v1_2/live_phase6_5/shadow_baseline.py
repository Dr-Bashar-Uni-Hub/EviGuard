"""Independent matched-snapshot temporal reference for LIVE observations.
No epoch information exists in these observations, so this is NOT a versioned-fencing implementation.
"""
class SnapshotTemporalReference:
    def evaluate(self, snapshot):
        event=snapshot.get('last_event') or {}
        if event.get('kind') not in ('bound','renew'):
            return False
        if event.get('ip') != snapshot.get('ip'):
            return False
        channels=('lease_present','ip_present','arp_present')
        for name in channels:
            if snapshot.get(name) is not True:
                return False
        return True
