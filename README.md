# Flask_with_Selinium

sudo apt-get update

sudo apt-get install python3-venv

git clone https://github.com/kvsnrkolapalli/Flask_with_Selinium/

mv Flask_with_Selinium Flask

cd Flask

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

sudo apt-get install chromium-chromedriver


sudo nano /etc/systemd/system/flask.service

Add this into the File

[Unit]
Description=Gunicorn instance for a simple app
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Flask
ExecStart=/home/ubuntu/Flask/venv/bin/gunicorn -b localhost:8000 app:app
Restart=always
[Install]
WantedBy=multi-user.target


sudo systemctl daemon-reload

sudo systemctl start flask

sudo systemctl enable flask

curl localhost:8000

sudo apt install nginx

sudo systemctl start nginx

sudo systemctl enable nginx

sudo nano /etc/nginx/sites-available/default

Add these Lines:
Top-{{{{{

upstream flaskhelloworld {
    server 127.0.0.1:8000;
}

}}}}}


Add in: Location{ }
{{{{{ proxy_pass http://flaskhelloworld; }}}}}}



sudo systemctl restart nginx
