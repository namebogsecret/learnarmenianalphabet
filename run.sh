#!/usr/bin/env bash
set -euo pipefail

QUIET=0
NO_COLOR=""
PORT=8000
for arg in "$@"; do
  case "$arg" in
    --quiet) QUIET=1 ; shift ;;
    --no-color) NO_COLOR=1 ; shift ;;
    --port=*) PORT="${arg#*=}" ; shift ;;
    *) echo "Unknown option: $arg"; exit 1 ;;
  esac
done

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/run-$(date +'%Y%m%d_%H%M%S').log"
touch "$LOG_FILE"

print() {
  local lvl="$1"; shift
  local ts=$(date +"%F %T%z")
  local color="" reset=""
  if [[ -z $NO_COLOR ]]; then
    case "$lvl" in
      INFO) color="\e[32m";;
      WARN) color="\e[33m";;
      ERROR) color="\e[31m";;
    esac
    reset="\e[0m"
  fi
  if [[ $QUIET -eq 1 && "$lvl" == "INFO" ]]; then
    printf "%s [%s] %s\n" "$ts" "$lvl" "$*" >> "$LOG_FILE"
  else
    printf "%b%s [%s] %s%b\n" "$color" "$ts" "$lvl" "$*" "$reset" | tee -a "$LOG_FILE"
  fi
}

run_cmd() {
  local cmd="$1"
  print INFO "$cmd"
  bash -c "$cmd" 2>&1 | tee -a "$LOG_FILE"
  return ${PIPESTATUS[0]}
}

trap 'print ERROR "Aborted (signal)"; exit 2' INT TERM

run_cmd "git pull --ff-only"
if [[ $? -ne 0 ]]; then
  print ERROR "git pull failed"
  exit 1
fi

if [[ -f requirements.txt ]]; then
  run_cmd "python -m pip install -r requirements.txt"
  [[ $? -ne 0 ]] && { print ERROR "deps - pip install failed"; exit 1; }
elif [[ -f package.json ]]; then
  run_cmd "npm ci --ignore-scripts"
  [[ $? -ne 0 ]] && { print ERROR "deps - npm install failed"; exit 1; }
fi

status=1
if [[ -f start.sh ]]; then
  run_cmd "bash start.sh"; status=$?
elif [[ -f package.json && $(jq -r '.scripts.start // empty' package.json 2>/dev/null) ]]; then
  run_cmd "npm start"; status=$?
elif [[ -f main.py ]]; then
  run_cmd "python main.py"; status=$?
elif [[ -f index.html ]]; then
  if lsof -i :$PORT >/dev/null 2>&1; then
    pid=$(lsof -ti :$PORT)
    if [[ -n $pid ]]; then
      kill $pid && print WARN "Killed process on port $PORT"
    fi
  fi
  run_cmd "python -m http.server $PORT"; status=$?
else
  print ERROR "No start command found"
  exit 1
fi

if [[ $status -eq 0 ]]; then
  print INFO "✓ SUCCESS"
else
  print ERROR "✗ FAILED (code $status)"
fi

exit $status
