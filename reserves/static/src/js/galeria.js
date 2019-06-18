console.log('Creacio del widget galeria');
odoo.define('cine.galeria', function(require) {
    "use strict";
var AbstractField = require('web.AbstractField'); 
	/* Ens basem en la classe abstracta 
	 * del fitxer /web/static/src/js/fields/abstract_field.js
	 * */
var core = require('web.core');
var qweb = core.qweb; // Necessari per cridar al render
var utils = require('web.utils'); // per a la imatge
var photo = 'photo_small';  // El nom que té el field de la foto per defecte.

var galeria = AbstractField.extend({
    className: 'o_field_m2m_galeria', // classe CSS
    supportedFieldTypes: ['many2many','many2one'], // Suporta M2m i M2o
    galeria_template: 'galeria_template', 
	/*
	 *  template: Definició de la plantilla Qweb
	 *  Recordem que tots els templates estan en el client 
	 *  perquè els demana amb web/webclient/qweb
	 *
	 *  En aquest cas utilitzem galeria_template perquè no volem que l'utilitze
	 *  dirèctament, sino cridar al qweb.render amb paràmetre.
	 */
   fieldsToFetch: {   // Els fields que va a demanar el widget del model. 
	   // Sols demana els que diu aquesta llista. Es pot observar en el debug del navegador.
	   // https://gitlab.merchise.org/merchise/odoo/commit/eafa14d3bc16e7212000d0c9c30a3ed922395574?view=inline
        display_name: {type: 'char'},
       // [photo]: {type: 'binary'},
	   /*
	    * Aquesta línia està comentada perquè l'interpreta abans de ser carregat el field. 
	    * Per tant, no pot fer ús del atribut 'image_field' de la vista i sempre utilitza el valor inicial
	    * de la variable photo. fieldsTofech és interpretat per data_manager.js al carregar la vista sencera, no el widget.
	    */
    },
    placeholder: "/web/static/src/img/placeholder.png", // Imatge en cas de no tindre imatge
    willStart: function(){
    
        var self = this;  // Com que anem a cridar a funcions, el this serà diferent dins i cal fer una variable independent.

        var res = this._rpc({           
		model: this.value.model,   // El model demanat per el field
                method: 'read',        // Demana el mètode python read
                args: [this.value.res_ids, [photo,'display_name']],   // En aquest cas, enviem com a arguments els ids demanats i el nom dels fields demanats.
                context: this.record.getContext(),   // El context
                }).then(function (result) {       
                if (result.length === 0) {
                    console.log('no trobat');
                }
	   	 var i;
            	for(let i of result) {
			var url = self.placeholder; // En cas de no tindre url
			if (i[photo]) {
			url = 'data:image/png;base64,' + i[photo];
			    }
		    	i.url= url;
		}
		self.record.dataLoaded = { elements: result, readonly: self.mode === "readonly"}; // El render espera aquest objecte
		});
	    return res;  // res és un 'promise' de jquery, ja que segurament el rpc no acaba abans que la funció. 
	                 // La funció que el cride ha de fer un $.when per esperar a que acabe la 'promise' i les dades estiguen carregades.
    
    },
    start: function() { 
	var p = this.$el.append('<p>Widget Galeria</p>');
	    // ^ línia sols per provar cóm es poden afegir coses al widget en start 
	    // (no es veurà, ja que sols funciona amb el render per defecte)
        return $.when(p, this._super.apply(this,arguments)); // $.when espera a l'inserció 
    },
    init: function(parent, name, record, options) { //inizialització amb valors
        photo = record.fieldsInfo[options.viewType][name].image_field //La manera d'extraure el valor d'un atribut 
	                                                              // En el field de la vista
        this._super.apply(this,arguments);
    },
    
    _LoadGaleria: function(){
    console.log('Load Galeria');
    },

/*
 *La següent funció modifica els datos que s'envien al render afegint el base64 al raw de la imatge.
 Com que no ha carregat la imatge en fieldsTofetch, cal fer un _rpc per a carregar-la en el moment del render. 
 Aquesta, no és la millor solució i per això està comentada, perquè carrega les dades cada vegada que es renderitza.
 La solució correcta és fer-ho en el willStart que ja actua de forma asíncrona.
 * */
    _getRenderGaleriaContext: function () {
        // var elements = this.value ? _.pluck(this.value.data, 'data') : []; 
	    // _.pluck() és una funció de underscore.js una biblioteca javascript que també
	    // utilitza Odoo. pluck és l'equivalent a mapped() en python.
	    // En aquest cas, de la llista sols volem un array amb la clau data de cadascun.
        /*var self = this;  // Com que anem a cridar a funcions, el this serà diferent dins i cal fer una variable independent.
        var res = this._rpc({           
		model: this.value.model,   // El model demanat per el field
                method: 'read',        // Demana el mètode python read
                args: [this.value.res_ids, [photo,'display_name']],   // En aquest cas, enviem com a arguments els ids demanats i el nom dels fields demanats.
                context: this.record.getContext(),   // El context
                }).then(function (result) {       
                if (result.length === 0) {
                    console.log('no trobat');
                }
	   	 var i;
            	for(let i of result) {
			var url = self.placeholder; // En cas de no tindre url
			if (i[photo]) {
			url = 'data:image/png;base64,' + i[photo];
			    }
		    	i.url= url;
		}
		self.record.dataLoaded = { elements: result, readonly: self.mode === "readonly"}; // El render espera aquest objecte
		});
	    return res;  // res és un 'promise' de jquery, ja que segurament el rpc no acaba abans que la funció. 
	                 // La funció que el cride ha de fer un $.when per esperar a que acabe la 'promise' i les dades estiguen carregades. */
    },

    _renderReadonly: function () {
        this._renderGaleria();
    },
    _renderEdit: function () {
        this._renderGaleria();
    },
    _renderGaleria: function () {
	    var self = this;
            $.when(this._getRenderGaleriaContext()).done(function(){
            //this.$el.html(qweb.render(this.tag_template, this._getRenderTagsContext()));
            self.$el.html(qweb.render(self.galeria_template, self.record.dataLoaded));
	    });
	    /*
	     *qweb.render() és una funció que accepta una template i un context en el que estan les 
	     variables que en template necessita. En aquest cas enviem elements i l'opcio de readonly
	     * */
    },
});
	var fieldRegistry = require('web.field_registry');
	fieldRegistry.add('m2m_galeria', galeria); // Son cal fer widget="m2m_galeria" en un field m2m o o2m
	return galeria;
});
