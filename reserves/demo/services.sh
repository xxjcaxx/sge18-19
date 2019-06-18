#!/bin/bash

echo '<odoo><data>'

for i in img/*.png
do

	name=$(echo $i | cut -d"." -f1 | cut -d'/' -f2)
	echo '<record model="reserves.services" id="reserves.services_'$name'"><field name="name">'$name'</field><field name="icon">'$(base64 $i)'</field></record>' 
	
	
done
echo '</data></odoo>'
