# coding=utf-8

redfish_mapper = None
redfish_version = None

class RedfishVersionMapping(object):
    """Implements basic url path mapping beetween Redfish versions."""

    def __init__(self, version):
        self.__version = version

    def map_sessionservice(self):
        if self.__version == "0.95":
            return "Sessions"
        return("SessionService")
        

    def map_links(self):
        if self.__version == "0.95":
            return "links"
        return("Links")  

    def map_links_ref(self):
        if self.__version == "0.95":
            return "href"
        return("@odata.id")
    
    def map_members(self):
        if self.__version == "0.95":
            return "Member"
        return("Members")