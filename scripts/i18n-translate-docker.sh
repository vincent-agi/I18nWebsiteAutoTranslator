#!/usr/bin/env bash
#
# Run i18n-translator in a single-use container (docker run --rm), mounting the
# working directory at /work, then optionally clean up the image and dangling
# layers it leaves behind.
#
# Examples:
#   DEEPL_API_KEY=xxx scripts/i18n-translate-docker.sh -- \
#     -s FR -t EN -i examples/fr.json -o examples/fr.en.json
#
#   # translate, then remove the pulled image and prune dangling layers
#   DEEPL_API_KEY=xxx scripts/i18n-translate-docker.sh --cleanup -- \
#     -s EN -t DE -i en.json -o de.json
#
set -uo pipefail

IMAGE="${I18N_TRANSLATE_IMAGE:-ghcr.io/vincent-agi/i18nwebsiteautotranslator:latest}"
WORKDIR="${I18N_TRANSLATE_WORKDIR:-$PWD}"
PULL="${I18N_TRANSLATE_PULL:-missing}"   # always | missing | never
RUN_AS_HOST_USER="${I18N_TRANSLATE_RUN_AS_HOST_USER:-1}"
CLEANUP=0

usage() {
  cat <<'EOF'
Usage: i18n-translate-docker.sh [options] -- <i18n-translate args>

Options:
  --cleanup           remove the image and run `docker image prune -f` after the run
  --pull POLICY       docker pull policy: always | missing | never   (default: missing)
  --root              run the container as its own non-root user instead of the
                      host uid/gid (output files will be owned by uid 10001)
  -h, --help          show this help

Environment:
  DEEPL_API_KEY                 forwarded into the container (required unless a
                               deepl-key.json sits in the mounted directory)
  I18N_TRANSLATE_IMAGE         image to run (default: ghcr.io/.../i18nwebsiteautotranslator:latest)
  I18N_TRANSLATE_WORKDIR       directory mounted at /work (default: current dir)
  I18N_TRANSLATE_PULL          default pull policy

Everything after `--` is passed verbatim to `i18n-translate` inside the container.
Paths in those args are resolved relative to /work (i.e. the mounted directory).
EOF
}

args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --cleanup) CLEANUP=1; shift ;;
    --pull)    PULL="${2:?--pull needs a policy}"; shift 2 ;;
    --root)    RUN_AS_HOST_USER=0; shift ;;
    -h|--help) usage; exit 0 ;;
    --)        shift; args=("$@"); break ;;
    *)         args+=("$1"); shift ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker not found in PATH" >&2
  exit 127
fi

if [ "${#args[@]}" -eq 0 ]; then
  usage >&2
  exit 2
fi

run_opts=(--rm --pull "$PULL" -e DEEPL_API_KEY -v "$WORKDIR:/work" -w /work)
if [ "$RUN_AS_HOST_USER" = "1" ] && command -v id >/dev/null 2>&1; then
  # Output files land owned by the caller, so cleanup needs no sudo.
  run_opts+=(--user "$(id -u):$(id -g)")
fi

docker run "${run_opts[@]}" "$IMAGE" "${args[@]}"
status=$?

if [ "$CLEANUP" = "1" ]; then
  echo "cleanup: removing $IMAGE and pruning dangling layers" >&2
  docker image rm "$IMAGE" >/dev/null 2>&1 || true
  docker image prune -f >/dev/null 2>&1 || true
fi

exit "$status"
