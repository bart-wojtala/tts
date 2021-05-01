set mypath=%cd%

if not exist %mypath%\data mkdir data
if not exist %mypath%\data\db mkdir data\db

cmd /k mongod --dbpath="%mypath%\data\db"