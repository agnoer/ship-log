#!/usr/bin/env bash
# Push ship-log ke GitHub + bikin repo public kalau belum ada.
# Pakai: ./push.sh <PAT>   (classic token, scope: repo)
set -euo pipefail

TOKEN="${1:-${GITHUB_TOKEN:-}}"
[ -z "$TOKEN" ] && { echo "usage: ./push.sh <PAT>"; exit 1; }

cd "$(dirname "$0")"

USER=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/user \
  | python3 -c 'import sys,json;print(json.load(sys.stdin).get("login",""))')
[ -z "$USER" ] && { echo "token invalid"; exit 1; }
echo "login sebagai: $USER"

REPO="ship-log"

CODE=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$USER/$REPO")
if [ "$CODE" = "404" ]; then
  curl -s -X POST -H "Authorization: token $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO\",\"description\":\"Daily ship log\",\"private\":false}" \
    | python3 -c 'import sys,json;d=json.load(sys.stdin);print("created:",d.get("html_url",d))'
else
  echo "repo sudah ada, lanjut push"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "https://$USER:$TOKEN@github.com/$USER/$REPO.git"
git push -u origin main

git remote set-url origin "https://github.com/$USER/$REPO.git"
echo "selesai: https://github.com/$USER/$REPO"
