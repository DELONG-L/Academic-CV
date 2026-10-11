.PHONY: all en zh check smoke pack clean

all:
	python3 scripts/build.py

en:
	python3 scripts/build.py --language en

zh:
	python3 scripts/build.py --language zh

check: all
	python3 scripts/check.py

smoke:
	python3 scripts/smoke.py

pack: all
	python3 scripts/pack.py

clean:
	python3 -c "from pathlib import Path; import shutil; p=Path('_build'); shutil.rmtree(p) if p.exists() else None"
