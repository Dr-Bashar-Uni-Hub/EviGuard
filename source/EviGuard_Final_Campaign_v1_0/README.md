# EviGuard final bounded campaign v1.0

Read `PROTOCOL.md` first. This package executes a deterministic **offline** failure model using the frozen v1.2 results archive for provenance checks. It does NOT inject real Linux faults. It does not modify the frozen archive.

Run on Ubuntu (no sudo required):

```bash
cd ~/EviGuard_Final_Campaign_v1_0
bash run.sh ~/EviGuard_Research_v1_2/EviGuard_v1_2_Results_20261109T200649Z.tar.gz
```

Adjust the archive path to where you actually saved the original results. Find it with:
`find ~ -name 'EviGuard_v1_2_Results_20261109T200649Z.tar.gz' -print`

Outputs are timestamped `results/` and a `.tar.gz` archive. Send that archive back for review. Do not call the offline PASS a kernel validation.
