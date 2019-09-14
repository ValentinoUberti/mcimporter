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
          
            var produzioneRpc = subclass(  {

                __url__ : "/gestionale/produzione/call/jsonrpc",
                  

            
            returnLavorazioneNameFromid : function ()

            {
                return this.__call__("return_lavorazione_name_from_id", makeArray(arguments));
            },
            
            saveLavorazioniPerArticolo : function ()

            {
                return this.__call__("save_lavorazioni_per_articolo", makeArray(arguments));
            },
            
            stampLavorazioniPerArticolo : function ()

            {
                return this.__call__("stampa_lavorazioni_per_ordine_e_articolo", makeArray(arguments));
            }
               
            
            
               
            
            
            }, Server);

            assert (isUndefined (justoop.produzioneRpc), "Produzione Rpc already defined");

            
            publish(justoop, { "produzioneRpc": new produzioneRpc()});
            

        })();
   
    
 })(justoop);
