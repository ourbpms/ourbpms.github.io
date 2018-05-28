from django.views.generic import TemplateView, UpdateView
from django.http import HttpResponse
from django.shortcuts import render, redirect
import pyrebase

from firebase import firebase
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from djexmo import send_message
from django.views.decorators.cache import cache_control
from django.core.cache import cache
from django.core.paginator import Paginator
now = " "
ses = " "
DoctorName = " "              #name
## ernie
# email1 = " "          #unused
uid = " "
tok = " "
## PassedPatientId = " "   #datt
PatientId = " "         #datt1
## ernie
# datt = " "
# datt1 = " "

### notes
# renamed "fav_color" to SessionStart
# renamed "did" to SortedAccountInformationList
# renamed "li" to AccountInformationList
# renamed "det" to UserInfoDictionary
### end notes

config = {          ## initial configurations
    'apiKey': "AIzaSyCwy2DSVWgniTi2PRbHlDKvF58dzE5LhmY",
    'authDomain': "thesisbpms-af272.firebaseapp.com",
    'databaseURL': "https://thesisbpms-af272.firebaseio.com",
    'projectId': "thesisbpms-af272",
    'storageBucket': "thesisbpms-af272.appspot.com",
    'messagingSenderId': "789763107091"
 }


firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
db = firebase.database()
sto = firebase.storage()

#this function is used for calling the landing page
def home(request):  ### okay na
    return render(request, 'index.html')

# this is a dummy landing page
## needed ni para maka log in ##
def home_log(request):  ### okay na
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
    return render(request, 'home_log.html', {'n':DoctorName} )

# this function calls for login page
def LoginForm(request): ## SignInForm   ### okay na
    return render(request,'form_login.html')

# this function calls sign in functionalities 
def Login(request):    ## SignIn
#   -- fetch email address and password --  #
    email=request.POST.get('email')
    passw = request.POST.get("pass")
#   -- check and authenticate if email and password match and if account is valid --    #
    try:
        user = authe.sign_in_with_email_and_password(email,passw)
    except:
        message = "Invalid Credentials" 
        return render(request,"form_login.html",{"m":message})
#   -- if verified, fetch local id and token -- #
    uid = user['localId']
    tok = user['idToken']
#   -- session starts --    #
    request.session['SessionStart'] = str(uid)
    ses = request.session['SessionStart']
#   -- using the token, fetch user information and store in AccountInformation -- #
    AccountInformation = authe.get_account_info(tok)
#   -- stores fetched user information in an array and sorts them in descending order --    #
    AccountInformationList = [] 
    for key,value in AccountInformation.items(): 
        AccountInformationList.append(tuple((key,value))) 
    AccountInformationList.sort(reverse = True) 
#   -- stores only items in 2nd place from the AccountInformationList --    #
#   -- contains information such as local id, email, password hash, email verified,
#      password updated at, provider user info: (provider id, federated id, email, raw id),
#      valid since, last login at, created at, identity toolkit --  #
#   -- the sorted values are displayed in a matrix? style --    #
    f = [y[1] for y in AccountInformationList]
    sorted(str(f))
#   -- same function with the previous operation. i do not clearly understand this one --   #
#   -- contains local id, email, password hash, email verified, password updated at,
#      provider user info:(provider id, federated id, email, raw id), valid since,
#      last login at, created at, i --  #
    g = [g[0] for g in f]
    sorted(str(g))
    SortedAccountInformationList = list(g)[0]
#   -- transfers information from sorted AccountInformationList1 to account info list array -- #
    AccountInformationList1 = []
    for key,value in SortedAccountInformationList.items():
        AccountInformationList1.append(tuple((key,value)))
        AccountInformationList1.sort(reverse = True)
#   -- stores the 6th element from AccountInformationList1 to account info AccountInformationList2  - #
#   -- 6th element is the EmailVerified --  #
    AccountInformationList2 = []
    AccountInformationList2 = AccountInformationList1[6]
#   -- fetch 2nd place value from AccountInformationList2 which is either true or false -- #
    CheckEmail = str(list(AccountInformationList2)[1])

    if CheckEmail == 'False':
        EmailVerifyMsg = "You need to verify your email first. Redirecting you to Homepage"
        return render(request,'index.html', {'m':EmailVerifyMsg})

    SuccessMsg = "Login Successful!"
    HttpResponse(SuccessMsg)
#   -- contains doctor input data with labels -- #
    UserInfoDictionary = db.child("users").child("doctor").child(ses).get().val()
#   -- sorts data in descending order and stores it in lis --   #
    lis = []
    for key,value in UserInfoDictionary.items():
        lis.append(tuple((key, value)))
    lis.sort(reverse=True)
#   -- filters the data from lis. only accesses the doctor data without the labels --   #
    DoctorInformation = [x[1] for x in lis]
#   -- access doctor first name --  #
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
#   -- access doctor profile picture??? -- #
    DoctorImage = db.child("users").child("profilepic").child(ses).child("link").get().val()
    if DoctorImage is None:
        checklicnum = db.child("users").child("doctor").shallow().get().val()
        print("This is check license num in if")
        print (checklicnum)
        return render(request, "dash.html", {'dab':DoctorInformation, 'n':DoctorName, "docID":ses})
    else:
        picc = []
        for ka,va in DoctorImage.items():
            picc.append(tuple((ka, va)))
        print("This is picc")
        print (picc)
        l = [x[1] for x in picc]
        print("This is l")
        print (l)
        DoctorImage = l
        checklicnum = db.child("users").child("doctor").shallow().get().val()
        print("This is check license num in else")
        print (checklicnum)
        return render(request, "dash.html", {'dab':DoctorInformation,'p':DoctorImage, 'n':DoctorName})

def RegistrationForm(request):    ## signupForm     ### okay na
    return render(request,'register.html')

def Register(request):    ## signuppost
    famName = request.POST.get('famName')
    firstName = request.POST.get('firstName')
    gender = request.POST.get("gender")
    birthdate = request.POST.get("birthdate")
    email = request.POST.get('email')
    passw = request.POST.get('password')
    conf_pass = request.POST.get('conf_password')
    address = request.POST.get("address")
    num = '+63' + str(request.POST.get("mobileNum"))
    MS=request.POST.getlist('MS')
    lNum = request.POST.get("lNum")
    fullname = {
        'lastName': famName,
        'firstname': firstName
    }
###Firebase init
### somewhat needed kay mu email address already registered siya if wala
    config = {
        'apiKey': "AIzaSyCwy2DSVWgniTi2PRbHlDKvF58dzE5LhmY",
        'authDomain': "thesisbpms-af272.firebaseapp.com",
        'databaseURL': "https://thesisbpms-af272.firebaseio.com",
        'projectId': "thesisbpms-af272",
        'storageBucket': "thesisbpms-af272.appspot.com",
        'messagingSenderId': "789763107091"
      }
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
#   -- validation of password --    #

    if(passw != conf_pass):
        ErrorMsg = "Passwords do not match"
        return render(request, "register.html",{'m':ErrorMsg})
#   -- verification of licenseNum --    #
    checklicnum = db.child("users").child("doctor").shallow().get().val()
    if checklicnum is None:
        try:
            user = auth.create_user_with_email_and_password(email,passw)
        except:
            ErrorMsg = "Email Address Already Registered"
            return render(request, "register.html", {'m':ErrorMsg})
        print (user)
        uid = user['localId']
        tok = user['idToken']
        users_ref = db.child("users").child("doctor").child(uid)
        sendemail = auth.send_email_verification(tok)
        users_ref.set({
        'email': email,
        'fullname': fullname,
        'address': address,
        'gender' : gender,
        'contactNo' : num,
        'birthDate' : birthdate,
        'medicalSpecialization' : MS,
        'LicenseNum': lNum,
        'status': "1",
        })

        SuccessMsg  = "Account Created Successfully"
        HttpResponse(SuccessMsg)
        return render(request, "verify.html",{"e":email,'m':SuccessMsg})
    else:
        lis=[]
        for x in checklicnum:
#   -- access license numbers in database and compare if it matches the input --    #
            j = db.child("users").child("doctor").child(x).child("LicenseNum").get().val()
            if j == lNum:
                ErrorMsg = "Duplicate License Number!"
                return render(request, "register.html", {'m':ErrorMsg})
        try:
            user = auth.create_user_with_email_and_password(email,passw)
        except:
            ErrorMsg = "Email Address Already Registered"
            return render(request, "register.html", {'m':ErrorMsg})
        print (user)
        uid = user['localId']
        tok = user['idToken']
        users_ref = db.child("users").child("doctor").child(uid)
        sendemail = auth.send_email_verification(tok)
        users_ref.set({
        'email': email,
        'fullname': fullname,
        'address': address,
        'gender' : gender,
        'contactNo' : num,
        'birthDate' : birthdate,
        'medicalSpecialization' : MS,
        'LicenseNum': lNum,
        'status': "1",
        })

        SuccessMsg  = "Account Created Successfully"
        HttpResponse(SuccessMsg)
        return render(request, "verify.html",{"e":email,'m':SuccessMsg})
        

def DoctorDashboard(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
    else:
        print ("No Session")
        return redirect('/SignIn')
#   -- access doctor information from database --   #
    try:
        UserInfoDictionary = db.child("users").child("doctor").child(ses).get().val()
    except:
        return render(request,"index.html")

#   -- -- filters the data from UserInfoDictionary. only accesses the doctor data without the labels --   #
    List = []
    for key,value in UserInfoDictionary.items():
        List.append(tuple((key, value)))
    List.sort(reverse=True)
    DoctorInformation = [x[1] for x in List]

    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
    DoctorImage = db.child("users").child("profilepic").child(ses).child("link").get().val()
    if DoctorImage is None:
        return render(request, "dash.html", {'dab':DoctorInformation, 'n':DoctorName})
    else:
        AccessImage = []
        for ka,va in DoctorImage.items():
            AccessImage.append(tuple((ka, va)))

        DoctorImage = [x[1] for x in AccessImage]

        if 'patientdash_session' in request.session:
            del request.session['patientdash_session']
            request.session.modified = True
        return render(request, "dash.html", {'dab':DoctorInformation,'p':DoctorImage, 'n':DoctorName})

def notif(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()

        if 'patientdash_session' in request.session:
            del request.session['patientdash_session']
            request.session.modified = True

        return render(request, "notif.html", {'n':DoctorName})
    else:
        print ("No Session")
        return redirect('/SignIn')


def AddPatientForm(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    if 'SessionStart' not in request.session:
        return redirect('/SignIn')
    else:
        return render(request, "add.html", {'n':DoctorName})

def AddPatient(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    import time
    import pytz
    from datetime import datetime, timezone
    tz = pytz.timezone('Asia/Manila')
    utc_dt = datetime.now(timezone.utc).astimezone(tz)
    millis = int(time.mktime(utc_dt.timetuple()))


    famName = request.POST.get('famName')
    firstName=request.POST.get('firstName')
    email = request.POST.get('email')
    address = request.POST.get("address")
    num = '+63' + str(request.POST.get("mobileNum"))
    gender = request.POST.get("gender")
    birthdate = request.POST.get("birthDate")
    btype = request.POST.get('btype')
    hours = request.POST.get('fHours')
    minutes = request.POST.get('fMinutes')
    seconds = request.POST.get('fSecs')
    
    fullname = {
        'lastName': famName,
        'firstname': firstName
    }

    frequency = {
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }

    qrData = {
        'patientID': millis,
        'frequency': frequency
    }

    users_ref = db.child("users").child("patient").child(ses).child(millis)
    users_ref.set({
            'fullname':fullname,
            'email':email,
            'address':address,
            'contactNo': num,
            'bloodType': btype,
            'gender':gender,
            'birthDate':birthdate,
            })
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
    SuccessMsg = "Patient Created Successfully. Redirecting you to Pairing of BP Device"
    return render(request, "qrgen.html", {'n':DoctorName, 'qrData':qrData, 'm':SuccessMsg, 'f':fullname})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def PatientDashboard(request):
        print ("PATIENT ID")
        if 'SessionStart' in request.session:
            ses = request.session['SessionStart']
            print (ses)
        else:
            print ("No Session")
            return redirect('/SignIn')

        if 'patientdash_session' not in request.session:
            return redirect('/vform')
        else:
            tell = request.GET.get('z')
            PatientId = tell.split('-')[0]

            request.session['my_pat'] = PatientId
            StoredData = db.child("users").child("patient").child(ses).child(PatientId).get().val()
            print ("this is Stored Patient Data")
            print (StoredData)

            SortedPatientData = []
            for key,value in StoredData.items():
                SortedPatientData.append(tuple((key, value)))
            SortedPatientData.sort(reverse=True)
            print ("this is leb")
            print (SortedPatientData)
## ernie
    ### i don't think this is necessary
            # b = len(leb)
            # print ("this is b")
            # print (b)

            PatientData = [x[1] for x in SortedPatientData]
            print ("this is g")
            print (PatientData)
            da = PatientData
            pic = db.child("users").child(ses).child("link").child("patient").child(PatientId).get().val()
            print ("this is pic")
            print (pic)
            PatientBPReading = db.child("users").child("data").child(ses).child(PatientId).child("BPdata").shallow().get().val()
## ernie
            # pic = db.child("users").child(ses).child("link").child("patient").child(PassedPatientId).get().val()
            # print ("this is pic")
            # print (pic)
            # ler = db.child("users").child("data").child(ses).child(PassedPatientId).child("BPdata").shallow().get().val()
            print ("this is PatientBPReading")
            print (PatientBPReading)
            DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
            print ("this is DoctorName")
            print (DoctorName)

            if PatientBPReading is None:
                if pic is None:
                    if 'patientdash_session' not in request.session:
                        return redirect('/SignIn')
                    else:
                        return render(request, "patientdash.html", {'da':da,'s':ses, 'd':PatientId, 'n':DoctorName})
## ernie
                        # return render(request, "patientdash.html", {'da':da,'s':ses, 'd':PassedPatientId, 'n':name})
                else:
                    picc = []
                    for ka,va in pic.items():
                        picc.append(tuple((ka, va)))
                    l = [x[1] for x in picc]
                    print ("this is l in else")
                    print (l)
                    pic = l

                    if 'patientdash_session' not in request.session:
                        return redirect('/SignIn')
                    else:
                        return render(request, "patientdash.html",{'n':DoctorName, 'da':da,'s':ses, 'd':PatientId})
## ernie
                        # return render(request, "patientdash.html",{'n':name, 'da':da,'s':ses, 'd':PassedPatientId})
            op = []
            for i in PatientBPReading:
                op.append(str(i))
                op.sort()
            print ("this is op")
            print (op)
            qo = []
            for a in op:
                Systolic = db.child("users").child("data").child(ses).child(PatientId).child("BPdata").child(a).child("syst").get().val()
                Diastolic = db.child("users").child("data").child(ses).child(PatientId).child("BPdata").child(a).child("dias").get().val()
## ernie
                # jj = db.child("users").child("data").child(ses).child(PassedPatientId).child("BPdata").child(a).child("syst").get().val()
                # jk = db.child("users").child("data").child(ses).child(PassedPatientId).child("BPdata").child(a).child("dias").get().val()
                BPReading = str(Systolic)+ " " + str(Diastolic)
                qo.append(str(BPReading))
                print ("this is qo")
                print (str(qo))
            if pic is None:
                return render(request, "patientdash.html", {'da':da,'s':ses, 'd':PatientId, 'n':DoctorName, 'q':qo})
## ernie
                # return render(request, "patientdash.html", {'da':da,'s':ses, 'd':PassedPatientId, 'n':name, 'q':qo})
            else:
                picc = []
                for ka,va in pic.items():
                    picc.append(tuple((ka, va)))
                l = [x[1] for x in picc]
                print ("this is l in 2nd else")
                print (l)
                pic = l

                if 'SessionStart' not in request.session:
                    return redirect('/SignIn')
                else:
                    return render(request, "patientdash.html",{'da':da,'s':ses, 'd':PatientId, 'n':DoctorName, 'q':qo})
## ernie
                    # return render(request, "patientdash.html",{'da':da,'s':ses, 'd':PassedPatientId, 'n':name, 'q':qo})

def UpdateDoctorProfile(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    try:
        UserInfoDictionary = db.child("users").child("doctor").child(ses).get().val()
    except:
        return render(request,"index.html")
#   -- lis array contains the stored user information --    #
    lis = []
    for key,value in UserInfoDictionary.items():
        lis.append(tuple((key, value)))
    lis.sort(reverse=True)

    DoctorInformation = [x[1] for x in lis]

    DoctorMobileNum = DoctorInformation[5]
    DoctorBirthdate = DoctorInformation[6]
    DoctorMobileNumInput = str(DoctorMobileNum[4:])
    DoctorAddress = DoctorInformation[7]
    DoctorEmail = db.child("users").child("doctor").child(ses).child("email").shallow().get().val()

    if 'SessionStart' not in request.session:
        return redirect('/SignIn')
    else:
        DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
        return render(request, "upd.html",{'n':DoctorName,'dab':DoctorInformation, 'e':DoctorEmail, 'd':DoctorBirthdate,'d1':DoctorMobileNumInput,'d2':DoctorAddress})

def UpdatedDoctorProfile(request):   ## updatedprof
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    email = request.POST.get('email')
    famName = request.POST.get('famName')
    firstName = request.POST.get('firstName')
    gender = request.POST.get("gender")
    birthdate = request.POST.get("birthdate")
    address = request.POST.get("address")
    num = '+63' + str(request.POST.get("mobileNum"))
    MS = request.POST.getlist('MS')
    lNum = request.POST.get('lNum')
    profpic = request.FILES.get('myfile',False)
#   -- checks if there are any modifications per information -- #
    FamilyName = len(famName)
    if FamilyName is 0:
        NewFamilyName = db.child("users").child("doctor").child(ses).child("fullname").child("lastName").shallow().get().val()
        famName = NewFamilyName

    FirstName = len(firstName)
    if FirstName is 0:
        NewFirstName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
        firstName = NewFirstName

    HomeAddress = len(address)
    if HomeAddress is 0:
        NewHomeAddress = db.child("users").child("doctor").child(ses).child("address").shallow().get().val()
        address = NewHomeAddress

    MobileNum = len(num)
    if MobileNum is 3:
        NewMobileNum = db.child("users").child("doctor").child(ses).child("contactNo").shallow().get().val()
        num = NewMobileNum

    MedicalSpecialization = len(MS)
    if MedicalSpecialization is 0:
        NewMedicalSpecialization = db.child("users").child("doctor").child(ses).child("medicalSpecialization").shallow().get().val()
        MS = NewMedicalSpecialization

    LicenseNumber = len(lNum)
    if LicenseNumber is 0:
        NewLicenseNumber = db.child("users").child("doctor").child(ses).child("LicenseNum").shallow().get().val()
        lNum = str(NewLicenseNumber)
    fullname = {
        'lastName': famName,
        'firstname': firstName
        }
    DatabaseConnect = db.child("users").child("doctor").child(ses)
    DatabaseConnect.update({
            'email':email,
            'fullname':fullname,
            'address':address,
            'gender':gender,
            'birthDate':birthdate,
            'contactNo' : num,
            'medicalSpecialization' : MS,
            'LicenseNum': lNum
            })
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
#   -- checks if there is an uploaded profile picture --    #
    if profpic is False:
        UserInfoDictionary = db.child("users").child("doctor").child(ses).get().val()
        print("this is user info dictionary")
        print (UserInfoDictionary)
        lis = []
        for key,value in UserInfoDictionary.items():
            lis.append(tuple((key, value)))
        lis.sort(reverse=True)
        print("this is lis in if")
        print(lis)
        DoctorInformation = [x[1] for x in lis]
        print("this is doctor information")
        print (DoctorInformation)
        DisplayDoctorInformation = DoctorInformation
        pic = db.child("users").child("profilepic").child(ses).child("link").get().val()

        print("this is pic")
        print(pic)
        if pic is None:
            return render(request, "dash.html", {'e':email,'dab':DisplayDoctorInformation, 'n':DoctorName})
        else:
            picc = []
            for ka,va in pic.items():
                picc.append(tuple((ka, va)))
            l = [x[1] for x in picc]
            print("this is l")
            print (l)
            pic = l
            return render(request, "dash.html", {'dab':DisplayDoctorInformation,'p':pic, 'n':DoctorName})
    else:
        print("this is up")
        print (DatabaseConnect)
        StoreImage = sto.child("images").child("doctor").child(ses).child("profpicture").put(profpic)
        print("this is StoreImage")
        print(StoreImage)
        FetchToken = sto.child("images").child("doctor").child(ses).child("profpicture").get_url(StoreImage['downloadTokens'])
        print("this is j_url")
        print (FetchToken)
        im = db.child("users").child("profilepic").child(ses).child("link")
        im.update({'url':FetchToken})
        SuccessMsg = "Updated Successfully"

        UserInfoDictionary = db.child("users").child("doctor").child(ses).get().val()

        lis = []
        for key,value in UserInfoDictionary.items():
            lis.append(tuple((key, value)))
        lis.sort(reverse=True)

        DoctorInformation = [x[1] for x in lis]
        DoctorImage = db.child("users").child("profilepic").child(ses).child("link").get().val()

        if DoctorImage is None:
            return render(request, "dash.html", {'dab':DoctorInformation, 'n':DoctorName})
        else:
            AccessImage = []
            for ka,va in DoctorImage.items():
                AccessImage.append(tuple((ka, va)))
            print("this is AccessImage")
            print(AccessImage)
            DoctorImage = [x[1] for x in AccessImage]

        if 'SessionStart' not in request.session:
            return redirect('/SignIn')
        else:
            return render(request, "dash.html", {'dab':DoctorInformation,'p':DoctorImage, 'm':SuccessMsg, 'n':DoctorName})

def Logout(request):
    print (auth)
    # auth.logout(request)
    request.session.flush();
    return render(request,"logout.html")

def UpdatePatientProfile(request):
    print("THIS IS UPDATE PATIENT PROFILE")
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    if 'my_pat' in request.session:
        PatientId = request.session['my_pat']
    print (PatientId)
    StoredData = db.child("users").child("patient").child(ses).child(PatientId).get().val()
    print("this is le in update patient profile")
    print(StoredData)

    SortedPatientInformation = []
    for key,value in StoredData.items():
        SortedPatientInformation.append(tuple((key, value)))
    SortedPatientInformation.sort(reverse=True)
    print("this is leb")
    print (SortedPatientInformation)
    # b = len(leb)
    # print("this is b")
    # print (b)

    g = [x[1] for x in SortedPatientInformation]
    print (g)
    # da = g
    dabb = g[3]
    daabb = str(dabb[4:])
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()

    if 'SessionStart' not in request.session:
        return redirect('/SignIn')
    else:
        return render(request,"upp.html", {'n':DoctorName,'d':g, 'd1':daabb})

def UpdatedPatientProfile(request):    ## updatedpatprof
    print("THIS IS UPDATED PATIENT PROFILE")
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    email = request.POST.get('email')
    famName = request.POST.get('famName')
    firstName = request.POST.get('firstName')
    gender = request.POST.get("gender")
    birthdate = request.POST.get("birthDate")
    address = request.POST.get("address")
    btype = request.POST.get("btype")
    num = '+63' + str(request.POST.get("mobileNum"))
    PatientId = request.session['my_pat']

    EmailAddress = len(email)
    if EmailAddress is 0:
        NewEmailAddress = db.child("users").child("patient").child(ses).child(PatientId).child("email").shallow().get().val()
        email = NewEmailAddress

    FamilyName = len(famName)
    if FamilyName is 0:
        NewFamilyName = db.child("users").child("patient").child(ses).child(PatientId).child("fullname").child("lastName").shallow().get().val()
        famName = NewFamilyName

    FirstName = len(firstName)
    if FirstName is 0:
        NewFirstName = db.child("users").child("patient").child(ses).child(PatientId).child("fullname").child("firstname").shallow().get().val()
        firstName = NewFirstName

    HomeAddress = len(address)
    if HomeAddress is 0:
        NewHomeAddress = db.child("users").child("patient").child(ses).child(PatientId).child("address").shallow().get().val()
        address = NewHomeAddress

    MobileNum = len(num)
    if MobileNum is 3:
        NewMobileNum = db.child("users").child("patient").child(ses).child(PatientId).child("contactNo").shallow().get().val()
        num = NewMobileNum

    fullname = {
        'lastName': famName,
        'firstname': firstName
        }
    DatabaseConnect = db.child("users").child("patient").child(ses).child(PatientId)
    DatabaseConnect.update({
            'email':email,
            'fullname':fullname,
            'address':address,
            'contactNo':num,
            'gender':gender,
            'birthDate':birthdate,
            'bloodType':btype,
            })
    print (DatabaseConnect)
    SuccessMsg = "Updated Successfully"

    NewData = db.child("users").child("patient").child(ses).child(PatientId).get().val()
    print("this is le")
    print (NewData)

    SortedNewData = []
    for key,value in NewData.items():
        SortedNewData.append(tuple((key, value)))
    SortedNewData.sort(reverse=True)
    print("this is leb")
    print (SortedNewData)
    # b = len(leb)
    # print("this is b")
    # print (b)

    g = [x[1] for x in SortedNewData]
    print("this is g")
    print (g)
    # da = g
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
    pic = db.child("users").child(ses).child("link").child("patient").child(PatientId).get().val()
    print("this is pic")
    print(pic)
    PatientBPReading = db.child("users").child("data").child(ses).child(PatientId).child("BPdata").shallow().get().val()
    print("this is PatientBPReading")
    print(PatientBPReading)
    if PatientBPReading is None:
        # if pic is None:
        SuccessMsg = "Updated Successfully"
        return render(request, "patientdash.html", {'da':g,'s':ses, 'd':PatientId, 'n':DoctorName})
        # else:
        #     picc = []
        #     for ka,va in pic.items():
        #         picc.append(tuple((ka, va)))
        #     print("this is picc")
        #     print(picc)
        #     l = [x[1] for x in picc]
        #     print("this is l")
        #     print (l)
        #     pic = l
        #     SuccessMsg = "Updated Successfully"
        # return render(request, "patientdash.html",{'n':DoctorName, 'da':g,'s':ses, 'd':PatientId})
    op = []
    for i in PatientBPReading:
        op.append(str(i))
        op.sort()
    print("this is op")
    print (op)
    qo = []
    for a in op:
        Systolic = db.child("users").child("data").child(ses).child(PatientId).child("BPdata").child(a).child("syst").get().val()
        Diastolic = db.child("users").child("data").child(ses).child(PatientId).child("BPdata").child(a).child("dias").get().val()
        BPReading = str(Systolic)+ " " + str(Diastolic)
        qo.append(str(BPReading))
    print("this is qo")
    print (str(qo))
    if pic is None:
        SuccessMsg = "Updated Successfully"
        return render(request, "patientdash.html", {'da':g,'s':ses, 'd':PatientId, 'n':DoctorName, 'q':qo})
    else:
        picc = []
        for ka,va in pic.items():
            picc.append(tuple((ka, va)))
        l = [x[1] for x in picc]
        print("this is l in else")
        print (l)
        pic = l

    if 'SessionStart' not in request.session:
        return redirect('/SignIn')
    else:
        SuccessMsg = "Updated Successfully"
        return render(request, "patientdash.html",{'da':g,'s':ses, 'd':PatientId, 'n':DoctorName, 'q':qo})


def Chart(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')
    if 'my_pat' in request.session:
        PatientId = request.session['my_pat']
    print (PatientId)
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()

    return render(request, "chart.html",{'s':ses,'d':PatientId, 'n':DoctorName})

    
def ContactPatientForm(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
    return render(request, 'contact.html', {'n':DoctorName})

def ContactPatient(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    if 'my_pat' in request.session:
        PatientId = request.session['my_pat']

    PatientContactNumber = db.child("users").child("patient").child(ses).child(PatientId).child("contactNo").shallow().get().val()
    SMS = request.POST.get('noww')

    send_message(to=PatientContactNumber,text=SMS)
    PatientInformation = db.child("users").child("patient").child(ses).child(PatientId).get().val()

    SortedPatientInformation = []
    for key,value in PatientInformation.items():
        SortedPatientInformation.append(tuple((key, value)))
    SortedPatientInformation.sort(reverse=True)

    g = [x[1] for x in SortedPatientInformation]

    # this is for pop up message
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
    ### not sure if needed ang pic
    pic = db.child("users").child("patientprof").child(ses).child("link").get().val()
    print("this is pic")
    print(pic)
    # if pic is None:
    message = "Message Sent! Redirecting to Patient Profile"
    return render(request, "patientdash.html", {'da':g, 'n':DoctorName, 'm':message})

def ViewPatient(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')
    UserInfoDictionary = db.child("users").child("doctor").child(ses).child("email").shallow().get().val()
    if 'SessionStart' not in request.session:
        return redirect('/SignIn')
    else:
        return render(request, 'credentials.html', {'e':UserInfoDictionary})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def PatientList(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')
    ## fetch email and password input
    email = db.child("users").child("doctor").child(ses).child("email").shallow().get().val()
    passw = request.POST.get('pass')
    ## try to autheniticate in database
    try:
        user = authe.sign_in_with_email_and_password(email,passw)
    except:
        message = "Invalid Credentials!"
        return render(request,"credentials.html",{"m":message, 'e':email})
    ## if authenticated
    uid = user['localId']
    request.session['SessionStart'] = str(uid)
    request.session['patientdash_session'] = str(uid)
    ses = request.session['SessionStart']

    if 'patientdash_session' not in request.session:
        return redirect('/vform')
    else:
        all_user_ids = db.child("users").child("patient").child(ses).get().val()
        DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
        if all_user_ids is None:
            return render(request, "nopat.html", {'n':DoctorName})
        else:
            PatientNames = []
            for item in all_user_ids:
                fename = db.child("users").child("patient").child(ses).child(item).child("fullname").child("firstname").shallow().get().val()
                lename = db.child("users").child("patient").child(ses).child(item).child("fullname").child("lastName").shallow().get().val()
                full = str(item)+ "-" +str(lename) +", "+str(fename)
                PatientNames.append(str(full))
            PatientNames.sort(reverse = True)

        if 'patientdash_session' not in request.session:
            return redirect('/login')
        else:
            return render(request, "patientlist.html",{'PatientName':PatientNames, 'n':DoctorName})

def PatientList2(request):
    print("PATIENT LIST 2")
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    all_user_ids = db.child("users").child("patient").child(ses).get().val()
    print("all user ids")
    print(all_user_ids)
    DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
    if all_user_ids is None:
        print("inside if")
        return render(request, "nopat.html", {'n':DoctorName})
    else:
        print("inside else")
        PatientNames = []
        for item in all_user_ids:
            fename = db.child("users").child("patient").child(ses).child(item).child("fullname").child("firstname").shallow().get().val()
            lename = db.child("users").child("patient").child(ses).child(item).child("fullname").child("lastName").shallow().get().val()
            full = str(item)+ "-" +str(lename) +", "+str(fename)
            PatientNames.append(str(full))
        PatientNames.sort(reverse = True)
        print(PatientNames)

    if 'patientdash_session' not in request.session:
        return redirect('/login')
    else:
        return render(request, "patientlist2.html",{'PatientName2':PatientNames, 'n':DoctorName})
        print("END OF PATIENT LIST 2")


def impForm(request):
    if 'SessionStart' in request.session:
        ses = request.session['SessionStart']
        print (ses)
    else:
        print ("No Session")
        return redirect('/SignIn')

    UserInfoDictionary = db.child("users").child("doctor").child(ses).child("email").shallow().get().val()
    # return render(request, 'credentials1.html', {'e':UserInfoDictionary})
    return render(request,"credentials1.html",{'e':UserInfoDictionary})

def impCredentials(request):
        if 'SessionStart' in request.session:
            ses = request.session['SessionStart']
        else:
            print ("No Session")
            return redirect('/SignIn')
        UserInfoDictionary = db.child("users").child("doctor").child(ses).child("email").shallow().get().val()
        email = UserInfoDictionary
        passw = request.POST.get('pass')
        DoctorName = db.child("users").child("doctor").child(ses).child("fullname").child("firstname").shallow().get().val()
        try:
            user = authe.sign_in_with_email_and_password(email,passw)
        except:
            message = "Invalid Credentials!"
            # return render(request,"credentials1.html",{"m":message, 'e':UserInfoDictionary, 'n':DoctorName})
            return render(request,"credentials1.html",{"m":message, 'e':UserInfoDictionary, 'n':DoctorName})
        print (user)
        uid = user['localId']
        print (user)
        request.session['SessionStart'] = str(uid)

        if 'SessionStart' not in request.session:
            return redirect('/SignIn')
        else:
            return render(request, "add.html",{'n':DoctorName})