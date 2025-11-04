# Data Directory

This directory contains the blocklist files and audit logs for the Blocklist Platform.

## Files

- **ip-address-blocklist.txt**: Contains blocked IP addresses
- **domain-blocklist.txt**: Contains blocked domains
- **url-blocklist.txt**: Contains blocked URLs
- **blocklist-log.txt**: Audit log of all block/unblock actions

## Important Notes

1. These files are automatically created and managed by the application
2. Do not manually edit these files unless you know what you're doing
3. Regular backups of this directory are recommended
4. This directory is excluded from git by default (see .gitignore)

## Backup

To backup your blocklists and logs:

```bash
# Create a timestamped backup
tar -czf blocklist-backup-$(date +%Y%m%d-%H%M%S).tar.gz data/
```

## Restore

To restore from a backup:

```bash
# Extract backup (this will overwrite existing files)
tar -xzf blocklist-backup-YYYYMMDD-HHMMSS.tar.gz
```
