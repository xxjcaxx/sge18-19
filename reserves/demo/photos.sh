#!/bin/bash

echo '<odoo><data>'

for i in img/*.jpg
do
	hotel=$(echo $i | grep -o 'hotel.')
	name=$(echo $i | cut -d"-" -f2 | tr '.' '_')
	echo '<record model="reserves.photos" id="reserves.photos_'$hotel'_'$name'"><field name="name">'$name'</field><field name="hotel" ref="reserves.'$hotel'"/><field name="photo">'$(base64 $i)'</field></record>' 
	
	
done
echo '</data></odoo>'
