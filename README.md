Lakukan command ini sebelum run:

```
## bebas di folder mana saja
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate

pip install -r requirements.txt

## di folder /task_management/ (yang ada manage.py nya)
python manage.py migrate

# buat super user (username & password bebas)
python manage.py createsuperuser

python manage.py runserver
```