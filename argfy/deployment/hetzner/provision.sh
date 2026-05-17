#!/usr/bin/env bash
set -euo pipefail

[[ $EUID -ne 0 ]] && { echo "Run as root"; exit 1; }
. /etc/os-release
[[ "$VERSION_ID" != "24.04" ]] && echo "Warning: tested on Ubuntu 24.04, got $VERSION_ID"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y upgrade
apt-get -y install \
    ufw fail2ban unattended-upgrades \
    curl wget git jq htop ncdu vim tmux \
    ca-certificates gnupg lsb-release \
    postgresql-client-16

timedatectl set-timezone UTC

if [[ ! -f /swapfile ]]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    sysctl vm.swappiness=10
    echo 'vm.swappiness=10' > /etc/sysctl.d/99-swappiness.conf
fi

SSHD=/etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' $SSHD
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/'   $SSHD
sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/'      $SSHD
systemctl reload ssh

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force enable

systemctl enable --now fail2ban
dpkg-reconfigure -f noninteractive unattended-upgrades

if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker is not installed. Is Coolify installed?"
    exit 1
fi

mkdir -p /backups/postgres
chown root:root /backups
chmod 700 /backups

cat > /usr/local/bin/argfy-pgbackup.sh <<'BACKUP'
#!/usr/bin/env bash
set -euo pipefail
TS=$(date -u +%Y%m%d_%H%M%S)
OUT=/backups/postgres/argfy_${TS}.sql.gz
CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'argfy.*postgres' | head -1)
[[ -z "$CONTAINER" ]] && { echo "No postgres container found"; exit 1; }
docker exec "$CONTAINER" pg_dump -U argfy -d argfy | gzip > "$OUT"
find /backups/postgres -name "argfy_*.sql.gz" -mtime +7 -delete
echo "[$(date -u +%FT%TZ)] Backup OK: $OUT ($(du -h "$OUT" | cut -f1))"
BACKUP
chmod +x /usr/local/bin/argfy-pgbackup.sh

cat > /etc/cron.d/argfy-backup <<'CRON'
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
0 6 * * * root /usr/local/bin/argfy-pgbackup.sh >> /var/log/argfy-backup.log 2>&1
CRON

echo ""
echo "VPS provisioned."
echo "  Coolify admin:  http://$(curl -s ifconfig.me):8000"
echo "  Backups cron:   0 6 * * * -> /backups/postgres/"
echo ""
