import re

try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2

unescape = HTMLParser().unescape

FETCHTV_PREFIX = '/video/fetchtv'
FETCHTV_URL = 'http://172.16.1.15:49152/web/cds_control'

####################################################################################################
def Start():
    ObjectContainer.title1 = 'FetchTV'
    HTTP.ClearCache()
    HTTP.Headers['User-Agent'] = 'Darwin/14.4.0, UPnP/1.0, Portable SDK for UPnP devices/1.6.18'

####################################################################################################
@handler(FETCHTV_PREFIX, 'FetchTV')
def MainMenu():
    return GetContainer('1', L('Recordings'))

####################################################################################################
@route(FETCHTV_PREFIX + '/{objectId}', allow_sync=True)
def GetContainer(objectId, title):
    data = Post(objectId)
    
    if data.find("{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}container") == None:
        return GetContent(data.findall("{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}item"), title)
    
    oc = ObjectContainer(
        title2 = title
    )
    
    for k, v in (data.getchildren()):
        parent = v.getparent()
        oc.add(
            TVShowObject(
                key     = Callback(GetContainer, objectId=parent.get("id"), title = v.text),
                rating_key = FETCHTV_PREFIX + "/container" + parent.get("id"),
                title   = v.text,
                thumb   = R("icon-default.png")
            )
        )
    
    return oc

####################################################################################################
def GetContent(items, label):
    oc = ObjectContainer(
        title1 = label,
    )

    for v in list(items):        
        oc.add(
            URLService.MetadataObjectForURL(v.find("{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}res").text)
        )

    oc.objects.sort(key=lambda obj: obj.originally_available_at)
        
    return oc
    
####################################################################################################
def Post(objectId):
    postData = getSoapEnvelope(objectId)
    result = HTTP.Request(FETCHTV_URL, headers={"Content-Type": "text/xml", "SOAPACTION": '"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"'}, data=postData, cacheTime=0)
    xml = XML.ObjectFromString(result.content)
    
    str = unescape(xml.Body["{urn:schemas-upnp-org:service:ContentDirectory:1}BrowseResponse"]["{}Result"].text)
    str = str.replace("&", "&amp;")
    
    return XML.ElementFromString(str)

####################################################################################################
def getSoapEnvelope(objectId):
    return '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'\
            '<s:Body><u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">'\
            '<ObjectID>' + objectId + '</ObjectID>'\
            '<BrowseFlag>BrowseDirectChildren</BrowseFlag>'\
            '<Filter>*</Filter>'\
            '<StartingIndex>0</StartingIndex>'\
            '<RequestedCount>0</RequestedCount>'\
            '<SortCriteria></SortCriteria>'\
            '</u:Browse>'\
            '</s:Body>'\
            '</s:Envelope>'
