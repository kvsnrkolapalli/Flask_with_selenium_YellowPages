from selenium.webdriver.common.by import By               
from selenium import webdriver        
from datetime import datetime
import pandas as pd
from selenium.webdriver.chrome.options import Options
import time
import io
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import pytz
import re
from selenium.webdriver import ActionChains
import os
from datetime import datetime
from flask import Flask, render_template, url_for, request,send_file,redirect
from flask_sqlalchemy import SQLAlchemy
from flask import *
import _thread
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_wtf import FlaskForm 
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


browse_params=False
columns=['Company Title','Address','Website','Phone Number','Second Number']
df=pd.DataFrame(columns=columns)

class Yellow:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            chromedriver_path = '/usr/bin/chromedriver'
            self.browser=webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=options)
            # self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
        

def get_list(browser,class_):
    list=[]
    company_elements=browser.browser.find_elements(by=By.CLASS_NAME,value=class_)
    for company_element in company_elements:
        if company_element.tag_name=='a':
            list.append(company_element.text)
    return list,company_elements[0]


def get_list_href(browser,class_):
    list=[]
    company_elements=browser.browser.find_elements(by=By.CLASS_NAME,value=class_)
    for company_element in company_elements:
        if company_element.tag_name=='a':
            print(company_element.get_attribute('href'))
            list.append(company_element.get_attribute('href'))
    return list

def get_list_href_xpath(browser,XPATH,l):
    list=[]
    XPATH='/html/body/div[5]/div/div[4]/div/company-result-0-'+XPATH+'/div[1]/div[2]/span[2]/a'
    print(XPATH)
    for i in range(0,l):
        XPATH_link=XPATH.replace('result-0','result-'+str(i))
        print(XPATH_link)
        try:
            company_element=browser.browser.find_element(by=By.XPATH,value=XPATH_link)
            if company_element.tag_name=='a':
                list.append(company_element.get_attribute('href'))
        except:
            list.append('')
    return list


def UI(Company,city,o_id):
    with app.test_request_context():
        global df
        start_time=datetime.now((pytz.timezone('US/Pacific')))
        browser=Yellow('SAM')
        search=Company
        try:
            main_link='https://yellowpages.com.eg/en/category/'+search.lower().replace(' ','-')+'/p1'+str(city)
            browser.open_page(main_link)

            last_page=browser.browser.find_element(by=By.CLASS_NAME,value='last-page').get_attribute('href')

            pages=last_page.split('/')[-1].split('p')[-1].split('?')[0]
            order=Orders.query.filter_by(o_id=o_id).first()
            order.no_of_pages=pages

            for page in range(1,int(pages)+1):
                order.status='Getting Page - '+str(page)
                db.session.commit()
                main_link='https://yellowpages.com.eg/en/category/'+search.lower().replace(' ','-')+'/p'+str(page)+str(city)
                print(main_link)
                browser.open_page(main_link)

                company_titles,xpath=get_list(browser,'item-title')

                # Get the XPath using JavaScript
                xpatha = browser.browser.execute_script("function absoluteXPath(element) {" +
                                            "var comp, comps = [];" +
                                            "var parent = null;" +
                                            "var xpath = '';" +
                                            "var getPos = function(element) {" +
                                            "var position = 1, curNode;" +
                                            "if (element.nodeType == Node.ATTRIBUTE_NODE) {" +
                                            "return null;" +
                                            "}" +
                                            "for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {" +
                                            "if (curNode.nodeName == element.nodeName) {" +
                                            "++position;" +
                                            "}" +
                                            "}" +
                                            "return position;" +
                                            "};" +
                                            "if (element instanceof Document) {" +
                                            "return '/';" +
                                            "}" +
                                            "for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {" +
                                            "comp = comps[comps.length] = {};" +
                                            "switch (element.nodeType) {" +
                                            "case Node.TEXT_NODE:" +
                                            "comp.name = 'text()';" +
                                            "break;" +
                                            "case Node.ATTRIBUTE_NODE:" +
                                            "comp.name = '@' + element.nodeName;" +
                                            "break;" +
                                            "case Node.PROCESSING_INSTRUCTION_NODE:" +
                                            "comp.name = 'processing-instruction()';" +
                                            "break;" +
                                            "case Node.COMMENT_NODE:" +
                                            "comp.name = 'comment()';" +
                                            "break;" +
                                            "case Node.ELEMENT_NODE:" +
                                            "comp.name = element.nodeName;" +
                                            "break;" +
                                            "}" +
                                            "comp.position = getPos(element);" +
                                            "}" +
                                            "for (var i = comps.length - 1; i >= 0; i--) {" +
                                            "comp = comps[i];" +
                                            "xpath += '/' + comp.name.toLowerCase();" +
                                            "if (comp.position !== null) {" +
                                            "xpath += '[' + comp.position + ']';" +
                                            "}" +
                                            "}" +
                                            "return xpath;" +
                                            "};" +
                                            "return absoluteXPath(arguments[0]);", xpath)

                company_address,a=get_list(browser,'address-text')

                website=get_list_href_xpath(browser,xpatha.split('result-0-')[1].split('[1]/div[2]/div[1]/a[1]/span[1]')[0],len(company_titles))

                mobile_numbers=[]
                company_elements=browser.browser.find_elements(by=By.CLASS_NAME,value='call-us-click')
                # Create an instance of ActionChains
                actions = ActionChains(browser.browser)
                elem=browser.browser.find_element(by=By.XPATH,value='/html/body/div[5]/div/div[4]/form')

                for company_element in company_elements:
                    if company_element.tag_name=='span':
                        # Move to the element
                        try:
                            actions.move_to_element(company_element).perform()
                            company_element.click()
                            time.sleep(0.3)
                            html=company_element.get_attribute('outerHTML')
                            html=html.replace('&quot;','"')
                            phone_numbers = re.findall(r'<a href="tel:(.*?)">', html)
                            elem.click()
                            list=[]
                            try:
                                list.append(phone_numbers[0])
                            except:
                                list.append('')
                                pass
                            text=''
                            for i in range(1,len(phone_numbers)):
                                if i==1:
                                    text=text+phone_numbers[i]
                                else:
                                    text=text+','+phone_numbers[i]
                            list.append(text)
                            print(list)
                        except:
                            list=['','']
                        mobile_numbers.append(list)
                        
                for i in range(len(company_titles)):
                    list=[company_titles[i],company_address[i],website[i],mobile_numbers[i][0],mobile_numbers[i][1]]
                    # Convert the list to a DataFrame with a single row
                    new_row_df = pd.DataFrame([list], columns=df.columns)
                    df = df.append(new_row_df, ignore_index=True)
                # excel_file = 'out.xlsx'
                # df.to_excel(excel_file, index=False)
        
                excel_file = io.BytesIO()
                df.to_excel(excel_file, index=False)
                excel_file.seek(0)
                order=Orders.query.filter_by(o_id=o_id).first() 
                
                order.file=excel_file.read()
                db.session.commit()
            order=Orders.query.filter_by(o_id=o_id).first() 
            order.status='Completed'
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            order.total_sec=total_sec.seconds
            order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
            db.session.commit()
            return 'Completed'
        except:
            order=Orders.query.filter_by(o_id=o_id).first() 
            order.status='Problem Has Occurred'
            end_time=datetime.now((pytz.timezone('US/Pacific')))
            total_sec=end_time-start_time
            order.total_sec=total_sec.seconds
            order.time_completed=datetime.now((pytz.timezone('US/Pacific'))).strftime("%m-%d-%Y, %H:%M:%S")
            db.session.commit()  
            try:
                browser.close_browser()
            except:
                pass


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'Myones..OK?!'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    
class Orders(db.Model):
    o_id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    order_id_remark = db.Column(db.String(80))
    time_created = db.Column(db.String(80))
    name = db.Column(db.String(80))
    status = db.Column(db.String(80))
    time_completed = db.Column(db.String(80))
    file = db.Column(db.LargeBinary)
    no_of_pages = db.Column(db.String(80))
    total_sec = db.Column(db.String(80))


    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    
    
    


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        message='Invalid username or password'
        return render_template('login.html', form=form,message=message)

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            message='Username Already Exists..'
        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            message='New user has been created!'
        return render_template('signup.html', form=form,message=message)
    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user.username)
    return render_template('index.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/account')
@login_required
def account():
    user=str(current_user.username)
    view_all=Orders.query.filter_by(username=user)
    return render_template('account.html', name=current_user.username,view_all=view_all)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        try:
            company_name=request.form['company_name']
            city=request.form['city']
            print(company_name)
            start_time=datetime.now(pytz.timezone('US/Pacific')).strftime("%m-%d-%Y, %H:%M:%S")
            new_order=Orders(username=current_user.username,time_created=start_time,name=company_name,status='Order Created')
            db.session.add(new_order)
            db.session.commit()
            o_id=new_order.o_id
            print(o_id) 
            _thread.start_new_thread(UI,(company_name,city,o_id,))
            return redirect('/account')
        except:
            pass
        return render_template('search.html', name=current_user.username)
    return render_template('search.html', name=current_user.username)

@app.route('/download_file/<o_id>')
@login_required
def download_pdf(o_id):
    d=Orders.query.filter_by(o_id=o_id).first()
    if d.username==current_user.username:
        path=str(d.name).replace(' ','_')+'.xlsx'
        # Create a BytesIO object to hold the Excel file
        excel_file = io.BytesIO(d.file)
        # Return the Excel file as a response
        return send_file(excel_file, download_name=path,
                     as_attachment=True)
    else:
        return 'Unauthorized Request'
    
@app.route('/remove_order/<o_id>')
@login_required
def remove_order(o_id):
    d=Orders.query.filter_by(o_id=o_id).first()
    if d.username==current_user.username:
        db.session.delete(d)
        db.session.commit()
        return redirect('/account')
    else:
        return 'Unauthorized Request'


if __name__ == '__main__':
    app.run(debug=True) 
