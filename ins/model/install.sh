#!/bin/bash
echo Parameters: $@
WWWORIG=www.biv.com
WWWCONF=www.biv.com.conf
SUBDIRS=("scripts app logs data tpl img") ## Add new directories here

PREFIX=$1

if [ -z $PREFIX ]; then
    PREFIX=/var/lib/biv
fi

if [ -d $PREFIX ]
then
    echo $PREFIX already there
else
    echo Creating: $PREFIX
    sudo mkdir -m 775 $PREFIX
	sudo chown -R www-data:www-data $PREFIX
fi
for s in $SUBDIRS
do
    if [ ! -d $PREFIX/$s ]; then
        sudo mkdir -m 775 $PREFIX//$s
	sudo chown -R www-data:www-data $PREFIX$s
    fi
done

sudo cp core-1.0.0/scripts/maintain_db.py $PREFIX/scripts
sudo cp core-1.0.0/scripts/index.py $PREFIX/scripts

cd core-1.0.0
sudo ./setup_biv.py install
cd ..

sudo cp core-1.0.0/wsgi/biv.wsgi.py $PREFIX/app


sudo chown -R www-data:www-data $PREFIX/app
sudo chown -R www-data:www-data $PREFIX/tpl
sudo chown -R www-data:www-data $PREFIX/img

sudo touch $WWWCONF
sudo chmod 777 $WWWCONF
sudo sed s?baseprefix?$PREFIX?  $WWWORIG > $WWWCONF
sudo cp $WWWCONF /etc/apache2/sites-available/

sudo a2ensite $WWWCONF
sudo apache2ctl restart


