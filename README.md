# sound3d

sound3d is a Django app built to generate 3D STL files from sound files.
It utilizes OpenSCAD as the drawing tool.

Currenly, only the mp3 format type is supported.

## Set up

1. Start Django Project 

  ``` bash
  django-admin startproject sound3d_project
  cd sound3d_project
  ```

2. Clone the git repository

  ``` bash
  git clone https://github.com/cameronlai/sound3d
  ```
  
3. Edit settings.py in your project folder

  ``` bash
  cd ../sound3d_PROJECT
  nano settings.py
  ```

  > Add 'sound3d' in INSTALLED_APPS
  > Add 'sound3d/static/', in STATICFILES_DIR

4. Edit urls.py in your project folder 
  
  ``` bash
  nano urls.py
  ```

  > Add url(r'$^', include('sound3d.urls')), to urlpatterns
  

5. Run migrations with manage.py

  ``` bash
  cd ../
  sudo python manage.py migrate
  ```

## Running Django app

1. Run server

  ``` bash
  python manage.py runserver
  ```

2. Launch web browser, enter correct IP address (Default is 127.0.0.1:8000) and your app is running.

## Dependencies

- OpenSCAD

## License

The app is released under the MIT License and more information can be found in the LICENSE file.

## Contributions

sound3d is a project to generate interesting 3D shapes from sound file data. 
The output could then be be printed out with a 3D printer for visualization.

Contributions for new ideas and bug fixes are sincerely welcome!