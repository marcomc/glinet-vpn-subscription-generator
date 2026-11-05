#!/usr/bin/env bash
set -euo pipefail

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add -A README.md output reports/coverage.json
if git diff --cached --quiet; then
  exit 0
fi

: "${LISTS_DEPLOY_KEY:?LISTS_DEPLOY_KEY is required to publish changed subscriptions}"
umask 077
ssh_directory=$(mktemp -d)
trap 'rm -rf -- "${ssh_directory}"' EXIT
printf '%s\n' "${LISTS_DEPLOY_KEY}" > "${ssh_directory}/key"
unset LISTS_DEPLOY_KEY
# GitHub's published Ed25519 host key (never trust an unverified ssh-keyscan).
# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints
printf '%s\n' 'github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl' > "${ssh_directory}/known_hosts"
export GIT_SSH_COMMAND="ssh -i '${ssh_directory}/key' -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile='${ssh_directory}/known_hosts'"

git commit -m 'Update VPN subscription lists'
# Use SSH only for the write; the public checkout stays on HTTPS.
git push git@github.com:marcomc/glinet-vpn-subscription-lists.git HEAD:main
exit 0
