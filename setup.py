#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='shappno-vps',
    version='11.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask>=3.0.3',
        'Werkzeug>=3.0.3',
        'psutil>=5.9.0',
        'requests>=2.31.0',
        'gunicorn>=22.0.0',
        'GitPython>=3.1.40',
        'python-dotenv>=1.0.0',
        'Flask-SocketIO>=5.3.4',
        'Flask-CORS>=4.0.0',
        'Flask-Limiter>=3.5.0',
        'APScheduler>=3.10.4',
        'pyotp>=2.9.0',
        'qrcode>=7.4.2',
        'bcrypt>=4.1.0',
        'PyJWT>=2.8.0',
        'cryptography>=41.0.0'
    ],
)