from urllib.error import URLError, HTTPError
from TokenHandler import TokenHandler
from urllib.request import urlopen
from urllib.parse import urlencode
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import requests

REDIRECT_URI = 'http://localhost:8080/'


class Google:
    def __init__(self):
        self._id = '721315778135-uoaat3pp211voatarr6t2cn2d7un5m6s.apps.googleusercontent.com'
        self._secret = '-OpopX57ChIV3bGSU0EZnBcK'
        self.access_url = 'https://accounts.google.com/o/oauth2/v2/auth?scope=https://www.google.com/m8/feeds/&' \
                          'state=security_token&' \
                          'redirect_uri=%s&' \
                          'response_type=code&' \
                          'client_id=%s' % (REDIRECT_URI, self._id)
        self.data = {'client_id': self._id,
                     'client_secret': self._secret,
                     'redirect_uri': REDIRECT_URI,
                     'grant_type':  'authorization_code'}
        self.api = 'https://www.googleapis.com/oauth2/v4/token?' + urlencode(self.data) + '&code='
        self.name = 'google'
        self.token_handler = TokenHandler(self._id, self._secret, self.access_url, self.api, self.name)
        self.access_token = self.google_oauth()

    def google_oauth(self):
        return self.token_handler.get_access_token()

    def create_xml(self, data):

        root = Element('atom:entry')
        root.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        root.set('xmlns:gd', 'http://schemas.google.com/g/2005')

        atom_category = Element('atom:category')
        atom_category.set('scheme', 'http://schemas.google.com/g/2005#kind')
        atom_category.set('term', 'http://schemas.google.com/contact/2008#contact')
        root.append(atom_category)

        atom_content = Element('atom:content')
        atom_content.set('type', 'text')
        atom_content.text = 'Notes'
        root.append(atom_content)

        name = Element('gd:name')
        given_name = Element('d:givenName')
        given_name.text = data['first_name']
        family_name = Element('gd:familyName')
        family_name.text = data['last_name']
        full_name = Element('gd:fullName')
        if data.get(name) is not None:
            full_name.text = data['name'].decode('utf-8')
        else:
            full_name.text = data['first_name'] + ' ' + data['last_name']
        name.append(given_name)
        name.append(family_name)
        name.append(full_name)
        root.append(name)

        if data.get('email') is not None:
            email = Element('gd:email')
            email.set('rel', 'http://schemas.google.com/g/2005#home')
            email.set('address', data['email'])
            root.append(email)

        if data.get('home_phone'):
            if data['home_phone'] != '':
                phone_number = Element('gd:phoneNumber')
                phone_number.set('rel', 'http://schemas.google.com/g/2005#work')
                phone_number.set('primary', 'true')
                phone_number.text = data['home_phone']
                root.append(phone_number)

        if data.get('occupation') is not None:
            organization = Element('gd:organization')
            organization.set('rel', 'http://schemas.google.com/g/2005#work')
            org_name = Element('gd:orgName')
            org_name.text = data['occupation']
            organization.append(org_name)
            root.append(organization)

        if data.get('city') is not None and data.get('country') is not None:
            adress = Element('gd:structuredPostalAddress')
            adress.set('rel', 'http://schemas.google.com/g/2005#work')
            adress.set('primary', 'true')
            city = Element('gd:city')
            city.text = data['city']
            country = Element('gd:country')
            country.text = data['country']
            adress.append(city)
            adress.append(country)
            root.append(adress)

        return tostring(root)

    def create_contact(self, xml_data):
        headers = {'Content-Type': 'application/atom+xml', 'GData-Version': '3.0'}
        r = requests.post('https://www.google.com/m8/feeds/contacts/default/full?access_token='+self.access_token,
                          data=xml_data, headers=headers)
        print(r.text)
        print(r.status_code)
