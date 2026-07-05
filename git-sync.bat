@echo off
cd /d "C:\Users\sts\AOS\projects\Projekte-Claude\meetily-glm-bridge"

echo [1] Remote setzen...
git remote remove origin 2>nul
git remote add origin https://github.com/steffensoldan/claude.git

echo [2] Aenderungen committen...
git add .
git commit -m "feat: production deployment complete - autostart, real Meetily schema, network access, updated docs"

echo [3] Remote-Branch holen...
git fetch origin claude/open-router-aos-integration-827scj

echo [4] Pushen (force, da lokale History divergiert)...
git push origin HEAD:claude/open-router-aos-integration-827scj --force-with-lease

echo.
echo Fertig: https://github.com/steffensoldan/claude/tree/claude/open-router-aos-integration-827scj
pause
