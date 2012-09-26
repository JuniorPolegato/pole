/******************************************
 * Assinar de string XML via Python
 * 
 * Arquivo: PoleXmlSec.c
 * Versão.: 0.2.1
 * Autor..: Claudio Polegato Junior
 * Data...: 15 Mar 2011
 * 
 * Copyright © 2011 - Claudio Polegato Junior <junior@juniorpolegato.com.br>
 * Todos os direitos reservados
 * 
 * *****************************************
 * 
 * Compilar com:
 * 
 * gcc -Wall -shared -o PoleXmlSec.so PoleXmlSec.c -I /usr/include/python2.6/ -I /usr/include/libxml2 -I /usr/include/xmlsec1 -l xml2 -l xmlsec1 -l xmlsec1-openssl
 * 
 * Trechos de código extraídos e adaptados de xmlsec1.c versão 1.2.14 para a função xmlSecAppAddIDAttr e
 * página http://www.aleksey.com/xmlsec/api/xmlsec-notes-sign.html para assinador e função principal, além
 * de referência de como criar, compilar e usar CPython minha mesma em
 * http://br.dir.groups.yahoo.com/group/python-brasil/message/45544
 * 
 ******************************************/

#include <Python.h>

#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <libxml/tree.h>
#include <libxml/xmlmemory.h>
#include <libxml/parser.h>

#ifndef XMLSEC_NO_XSLT
#include <libxslt/xslt.h>
#endif /* XMLSEC_NO_XSLT */

#define XMLSEC_CRYPTO_OPENSSL

//#define XMLSEC_CRYPTO_DYNAMIC_LOADING

//#define XMLSEC_CRYPTO "openssl"

#include <xmlsec/xmlsec.h>
#include <xmlsec/xmltree.h>
#include <xmlsec/xmldsig.h>
#include <xmlsec/crypto.h>

static int  
xmlSecAppAddIDAttr(xmlNodePtr node, const xmlChar* attrName, const xmlChar* nodeName, const xmlChar* nsHref) {
    xmlAttrPtr attr, tmpAttr;
    xmlNodePtr cur;
    xmlChar* id;

    if((node == NULL) || (attrName == NULL) || (nodeName == NULL)) {
        return(-1);
    }

    /* process children first because it does not matter much but does simplify code */
    cur = xmlSecGetNextElementNode(node->children);
    while(cur != NULL) {
        if(xmlSecAppAddIDAttr(cur, attrName, nodeName, nsHref) < 0) {
            return(-1);
        }
        cur = xmlSecGetNextElementNode(cur->next);
    }

    /* node name must match */
    if(!xmlStrEqual(node->name, nodeName)) {
        return(0);
    }

    /* if nsHref is set then it also should match */    
    if((nsHref != NULL) && (node->ns != NULL) && (!xmlStrEqual(nsHref, node->ns->href))) {
        return(0);
    }

    /* the attribute with name equal to attrName should exist */
    for(attr = node->properties; attr != NULL; attr = attr->next) {
        if(xmlStrEqual(attr->name, attrName)) {
            break;
        }
    }
    if(attr == NULL) {
        return(0);
    }

    /* and this attr should have a value */
    id = xmlNodeListGetString(node->doc, attr->children, 1);
    if(id == NULL) {
        return(0);
    }

    /* check that we don't have same ID already */
    tmpAttr = xmlGetID(node->doc, id);
    if(tmpAttr == NULL) {
        xmlAddID(NULL, node->doc, id, attr);
    } else if(tmpAttr != attr) {
        fprintf(stderr, "Error: duplicate ID attribute \"%s\"\n", id);        
        xmlFree(id);
        return(-1);
    }
    xmlFree(id);
    return(0);
}

static PyObject*
sign_xml(const char* xml_string, const char* key_file, const char* cert_file, const char* id_attr_name, const char* id_node_name) {
    xmlDocPtr doc = NULL;
    xmlNodePtr node = NULL;
    xmlSecDSigCtxPtr dsigCtx = NULL;
    xmlChar *signed_xml;
    int size;
    PyObject *result;

    assert(xml_string);
    assert(key_file);
    assert(cert_file);

    /* load template */
    doc = xmlParseDoc((xmlChar*)xml_string);
    if ((doc == NULL) || (xmlDocGetRootElement(doc) == NULL)){
        fprintf(stderr, "Error: unable to parse xml string!\n");
        goto done;
    }

    /* add id */
    if (id_attr_name && id_node_name && *id_attr_name != '\0' && *id_node_name != '\0')
        xmlSecAppAddIDAttr(xmlDocGetRootElement(doc), (xmlChar*)id_attr_name, (xmlChar*)id_node_name, NULL);

    /* find start node */
    node = xmlSecFindNode(xmlDocGetRootElement(doc), xmlSecNodeSignature, xmlSecDSigNs);
    if(node == NULL) {
        fprintf(stderr, "Error: start node <Signature> not found in xml string\n");
        goto done;      
    }

    /* create signature context, we don't need keys manager in this example */
    dsigCtx = xmlSecDSigCtxCreate(NULL);
    if(dsigCtx == NULL) {
        fprintf(stderr,"Error: failed to create signature context\n");
        goto done;
    }

    /* load private key, assuming that there is not password */
    dsigCtx->signKey = xmlSecCryptoAppKeyLoad(key_file, xmlSecKeyDataFormatPem, NULL, NULL, NULL);
    if(dsigCtx->signKey == NULL) {
        fprintf(stderr,"Error: failed to load private pem key from \"%s\"\n", key_file);
        goto done;
    }

    /* set key name to the file name */
    if(xmlSecKeySetName(dsigCtx->signKey, (xmlChar*)key_file) < 0) {
        fprintf(stderr,"Error: failed to set key name for key from \"%s\"\n", key_file);
        goto done;
    }

    /* set cert name to the file name */
    if(xmlSecCryptoAppKeyCertLoad(dsigCtx->signKey, cert_file, xmlSecKeyDataFormatPem) < 0) {
        fprintf(stderr,"Error: failed to set cert name for cert from \"%s\"\n", cert_file);
        goto done;
    }

    /* sign the template */
    if(xmlSecDSigCtxSign(dsigCtx, node) < 0) {
        fprintf(stderr,"Error: signature failed\n");
        goto done;
    }

done:
    /* cleanup */
    if(dsigCtx != NULL) {
        xmlSecDSigCtxDestroy(dsigCtx);
    }

    if(doc != NULL) {
        xmlDocDumpMemory(doc, &signed_xml, &size);
        result = Py_BuildValue("s", signed_xml);
        xmlFree(signed_xml);
        xmlFreeDoc(doc); 
    }
    else {
        result = Py_BuildValue("s", NULL);
    }

    return result;
}

xmlSecKeysMngrPtr 
load_trusted_certs(const char** files, int files_size) {
    xmlSecKeysMngrPtr mngr;
    int i;
        
    assert(files);
    assert(files_size > 0);
    
    /* create and initialize keys manager, we use a simple list based
     * keys manager, implement your own xmlSecKeysStore klass if you need
     * something more sophisticated 
     */
    mngr = xmlSecKeysMngrCreate();
    if(mngr == NULL) {
        fprintf(stderr, "Error: failed to create keys manager.\n");
        return(NULL);
    }
    if(xmlSecCryptoAppDefaultKeysMngrInit(mngr) < 0) {
        fprintf(stderr, "Error: failed to initialize keys manager.\n");
        xmlSecKeysMngrDestroy(mngr);
        return(NULL);
    }    
    
    for(i = 0; i < files_size; ++i) {
        assert(files[i]);

        /* load trusted cert */
        if(xmlSecCryptoAppKeysMngrCertLoad(mngr, files[i], xmlSecKeyDataFormatPem, xmlSecKeyDataTypeTrusted) < 0) {
            fprintf(stderr,"Error: failed to load pem certificate from \"%s\"\n", files[i]);
            xmlSecKeysMngrDestroy(mngr);
            return(NULL);
        }
    }

    return(mngr);
}

int 
verify_xml(xmlSecKeysMngrPtr mngr, const char* xml_string, const char* id_attr_name, const char* id_node_name) {
    xmlDocPtr doc = NULL;
    xmlNodePtr node = NULL;
    xmlSecDSigCtxPtr dsigCtx = NULL;
    int res = -1;
    
    assert(mngr);
    assert(xml_string);

    /* load template */
    doc = xmlParseDoc((xmlChar*)xml_string);
    if ((doc == NULL) || (xmlDocGetRootElement(doc) == NULL)){
        fprintf(stderr, "Error: unable to parse xml string\n");
        goto done2;
    }

    /* add id */
    if (id_attr_name && id_node_name)
        xmlSecAppAddIDAttr(xmlDocGetRootElement(doc), (xmlChar*)id_attr_name, (xmlChar*)id_node_name, NULL);

    /* find start node */
    node = xmlSecFindNode(xmlDocGetRootElement(doc), xmlSecNodeSignature, xmlSecDSigNs);
    if(node == NULL) {
        fprintf(stderr, "Error: start node not found in xml string\n");
        goto done2;
    }

    /* create signature context */
    dsigCtx = xmlSecDSigCtxCreate(mngr);
    if(dsigCtx == NULL) {
        fprintf(stderr,"Error: failed to create signature context\n");
        goto done2;
    }

    /* Verify signature */
    if(xmlSecDSigCtxVerify(dsigCtx, node) < 0) {
        fprintf(stderr,"Error: signature verify\n");
        goto done2;
    }
        
    res = (dsigCtx->status == xmlSecDSigStatusSucceeded);

done2:    
    /* cleanup */
    if(dsigCtx != NULL) {
        xmlSecDSigCtxDestroy(dsigCtx);
    }
    
    if(doc != NULL) {
        xmlFreeDoc(doc); 
    }
    return(res);
}

static PyObject *
PoleXmlSec_assinar(PyObject *self, PyObject *args)
{
    const char *xml, *chave, *certificado, *nome_atributo_id, *nome_no_id;
    PyObject* result;

    if (!PyArg_ParseTuple(args, "sssss", &xml, &chave, &certificado, &nome_atributo_id, &nome_no_id))
        return NULL;
        
    result = Py_BuildValue("s", xml);

    /* Init libxml and libxslt libraries */
    xmlInitParser();
    LIBXML_TEST_VERSION
    xmlLoadExtDtdDefaultValue = XML_DETECT_IDS | XML_COMPLETE_ATTRS;
    xmlSubstituteEntitiesDefault(1);
#ifndef XMLSEC_NO_XSLT
    xmlIndentTreeOutput = 1; 
#endif /* XMLSEC_NO_XSLT */
                
    /* Init xmlsec library */
    if(xmlSecInit() < 0) {
        fprintf(stderr, "Error: xmlsec initialization failed.\n");
        return result;
    }

    /* Check loaded library version */
    if(xmlSecCheckVersion() != 1) {
        fprintf(stderr, "Error: loaded xmlsec library version is not compatible.\n");
        return result;
    }

    /* Load default crypto engine if we are supporting dynamic
     * loading for xmlsec-crypto libraries. Use the crypto library
     * name ("openssl", "nss", etc.) to load corresponding 
     * xmlsec-crypto library.
     */
#ifdef XMLSEC_CRYPTO_DYNAMIC_LOADING
    if(xmlSecCryptoDLLoadLibrary(BAD_CAST XMLSEC_CRYPTO) < 0) {
        fprintf(stderr, "Error: unable to load default xmlsec-crypto library. Make sure\n"
                        "that you have it installed and check shared libraries path\n"
                        "(LD_LIBRARY_PATH) envornment variable.\n");
        return result;
    }
#endif /* XMLSEC_CRYPTO_DYNAMIC_LOADING */

    /* Init crypto library */
    if(xmlSecCryptoAppInit(NULL) < 0) {
        fprintf(stderr, "Error: crypto initialization failed.\n");
        return result;
    }

    /* Init xmlsec-crypto library */
    if(xmlSecCryptoInit() < 0) {
        fprintf(stderr, "Error: xmlsec-crypto initialization failed.\n");
        return result;
    }

    result = sign_xml(xml, chave, certificado, nome_atributo_id, nome_no_id);

    /* Shutdown xmlsec-crypto library */
    xmlSecCryptoShutdown();

    /* Shutdown xmlsec library */
    xmlSecShutdown();

    /* Shutdown crypto library */
    /* Se executar essa linha dá erro na conexão HTTPS */
    //xmlSecCryptoAppShutdown();

    /* Shutdown libxslt/libxml/libxmlsec1 */
#ifndef XMLSEC_NO_XSLT
    xsltCleanupGlobals();            
#endif /* XMLSEC_NO_XSLT */
    xmlCleanupParser();

    return result;
}

static PyObject *
PoleXmlSec_verificar(PyObject *self, PyObject *args)
{
    const char *xml, *certificadora, *nome_atributo_id, *nome_no_id;
    int verified = -1;
    PyObject* result;
    xmlSecKeysMngrPtr mngr;

    if (!PyArg_ParseTuple(args, "ssss", &xml, &certificadora, &nome_atributo_id, &nome_no_id))
        return NULL;

    result = Py_BuildValue("b", verified);

    /* Init libxml and libxslt libraries */
    xmlInitParser();
    LIBXML_TEST_VERSION
    xmlLoadExtDtdDefaultValue = XML_DETECT_IDS | XML_COMPLETE_ATTRS;
    xmlSubstituteEntitiesDefault(1);
#ifndef XMLSEC_NO_XSLT
    xmlIndentTreeOutput = 1; 
#endif /* XMLSEC_NO_XSLT */
                
    /* Init xmlsec library */
    if(xmlSecInit() < 0) {
        fprintf(stderr, "Error: xmlsec initialization failed.\n");
        return result;
    }

    /* Check loaded library version */
    if(xmlSecCheckVersion() != 1) {
        fprintf(stderr, "Error: loaded xmlsec library version is not compatible.\n");
        return result;
    }

    /* Load default crypto engine if we are supporting dynamic
     * loading for xmlsec-crypto libraries. Use the crypto library
     * name ("openssl", "nss", etc.) to load corresponding 
     * xmlsec-crypto library.
     */
#ifdef XMLSEC_CRYPTO_DYNAMIC_LOADING
    if(xmlSecCryptoDLLoadLibrary(BAD_CAST XMLSEC_CRYPTO) < 0) {
        fprintf(stderr, "Error: unable to load default xmlsec-crypto library. Make sure\n"
                        "that you have it installed and check shared libraries path\n"
                        "(LD_LIBRARY_PATH) envornment variable.\n");
        return result;
    }
#endif /* XMLSEC_CRYPTO_DYNAMIC_LOADING */

    /* Init crypto library */
    if(xmlSecCryptoAppInit(NULL) < 0) {
        fprintf(stderr, "Error: crypto initialization failed.\n");
        return result;
    }

    /* Init xmlsec-crypto library */
    if(xmlSecCryptoInit() < 0) {
        fprintf(stderr, "Error: xmlsec-crypto initialization failed.\n");
        return result;
    }

    /* create keys manager and load trusted certificates */
    mngr = load_trusted_certs(&certificadora, 1);
    if(mngr == NULL) {
        return result;
    }
    verified = verify_xml(mngr, xml, nome_atributo_id, nome_no_id);

    /* Shutdown xmlsec-crypto library */
    xmlSecCryptoShutdown();

    /* Shutdown xmlsec library */
    xmlSecShutdown();

    /* Shutdown crypto library */
    /* Se executar essa linha dá erro na conexão HTTPS */
    //xmlSecCryptoAppShutdown();

    /* Shutdown libxslt/libxml/libxmlsec1 */
#ifndef XMLSEC_NO_XSLT
    xsltCleanupGlobals();            
#endif /* XMLSEC_NO_XSLT */
    xmlCleanupParser();

    return result;
}

static PyMethodDef PoleXmlSec_methods[] = {
    {"assinar",  PoleXmlSec_assinar, METH_VARARGS,
     "Assina um xml com chave privada e certificado X509 no formato PEM sem senha.\n"
     "Uso: assinar(xml, arquivo_chave, arquivo_certificado, nome_atributo_id, nome_nó_id)\n"
     "Parâmetros: cinco strings cujo nome diz o que é.\n"
     "Retorno: xml assinado, string."},
    {"verificar",  PoleXmlSec_verificar, METH_VARARGS,
     "Verifica a assinatura de um xml com certificado X509.\n"
     "Uso: verificar(xml, nome_atributo_id, nome_nó_id)\n"
     "Parâmetros: três strings cujo nome diz o que é.\n"
     "Retorno: True se confere e False se não confere, boolean."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyMODINIT_FUNC
initPoleXmlSec(void)
{
    (void) Py_InitModule("PoleXmlSec", PoleXmlSec_methods);
}
