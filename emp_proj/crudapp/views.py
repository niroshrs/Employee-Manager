#from math import e
from django.shortcuts import render,redirect
from crudapp.models import EmpDetail, LoggedInUser

from django.utils import timezone


#from django.contrib.auth import logout as auth_logout

#import package ----------------------------------------------
from cryptography.fernet import Fernet
from django.conf import settings
# Create your views here.
#import key ----------------------------------------------------
f = Fernet(settings.ENCRYPT_KEY)
def create(req):
    
    if not req.session.get('emp_id'):       
            return redirect('login')
                   
    if req.method == "POST":
        # Process the form data
        emp_id =req.POST.get('emp_id')
        name = req.POST.get("name")
        email = req.POST.get("email")
        password = req.POST.get("password")
        mob_no = req.POST.get("mob_no")
        salary = req.POST.get("salary")
        title = req.POST.get("title")
        
        
        
        #encrypting++++++++++++++++++++++++++++++
        name_bytes = name.encode('utf-8')
        name_encrypt = f.encrypt(name_bytes)
        name_to_db = name_encrypt.decode('utf-8')
        
        password_bytes = password.encode('utf-8')
        password_encrypt = f.encrypt(password_bytes)
        password_to_db = password_encrypt.decode('utf-8')
       
        dt = EmpDetail.objects.create(name=name_to_db, 
                                      email=email, 
                                      mob_no=mob_no,
                                      salary=salary,
                                      title=title,
                                      emp_id=emp_id,
                                      password=password_to_db)

        if dt:
            return redirect('/employee/')
        else:
            pass
    else:
        return render(req, "create_emp.html")

#-------------------------------------------------------

def retrieve(req):
    
    if not req.session.get('emp_id'):       # ← guard
            return redirect('login')
            
            
    dt = EmpDetail.objects.all()
    for emp in dt:
        try:
            emp.name = f.decrypt(emp.name.encode()).decode()
        except Exception:
            pass
        try:
            emp.date = f.decrypt(emp.date.encode()).decode() 
        except Exception:
            pass
    return render(req, "all_emp.html", {'emp_data': dt})

#----------------------------------------------------------------

def delete(req,emp_id):
    
    if not req.session.get('emp_id'):       # ← guard
            return redirect('login')
            
            
    EmpDetail.objects.filter(id=emp_id).delete()
    return redirect('retrieve')
    
#----------------------------------------------------------------
 
def update(req, emp_id):
    
    if not req.session.get('emp_id'):       # ← guard
            return redirect('login')
            
            
    emp = EmpDetail.objects.get(id=emp_id)
    if req.method == "POST":
        # ... your existing POST logic is correct ...
        name = req.POST.get("name")
        encrypted_name = f.encrypt(name.encode('utf-8'))
        emp.name = encrypted_name.decode('utf-8')
        
        
        emp.email = req.POST.get("email")
        emp.mob_no = req.POST.get("mob_no")
        emp.save()
        return redirect('retrieve')
    else:
        # NEW: Decrypt the name so the user sees "John Doe" in the input box, 
        # not "gAAAAABl..."
        try:
            decrypted_name = f.decrypt(emp.name.encode('utf-8')).decode('utf-8')
            emp.name = decrypted_name
        except Exception:
            # Fallback if data is corrupted or already plain text
            pass

        context = {'emp': emp}
        return render(req, "update.html", context)
    
#----------------------------------------------------------------
def emp(req):
    print('-----------------------------------------------------',req.POST.emp_id)
    
#---------------------------------------------------    

def login(req):
    if req.method == "POST":
        emp_id = req.POST.get("emp_id")
        password = req.POST.get("password")

        try:
            emp = EmpDetail.objects.get(emp_id=emp_id)
            decrypted_password = f.decrypt(emp.password.encode()).decode()

            if decrypted_password == password:

                # Check if already logged in
                existing = LoggedInUser.objects.filter(emp=emp).first()

                if existing and existing.session_key:
                    print("BLOCKED — already logged in:", existing.session_key)
                    return render(req, "login.html", {
                        "error": "Already logged in from another device."
                    })

                # Set session data first
                req.session['emp_id'] = emp_id
                req.session['emp_name'] = f.decrypt(emp.name.encode()).decode()
                req.session['login_time'] = timezone.now().isoformat()
                
                date = timezone.now().isoformat()
                encrypted_date = f.encrypt(date.encode())
                emp.date = encrypted_date.decode('utf-8')
                emp.save()

                req.session.save()  # ← FORCE save to DB before reading session_key

                # Now session_key will have a real value, not None
                LoggedInUser.objects.update_or_create(
                    emp=emp,
                    defaults={'session_key': req.session.session_key}
                )

                print("Logged in, session key saved:", req.session.session_key)
                return redirect('/employee/')

            else:
                return render(req, "login.html", {"error": "Invalid credentials"})

        except EmpDetail.DoesNotExist:
            return render(req, "login.html", {"error": "Employee not found"})

    return render(req, "login.html")
    
def logout(request):
    emp_id = request.session.get('emp_id')

    if emp_id:
        try:
            emp = EmpDetail.objects.get(emp_id=emp_id)
            # Clear the session key — marks them as logged out
            LoggedInUser.objects.filter(emp=emp).update(session_key=None)
        except EmpDetail.DoesNotExist:
            pass

    request.session.flush()
    return redirect('login')
    
def session_expired_view(request):
    # ← Was rendering login.html, should show a dedicated expired page
    return render(request, 'session_expired.html')