echo "Please enter the admin username"
read tval
echo "Please enter the admin email"
read tem
python manage.py createsuperuser --username=$tval --email=tem