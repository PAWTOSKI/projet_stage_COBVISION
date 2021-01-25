PAUSE
rem Chemin d'accès aux binaires MySQL (en fonction de l'installation)
set mysql_bin=C:\UwAmp\bin\database\mysql-5.7.11\bin

rem Chemin d'accès au dossier de sauvegarde (en fonction de l'installation)
set dossier_sauvegarde=D:\stage\application\data

rem Voir secure/connect.inc.php
set dbHost=localhost
set dbDb=essai_cobtest_2
set dbUser=....(mettre ici l'identifiant utilisée pour accéder à l'application COBTEST)
set dbPass=...(mettre ici le mot de passe utilisée)


set fichier_sauvegarde=%dossier_sauvegarde%\%dbDb%_backup.sql

rem Création de la sauvegarde
"%mysql_bin%\mysqldump.exe" -h %dbHost% -u%dbUser% --databases %dbDb%  > %fichier_sauvegarde%
