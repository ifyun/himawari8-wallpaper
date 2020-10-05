./clean.sh;
pipenv run pyinstaller -F -w ./src/himawari8.py -i ./assets/icon.ico;
if [ $? -eq 0 ]; then
    cp ./config.json ./dist
fi