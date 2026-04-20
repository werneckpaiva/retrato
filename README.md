[![CI](https://github.com/werneckpaiva/retrato/actions/workflows/ci.yml/badge.svg)](https://github.com/werneckpaiva/retrato/actions/workflows/ci.yml)

Retrato
=======

Perfect balanced Photo Album with admin.

Features
--------
- Perfect balance pictures in the page (http://werneckpaiva.github.io/retrato-js/)
- Ajax-based album browsing with push state
- Dynamic image resizing
- Real-time responsive
- Auto-rotate based on exif orientation
- Admin 
- Album share link 

Inspired by the project http://www.chromatic.io/

Requirements:
-------------
- Django==1.6.2
- Pillow==2.3.0
- django-jasmine==0.4.1

Installation & Build:
-------------
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install and build frontend assets:
```bash
npm install
npm run build
```


Google Drive:
-------------

Find the root folder id. Open the folder in the google drive and look for the id on the path:
https://drive.google.com/drive/u/0/folders/<folderid>

Docker
------
```
docker build -t retrato-app .
docker run -d -p 8000:8000 retrato-app
```

