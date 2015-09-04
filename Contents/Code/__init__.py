import re

FetchPost = SharedCodeService.fetch.FetchPost

FETCHTV_PREFIX = '/video/fetchtv'

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
    data = FetchPost(objectId, "BrowseDirectChildren")
    
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


