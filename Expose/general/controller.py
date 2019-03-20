import random
import uuid
from datetime import datetime
from django.core.mail import send_mail
from pymongo import MongoClient
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from bson.objectid import ObjectId

db = MongoClient('localhost', 27017).Expose
users = db.auth_user
confirmatory_code = db.confirmatory_code
career = db.career
post = db.post
reset = db.reset
domainName = '127.0.0.1:8000/'



class Registration:
    def __init__(self, POST):
        self.data = Data_Extraction().register(POST)
        self.CreateUser()

    def Emailing(self):
        data = Data_Extraction().code(_id=self.__str__())
        Queries(confirmatory_code).InsertOne(data=data)

        Email().send_confirmatory_code(recipient_email=self.data['Info']['email'],
                                       first_name=self.data['Info']['first_name'], code=data['code'])

    def CreateUser(self):
        User.objects.create_user(username=self.data['Info']['email'], email=self.data['Info']['email'],
                                 first_name=self.data['Info']['first_name'], last_name=self.data['Info']['last_name'],
                                 password=self.data['Info']['password'], is_active=False)
        print('it worked')

    def __str__(self):
        return Queries(users).FindOne(filter=Data_Extraction().objectID(email=self.data['Info']['email']))['_id']


class Confirmation:

    def __init__(self, POST, id):
        self.data = Data_Extraction().confirmation(POST=POST)
        self.id = id

    def Confirm(self):
        try:
            data = Queries(confirmatory_code).FindOne({'_id': ObjectId(self.id)})
            # print(data['code'])
            print(type(self.data['code']))
            print(type(self.data['code']))
            if str(data['code']) == self.data['code']:

                print('Successfully confirm')

                Queries(confirmatory_code).DeleteMany({'_id': ObjectId(self.id)})

                UserSettings(id=self.id).Activate()

                Queries(users).UpdateOne(filter={'_id': self.id}, update={'$set': {'privacy': 'Public'}}) # make account public after creating

                return True

            else:
                return False

        except:
            return False

    def Login(self, request):
        data = Queries(users).FindOne({'_id': ObjectId(self.id)})
        Login_C(request=request).Login()


class Data_Extraction:
    def __init__(self):
        pass

    def register(self, POST):
        return {

            "Info": {
                "first_name": POST.get('first_name'),
                "last_name": POST.get('last_name'),
                "email": POST.get('email'),
                "password": POST.get('password')
            },
            "careers": [],
        }

    def confirmation(self, POST):
        return {
            "code": POST.get('code'),
        }

    def password(self, POST):
        return {
            "password": POST.get('newPassword'),
        }

    def objectID(self, email):
        try:
            return {
                'email': email
            }
        except:
            return {}

    def code(self, _id):
        return {
            "code": Randomizer().code6(),
            "_id": ObjectId(_id)
        }

    def Career(self, POST):
        return {
            POST.get('name'):{

                "Basic_Information": {
                    "email": POST.get('email'),
                    "start": POST.get('start'),
                    "end": POST.get('end'),
                    "rating": int(POST.get('rating'))

                },

                "Contact": {
                    "address": POST.get('address'),
                    "city": POST.get('city'),
                    "country": POST.get('country'),
                    "postal_code": POST.get('postal_code'),
                },

                "message": POST.get('message'),
                "datetime_update":datetime.now()

            }
        }

    def Post(self, POST, id):
        return {
                "_id":ObjectId(POST.get("post_id")),
                "title":POST.get('title'),
                "email":POST.get('email'),
                "abstract": POST.get('abstract'),
                "question": POST.get('question'),
                "target":{
                    "category": POST.get('category'),
                    "filter": POST.get('filter')
                },
                "author":UserSettings(id=id).getEmail()['username'],
                "datetime_update": datetime.now()

        }

    def Review(self, POST, email, id):
        return {
            "comments":{
                id:{
                "email":email,
                "opinion":POST.get('opinion'),
                "identity": POST.get('identity'),
                "date_reviewed":datetime.now()
                }
            },
            "_id":ObjectId(POST.get('post_id'))
        }

    def Profile(self, POST):
        return {
            "first_name": POST.get('first_name'),
            "last_name":POST.get('last_name'),
            "email":POST.get('email'),
            "date_of_birth":POST.get('dob'),
            "current_organization":POST.get('current_organization'),
            "position":POST.get('position'),
            "address":POST.get('address'),
            "city":POST.get('city'),
            "country":POST.get('country'),
            "telephone":POST.get('telephone'),
            "bio":POST.get('bio')

        }

class Profile_C:

    def __init__(self, id):
        self.id = ObjectId(id)

    def SaveChanges(self, POST):
        data = Data_Extraction().Profile(POST=POST)
        filter = {'_id': self.id}
        Queries(users).UpdateOne(filter=filter, update={'$set':data})

    def GatherAll(self):
        # print(users.find_one({'_id':self.id}, {'id':0, '_id':0, 'password':0, 'is_superuser':0, 'is_active':0, 'is_staff':0, 'last_login':0, 'username':0, 'date_joined':0}))
        return users.find_one({'_id':self.id}, {'id':0, '_id':0, 'password':0, 'is_superuser':0, 'is_active':0, 'is_staff':0, 'last_login':0, 'username':0, 'date_joined':0})

    def Privacy(self):
        print(users.find_one({'_id':self.id}, {'_id':0, 'privacy':1}))
        if users.find_one({'_id':self.id}, {'_id':0, 'privacy':1})['privacy'] == 'Private':
            return Queries(users).UpdateOne(filter={'_id':self.id}, update={'$set': {'privacy':'Public'}})

        return Queries(users).UpdateOne(filter={'_id':self.id}, update={'$set': {'privacy':'Private'}})


class Queries:
    def __init__(self, collection):
        self.collection = collection

    def InsertOne(self, data):
        return self.collection.insert_one(data)

    def FindOne(self, filter):
        try:
            return self.collection.find_one(filter)
        except:
            return {}

    def DeleteMany(self, filter):
        try:
            return self.collection.delete_many(filter)
        except:
            return {}

    def ReplaceOne(self, filter, replacement):
        return self.collection.replace_one(filter=filter, replacement=replacement)


    def UpdateOne(self, filter, update):
            return self.collection.update_one(filter=filter, update=update)

    def UpdateOneUpsert(self, filter, update):
                return self.collection.update_one(filter=filter, update=update, upsert=True)


class Randomizer:
    def __init__(self):
        random.seed(a=uuid.uuid4())

    def code6(self):
        return int(random.random() * 1000000)

    def code4(self):
        return int(random.random() * 10000)


class Email:
    def __init__(self):
        self.sender = 'alberteinstein00592@gmail.com'

    def send_confirmatory_code(self, recipient_email, first_name, code):
        subject = 'Confirm your account'
        message = 'Dear ' + first_name + \
                  '\n\nThank you for creating an account with greyClassic.' \
                  '\n\nTo confirm your account, use the given confirmatory code:' \
                  '\n\n\t' + str(code) + '\n\n'

        send_mail(subject=subject, message=message, from_email=self.sender, recipient_list=[recipient_email])

    def send_forget_password(self, recipient_email, first_name, link):
        subject = 'Change password link'
        message = 'Dear ' + first_name + \
                  '\n\n I forgot my password.' \
                  '\n\nTo confirm your account, use the given confirmatory code:' \
                  '\n\n\t' + '<a href="' + link + '"> reset link</a>' + '\n\n'

        send_mail(subject=subject, message=message, from_email=self.sender, recipient_list=[recipient_email])


class Login_C:

    def __init__(self, request):
        self.user = authenticate(username=request.POST.get('email'), password=request.POST.get('password'))
        self.request = request

    def Login(self):
        if (self.user is not None) and self.user.is_active:
            login(self.request, self.user)
            id = Queries(users).FindOne({'email': self.request.POST.get('email')})['_id']
            return id.__str__()

        return False


class Logout_C:

    def __init__(self, request):
        logout(request=request)


class UserSettings:
    ''''this class is used to make settings to each user. This settings include creating a user, making the user active or deleting the user'''

    def __init__(self, id):
        self.id = ObjectId(id)

    def getEmail(self):
        return users.find_one({'_id':self.id}, {'username':1})

    def Activate(self):
        users.update_one({'_id': self.id}, {'$set': {'is_active': True}})

    def Deactivate(self):
        users.update_one({'_id': self.id}, {'$set': {'is_active': False}})

    def CreateUser(self, data):
        '''This has been done in the registration and so were going to use that to do it'''

    #         A user can only be added if only they register
    #         see the registration class to create a user

    def ChangePassword(self, password):
        email = Queries(reset).FindOne({'_id': self.id})['email']
        user = User.objects.get_by_natural_key(username=email)
        print(user.username)
        print(user.password)
        user.set_password(raw_password=password)
        user.save()
        print(user.password)
        return email


class ForgetPassword_controller:
    def __init__(self, email):
        self.email = email

    def ConfirmEmail(self):
        data = Queries(users).FindOne({'username': self.email})
        if data:
            self.confirm = data
        else:
            self.confirm = False

    def CreateLink(self, ):
        Queries(reset).InsertOne({'email': self.email})
        link = Queries(reset).FindOne({'email': self.email})['_id']
        self.link = domainName + 'resetPassword/' + link.__str__()

    def SendMail(self):
        self.ConfirmEmail()
        if self.confirm:
            self.CreateLink()
            Email().send_forget_password(recipient_email=self.email, first_name=self.confirm['first_name'],
                                         link=self.link)

        else:
            pass

    def DeleteLink(self):
        Queries(reset).DeleteMany({'email': self.email})


class Reset_controller:
    def __init__(self, id):
        self.id = id

    def id_checker(self):
        if Queries(reset).FindOne({'_id': ObjectId(self.id)}):
            return True
        else:
            return False

    def SetPassword(self, POST):
        password = Data_Extraction().password(POST)['password']
        email = UserSettings(id=self.id).ChangePassword(password=password)
        ForgetPassword_controller(email=email).DeleteLink()


class Career_C:

    def __init__(self, id):
        self.id = ObjectId(id)


    def GatherAll(self):
        return list(career.find({'_id': self.id}, {'_id':0}))


    def SaveChanges(self, POST):
        data = Data_Extraction().Career(POST=POST)
        filter = {'_id': self.id}
        Queries(career).UpdateOne(filter=filter, update={'$set':data})


    def Delete(self, name):
        Queries(career).UpdateOne(filter={'_id': self.id}, update={'$unset':{name: 1}})


    def AddOne(self, POST):
        data = Data_Extraction().Career(POST)
        Queries(career).InsertOne(data=data)

class Post_C:

    def __init__(self, id):
        self.id = ObjectId(id)


    def GatherAll(self):
        return list(post.find({'author': self.id}))


    def SaveChanges(self, POST):
        data = Data_Extraction().Post(POST=POST, id=self.id)
        filter = {'_id': data['_id']}
        if data['_id']:
            Queries(post).UpdateOne(filter=filter, update={'$set':data})

        else:
            data.pop('_id')
            Queries(post).InsertOne(data=data)

    # delete the whole post with its associated comments.
    def DeletePost(self):
        filter = {'_id': self.id}
        Queries(post).DeleteMany(filter=filter)


class Review_C:

    def __init__(self, id):
        self.email = UserSettings(id=id).getEmail()['username']
        self.id = id



    def GatherAll(self):

        return list(post.find({'comments.'+self.id:{'$exists':True}},
                              {'comments.'+self.id:1, 'email':1, 'title':1, 'question':1, 'abstract':1, 'author': 1 , 'comments.'+self.id:1}))


    def SaveChanges(self, POST):
        data = Data_Extraction().Review(POST=POST, email=self.email, id=self.id)
        print(POST.get('identity'))
        filter = {'_id':data['_id']}#, 'comments':self.email} #id- question id not person's id
        data.pop('_id')

        Queries(post).UpdateOne(filter=filter, update={'$set':data})

    # delete the whole post with its associated comments.
    def DeleteComment(self, email):
        filter = {'_id': self.id, 'comments':email}
        Queries(post).DeleteMany(filter=filter)

