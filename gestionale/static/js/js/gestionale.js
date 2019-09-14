(function (justoop)

{
    var get = justoop.get,
    publish = get(justoop.publish),
    namespace = get(justoop.namespace),
    subclass = get(justoop.subclass),
    Server=get(justoop.Server),
    isUndefined = get(justoop.isUndefined),
    makeArray = get(justoop.makeArray),
    assert = get(justoop.assert);
    
   
    
    
     (function ()
        {   
          
    	   /*
            var socket = io.connect('http://' + document.domain + ':' + port );
    	    
    	    
    	    socket.on('connect',function() {
    	    	$("#plc_server_status").html("Server");
    	    	
    	    	$("#plc_server_status_off_img").removeClass("show");
    	    	$("#plc_server_status_on_img").addClass("show");
    	    	
    	    	
    	    });
    	    
    	    socket.on('disconnect',function() {
    	    	$("#plc_server_status").html("Server");
    	    	$("#plc_server_online_status").html("offline");
    	    	
    	    	$("#plc_server_status_on_img").removeClass("show");
    	    	$("#plc_server_status_off_img").addClass("show");
    	    	
    	    	
    	    });
    	    
    	    socket.on('connect_failed',function() {
    	    	
    	    	$("#plc_server_status").html("Server");
    	    	$("#plc_server_online_status").html("offline");
    	    	
    	    	$("#plc_server_status_on_img").removeClass("show");
    	    	$("#plc_server_status_off_img").addClass("show");
    	    	
    	    });
    	    
    	    socket.on('connect_error',function() {
    	    	
    	    	$("#plc_server_status").html("Server");
    	    	$("#plc_server_online_status").html("offline");
    	    	
    	    	$("#plc_server_status_on_img").removeClass("show");
    	    	$("#plc_server_status_off_img").addClass("show");
    	    });
    	    
    	    */
            var gestionaleRpc = subclass(  {

                __url__ : "/gestionale/default/call/jsonrpc",
                  

            searchPianoDeiConti : function (cmd)

            {
                return this.__call__("search_piano_dei_conti", makeArray(arguments));
            },
            
            returnListini : function ()

            {
                return this.__call__("return_listini", makeArray(arguments));
            },
                returnPrice : function ()

            {
                return this.__call__("return_price", makeArray(arguments));
            },
                
                returnPriceFornitori : function ()

            {
                return this.__call__("return_price_fornitori", makeArray(arguments));
            },
                addRowToDdt : function ()

            {
                return this.__call__("add_row_to_ddt", makeArray(arguments));
            },
            
            
            
            successivoRiba : function ()

	        {
	            return this.__call__("successivo_riba", makeArray(arguments));
	        }
,
            
            
            
            aggiornaGiacenza : function ()

	        {
	            return this.__call__("aggiorna_giacenza", makeArray(arguments));
	        }
            ,
            
            
            
            aggiornaQuantita : function ()

	        {
	            return this.__call__("aggiorna_quantita", makeArray(arguments));
	        }
	         ,
            
            
            
            riservaGiacenza : function ()

	        {
	            return this.__call__("riserva_giacenza", makeArray(arguments));
	        }
	        
	         ,
            
            
            
            disdireGiacenza : function ()

	        {
	            return this.__call__("disdire_giacenza", makeArray(arguments));
	        }
            
            ,
            
            
            
            accorpa : function ()

	        {
	            return this.__call__("accorpa", makeArray(arguments));
	        }
            
            ,
            
            
            
            aggiungiFattura : function ()

	        {
	            return this.__call__("aggiungi_fattura", makeArray(arguments));
	        }
            ,    addRowToDdtMod : function ()

            {
                return this.__call__("add_row_to_ddt_mod", makeArray(arguments));
            },
                 addRowToDdtFornitori : function ()

            {
                return this.__call__("add_row_to_ddt_fornitori", makeArray(arguments));
            },
                
                
                insertDdt : function ()

            {
                return this.__call__("insert_ddt", makeArray(arguments));
            },
            
            
            insertModDdt : function ()

        {
            return this.__call__("insert_mod_ddt", makeArray(arguments));
        },
                
                
                insertDdtPreview : function ()

            {
                return this.__call__("insert_ddt_preview", makeArray(arguments));
            },
            
            
            insertModDdtPreview : function ()

        {
            return this.__call__("insert_mod_ddt_preview", makeArray(arguments));
        }
                ,
                
                
                insertDdtFornitoriPreview : function ()

            {
                return this.__call__("insert_ddt_fornitori_preview", makeArray(arguments));
            }
                
                ,
                
                 insertDdtFornitori : function ()

            {
                return this.__call__("insert_ddt_fornitori", makeArray(arguments));
            },
             
                
                aggiungiDDT : function ()

            {
                return this.__call__("aggiungi_ddt_a_fattura", makeArray(arguments));
            }
                ,
             
                
                creaFattura : function ()

            {
                return this.__call__("crea_fattura", makeArray(arguments));
            }  ,
             
                
                creaFatturaPreview : function ()

            {
                return this.__call__("crea_fattura_preview", makeArray(arguments));
            }
            
             ,
             
                
                creaFatturaIstantanea : function ()

            {
                return this.__call__("crea_fattura_istantanea", makeArray(arguments));
            }  ,
             
                
                creaFatturaPreviewIstantanea : function ()

            {
                return this.__call__("crea_fattura_preview_istantanea", makeArray(arguments));
            }
            ,
                
                returnPagamenti : function ()

            {
                return this.__call__("return_pagamenti", makeArray(arguments));
            }
                ,
                
                stampaOrdineFornitore : function ()

            {
                return this.__call__("stampa_ordine_fornitore", makeArray(arguments));
            } ,
             
                
                creaFatturaIstantaneaAccredito : function ()

            {
                return this.__call__("crea_fattura_istantanea_accredito", makeArray(arguments));
            }  ,
             
                
                creaFatturaPreviewIstantaneaAccredito : function ()

            {
                return this.__call__("crea_fattura_preview_istantanea_accredito", makeArray(arguments));
            }
               ,
                stampaEtichetta : function ()

            {
                return this.__call__("stampa_etichetta", makeArray(arguments));
            }
               ,
               returnDescription : function ()

           {
               return this.__call__("return_description", makeArray(arguments));
           }
               ,
               stampaRcp : function ()

           {
               return this.__call__("stampa_rcp", makeArray(arguments));
           }
               
            
            
               
            
            
            }, Server);

            assert (isUndefined (justoop.gestionaleRpc), "PlcRpc already defined");

            //publish(justoop, { "PlcRpc": new PlcRpc(),"socket":socket });
            publish(justoop, { "gestionaleRpc": new gestionaleRpc()});
            

        })();
   
    
 })(justoop);
