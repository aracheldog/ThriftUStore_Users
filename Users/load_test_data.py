import csv
import os

import django
from django import setup

# 设置 Django 的环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ThriftUStore_Users.settings")
django.setup()

# 初始化 Django 设置

from Users.models import User


csv_file_path = '../MOCK_DATA.csv'

with open(csv_file_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        full_name = row['full_name']
        avatar_url = row['avatar_url']
        email = row['email']
        password = row['password']
        address = row['address']
        zip_code = row['zip_code']
        state = row['state']
        country = row['country']
        description = row['description']
        print(full_name, avatar_url, email, password, address, zip_code, state, country, description)

        if not User.objects.filter(email=email).exists():

            User.objects.create_user(full_name=full_name,
                                avatar_url=avatar_url,
                                email=email,
                                password=password,
                                address=address,
                                zip_code=zip_code,
                                state=state,
                                country=country,
                                description=description)