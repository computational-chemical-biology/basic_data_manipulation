#!/bin/bash
#https://stackoverflow.com/questions/44288901/how-to-force-docker-to-release-storage-space-after-manual-delete-of-file-in-volu

# Remove dead containers (and their volumes)
docker ps -f status=dead --format '{{ .ID }}' | xargs -r docker rm -v
# Remove dangling volumes
docker volume ls -qf dangling=true | xargs -r docker volume rm
# Remove untagged ("<none>") images
docker images --digests --format '{{.Repository}}:{{.Tag}}@{{.Digest}}' | sed -rne 's/([^>]):<none>@/\1@/p' | xargs -r docker rmi
# Remove dangling images
docker images -qf dangling=true | xargs -r docker rmi
# Remove temporary files
rm -f /var/lib/docker/tmp/*
