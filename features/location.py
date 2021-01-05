def getLocation(address):
    if address['city'] != address['state_district']:
        address_output =  "Sir, your current location is in city "+address['city']+", district "+address['state_district']+" and state "+address['state']+"in "+address['country']+". Your postal code is "+address['postcode']+"."
        return address_output
    else:
        address_output =  "Sir, your current location is in city "+address['city']+" and state "+address['state']+"in "+address['country']+". Your postal code is "+address['postcode']+"."
        return address_output