## Image Repo
This image repository app was built for Shopify Backend Developer Intern Challenge.
####
<img src="https://github.com/elena-kolomeets/Django-Repo/blob/master/image-repo.PNG" width="400"/>

### What is it?
It's a special image storage. Apart from storing your images, it also analyzes them to extract image *description*, 
*tags* and *main colors*. This data can be used to ensure accessibility and enable quick searching and sorting of contents. 
### How to use it?
1. Open [Image Repo](https://image-repo-elena.herokuapp.com/) on desktop or mobile device.
2. Sign up, or sign in if you already have an account.
3. Upload an image. There is currently a limit of 5 uploads.
4. You will see your images, along with extracted information, sorted from new to old ones. 
5. Your data is still there if you sign out and come back :)

*Note: images larger than 4 MB will not be analyzed but will still be stored. (Third-party provider limitation.)*
####
<img src="https://github.com/elena-kolomeets/Django-Repo/blob/master/image-repo.gif" width="500"/>

### How does it work?
* Accounts are created if valid username and password are given. Sign-up page provides hints for choosing credentials
  and error messages when needed.
* Signed-in users can upload valid images that will be associated with their accounts (other users won't see them).
* The images are uploaded to a secure storage and encrypted.
* Upon uploading the images are analyzed to get image description, tags and dominant colors.
* Image paths and extracted data are stored in a secure database.
* Images are displayed with the help of temporary secure urls.

### How was it built?
#### Development
*Backend* was built with Python and Django, AWS S3 and PostgreSQL. 
The app utilizes Azure Computer Vision API to analyze images.

Although it's a backend developer challenge, some frontend was needed for usability.
Minimalistic but responsive *frontend* is based on HTML templates with internal CSS.

This stack was chosen to deliver a working product within a limited period of time as it provides some features out of 
the box and is familiar to the developer.
#### Testing
Tests were run locally before each push. Initial plan was to automate testing with GitHub Actions, 
but Postgres required user permission to create a database (a temporary one for testing), and Heroku free plan 
didn't allow altering user's permissions. Since both tools were already in use and no quick workarounds were found, 
it was decided to focus on development and run tests locally.
####
<img src="https://github.com/elena-kolomeets/Django-Repo/blob/master/tests.PNG" width="300"/>

#### Deployment
The app was deployed from GitHub directly to Heroku using Heroku Pipelines with automated deployment during development.
#### Security
S3 bucket has no public access; server-side encryption with SSE-S3 is enabled.
To view images in the app, presigned urls with expiration time of 30 min are generated. 
Connection to the bucket and database is established using SSL.
### What's next?
There is always room for improvement. Here is what could be done in the future:
* allow users to delete uploaded images;
* enable searching images by tags/description keywords/colors;
* resize big images to get over Azure API limits (but store original ones);
* enable sign-in with identity providers like Google or Facebook (OAuth 2.0 flow);
* increase test coverage and automate tests.
### Bonus for developers
To run the app locally and make changes, follow these steps:
* in a terminal open in a new folder run `git clone https://github.com/elena-kolomeets/Django-Repo.git` to get the source code;
* make sure you have Python 3.8 or later version;
* go to the project folder and install dependencies with `pip install requirement.txt`
* add `.env` file in `image_repo_project` folder (that contains `settings.py`) with the following contents: 
```
IMG_REPO_SECRET_KEY=your-django-secret-key
POSTGRES_PASSWORD=your-postgres-user-password
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_STORAGE_BUCKET_NAME='your-aws-storage-bucket-name
AZURE_CV_KEY=your-azure-computer-vision-key
AZURE_CV_ENDPOINT=your-azure-computer-vision-endpoint
```
* obviously you'll need to have these resources to use them, so go ahead and 
  * create an S3 bucket and user 
  with [right permissions](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#iam-policy); 
  * create a PostgreSQL database and user with permission to create databases (in psql: `ALTER USER <username> CREATEDB;`);
  * create a Computer Vision resource in Azure Portal.
* in `image_repo_project/settings.py` set DEBUG to `False` and make other necessary settings changes 
  (like using MEDIA_ROOT and MEDIA_URL settings for local media file uploads).
* run
  ```
  python manage.py makemigrations   # analyze models and create db commands
  python manage.py migrate          # apply changes to the database
  python manage.py collectstatic    # collect all static files in one dir
  python manage.py test             # run tests
  python manage.py createsuperuser  # get access to adminpanel
  python manage.py runserver        # start local server
  ```
___
If you have any questions/suggestions/remarks, don't hesitate to contact me [here](https://www.linkedin.com/in/elena-kolomeets-72063517a/) or via kolomeets.elena7@gmail.com.

Thanks for checking out Image Repo!:tada: