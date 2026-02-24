setup:
	docker-compose --project-directory . -f db/docker-compose.yml up -d

teardown:
	docker-compose --project-directory . -f db/docker-compose.yml down -v

clean:
	powershell -NoProfile -Command "$$paths = 'data/raw','data/curated','data/exports'; foreach ($$p in $$paths) { if (Test-Path $$p) { Get-ChildItem -Path $$p -File -Recurse | Remove-Item -Force } }"
