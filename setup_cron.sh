#!/usr/bin/env bash
# setup_cron.sh
# Installs a monthly cron job that runs mortgage_calculator.py on the 1st of
# each month at 09:00.  The script runs non-interactively using the last
# overpayment amount you entered interactively (saved to ~/.mortgage_overpayment).
#
# To set / update your overpayment amount run the calculator manually:
#   python3 mortgage_calculator.py
# or pass it directly:
#   python3 mortgage_calculator.py 350

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CALCULATOR="$SCRIPT_DIR/mortgage_calculator.py"
LOG_DIR="$HOME/mortgage_reports"
LOG_FILE="$LOG_DIR/cron.log"

# ── Pre-flight checks ─────────────────────────────────────────────────────────
if [[ ! -f "$CALCULATOR" ]]; then
  echo "ERROR: mortgage_calculator.py not found in $SCRIPT_DIR" >&2
  exit 1
fi

PYTHON=$(command -v python3 2>/dev/null || true)
if [[ -z "$PYTHON" ]]; then
  echo "ERROR: python3 not found on PATH" >&2
  exit 1
fi

echo "Python  : $PYTHON"
echo "Script  : $CALCULATOR"
echo "Log     : $LOG_FILE"
echo ""

# ── Verify the script runs ────────────────────────────────────────────────────
echo "Running a quick dry-run (overpayment = £0) to verify the script …"
mkdir -p "$LOG_DIR"
if "$PYTHON" "$CALCULATOR" 0 > /dev/null 2>&1; then
  echo "  ✓ Script executed successfully."
else
  echo "  ✗ Script failed – check for errors above before continuing." >&2
  exit 1
fi
echo ""

# ── Install cron entry ────────────────────────────────────────────────────────
MARKER="mortgage_calculator.py"

if crontab -l 2>/dev/null | grep -qF "$MARKER"; then
  echo "A cron entry already exists:"
  crontab -l | grep "$MARKER"
  echo ""
  read -rp "Replace it? [y/N] " answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    # Remove old entry then re-add
    ( crontab -l 2>/dev/null | grep -vF "$MARKER" ) | crontab -
  else
    echo "No changes made."
    exit 0
  fi
fi

CRON_LINE="0 9 1 * * mkdir -p \"$LOG_DIR\" && \"$PYTHON\" \"$CALCULATOR\" >> \"$LOG_FILE\" 2>&1"
( crontab -l 2>/dev/null; echo "$CRON_LINE" ) | crontab -

echo "Cron job installed successfully."
echo ""
echo "Schedule  : 1st of every month at 09:00"
echo "Command   : $PYTHON $CALCULATOR"
echo "Log file  : $LOG_FILE"
echo ""
echo "The job runs non-interactively using the overpayment saved in"
echo "~/.mortgage_overpayment.  To update that value, run:"
echo ""
echo "  python3 $CALCULATOR"
echo ""
echo "Reports are written to: $LOG_DIR/"
