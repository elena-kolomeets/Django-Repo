import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from .forms import ImageForm
from .models import Image


class ImageRepoTestCase(TestCase):
    def setUp(self):
        """Set up tests by creating an signing in a user and getting an image"""
        # create a temp dir to upload images
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        # upload images to a temp dir for tests
        Image.image.field.storage = FileSystemStorage(location=settings.MEDIA_ROOT)
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='Password')
        self.client.login(username='user1', password='Password')
        with open('image_repo/test_data/test.png', 'rb') as file:
            self.upload_image = SimpleUploadedFile('test.png', file.read())

    def tearDown(self):
        """Clean up resources from setup and tests"""
        # remove temp dir for uploaded images
        shutil.rmtree(settings.MEDIA_ROOT)

    # MODELS
    def test_save_image(self):
        """Test if uploaded image path is correct (models.save_image())"""
        new_img = Image.objects.create(image=self.upload_image, user=self.user1)
        self.assertEqual(new_img.image.url, '/user1/test.png')

    def test_image_create(self):
        """Test if Image instance is created (models.Image())"""
        new_img = Image.objects.create(image=self.upload_image, user=self.user1)
        new_img.save()
        self.assertIsInstance(new_img, Image)

    # FORMS
    def test_image_form(self):
        """Test if image form is valid (forms.ImageForm())"""
        form_data = {'image': self.upload_image}
        form = ImageForm(files=form_data)
        self.assertTrue(form.is_valid())

    # VIEWS
    # sign up
    def test_sign_up_success_view(self):
        """Test if user signed up successfully (views.user_sign_up())"""
        self.client.logout()
        # use valid username and password
        resp = self.client.post(reverse('signup'), {'username': 'newuser', 'password1': 'Newuserpass',
                                                    'password2': 'Newuserpass'})
        # make sure user is redirected to repo
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('repo'))

    def test_sign_up_fail_view(self):
        """Test if user couldn't sign up (views.user_sign_up())"""
        self.client.logout()
        # use invalid password (too short)
        resp = self.client.post(reverse('signup'), {'username': 'newuser', 'password1': 'pass',
                                                    'password2': 'pass'})
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.context['error'], 'Invalid username or password. Please choose another one.')
        # use invalid username (with '!')
        resp = self.client.post(reverse('signup'), {'username': 'newuser!', 'password1': 'Password',
                                                    'password2': 'Password'})
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.context['error'], 'Invalid username or password. Please choose another one.')
        # user different passwords
        resp = self.client.post(reverse('signup'), {'username': 'newuser', 'password1': 'pass1',
                                                    'password2': 'pass2'})
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.context['error'], 'Passwords do not match.')
        # user already exists
        resp = self.client.post(reverse('signup'), {'username': 'user1', 'password1': 'user1Pass',
                                                    'password2': 'user1Pass'})
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.context['error'], 'Username is already used. Please choose another one.')

    # sign in
    def test_sign_in_success_view(self):
        """Test if user signed in successfully (views.user_sign_in())"""
        self.client.logout()
        # existing user credentials (from setUp())
        resp = self.client.post(reverse('signin'), {'username': 'user1', 'password': 'Password'})
        # make sure user is redirected to repo
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('repo'))

    def test_sign_in_fail_view(self):
        """Test if user couldn't sign in (views.user_sign_in())"""
        self.client.logout()
        # non existing user credentials
        resp = self.client.post(reverse('signin'), {'username': 'someusername', 'password': 'Password'})
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.context['error'], 'Given username or password is incorrect.')

    # repo
    def test_redirect_unauth_view(self):
        """Test if unauthenticated user is redirected from views.repo()"""
        self.client.logout()
        resp = self.client.get(reverse('repo'))
        self.assertRedirects(resp, '/?next=/repo/')

    def test_auth_view(self):
        """Test if authenticated user can see views.repo()"""
        resp = self.client.get(reverse('repo'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'image_repo/repo.html')

    def test_auth_user_repo(self):
        """Test if user only sees their images (views.repo())"""
        # user1 uploads an image
        new_img = Image.objects.create(image=self.upload_image, user=self.user1)
        new_img.save()
        # check that user1 sees his data
        resp = self.client.get(reverse('repo'))
        # response context value of key 'images' (sent in views.repo())
        # should be the same as query set of user1
        self.assertQuerysetEqual(resp.context['images'], Image.objects.filter(user=self.user1))
        # create a second user who has no images
        self.client.logout()
        self.user2 = User.objects.create_user(username='user2', password='passworD')
        self.client.login(username='user2', password='passworD')
        # check that user2 sees only their data
        resp = self.client.get(reverse('repo'))
        self.assertQuerysetEqual(resp.context['images'], Image.objects.filter(user=self.user2))

    def test_image_upload(self):
        """Test if image gets uploaded in views.repo()"""
        resp = self.client.post(reverse('repo'), data={'image': self.upload_image})
        self.assertEqual(resp.status_code, 200)
