#!/bin/zsh

cd "/Users/agvan/.codex/.chatgpt-projects/g-p-691ca0b6aafc8191b2970dc52cbc6877/guardian-editorial-analysis" || exit 1

BUNDLED_PYTHON="/Users/agvan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"

if [[ -x "$BUNDLED_PYTHON" ]]; then
  "$BUNDLED_PYTHON" download_guardian_data.py
elif command -v python3 >/dev/null 2>&1; then
  python3 download_guardian_data.py
else
  echo "Python could not be found. Ask Codex to run the Guardian downloader for you."
  exit 1
fi

STATUS=$?
echo
if [[ $STATUS -eq 0 ]]; then
  echo "Finished. Press Enter to close this window."
else
  echo "The download did not finish. Press Enter to close this window."
fi
read
exit $STATUS
