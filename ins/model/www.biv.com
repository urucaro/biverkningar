#
#  biv.com (/etc/apache2/sites-available/www.biv.com)
#
<VirtualHost *:80>
        ServerAdmin webmaster@biv.com
        ServerName  www.biv.com
        ServerAlias biv.com
	
	#DocumentRoot baseprefix/app/
	#<Directory baseprefix/app/>
	#	Options Indexes FollowSymLinks MultiViews
	#	AllowOverride None
	#	Order allow,deny
	#	allow from all
	#</Directory>


	WSGIDaemonProcess  biv user=www-data group=www-data processes=1 threads=5
	WSGIScriptAlias / baseprefix/app/biv.wsgi.py
	

	<Directory /var/lib/biv/app>
		WSGIProcessGroup biv
		WSGIApplicationGroup %{GLOBAL}
		Order deny,allow
		Allow from all
	</Directory>

        # Logfiles
        ErrorLog  baseprefix/logs/error.log
        CustomLog baseprefix/logs/access.log combined
</VirtualHost>
