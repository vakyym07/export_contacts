from token_handler import TokenHandler
from urllib.parse import urlencode
from xml.etree.ElementTree import Element, tostring
import requests

REDIRECT_URI = 'http://localhost:8080/'


class Google:
    def __init__(self):
        self._id = '721315778135-uoaat3pp211voatarr6t2cn2d7un5m6s' \
                   '.apps.googleusercontent.com'
        self._secret = '-OpopX57ChIV3bGSU0EZnBcK'
        self.access_url = 'https://accounts.google.com' \
                          '/o/oauth2/v2/auth?scope=' \
                          'https://www.google.com/m8/feeds/&' \
                          'state=security_token&' \
                          'redirect_uri=%s&' \
                          'response_type=code&' \
                          'client_id=%s' % (REDIRECT_URI, self._id)
        self.data = {'client_id': self._id,
                     'client_secret': self._secret,
                     'redirect_uri': REDIRECT_URI,
                     'grant_type':  'authorization_code'}
        self.api = 'https://www.googleapis.com/oauth2/v4/token?' + \
                   urlencode(self.data) + '&code='
        self.name = 'google'
        self.token_handler = TokenHandler(
            self._id, self._secret, self.access_url, self.api, self.name)
        self.access_token = None

    def google_oauth(self):
        return self.token_handler.get_access_token()

    def create_xml(self, data):
        root = Element('atom:entry')
        root.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        root.set('xmlns:gd', 'http://schemas.google.com/g/2005')

        atom_category = Element('atom:category')
        atom_category.set('scheme', 'http://schemas.google.com/g/2005#kind')
        atom_category.set('term', 'http://schemas.google.com'
                                  '/contact/2008#contact')
        root.append(atom_category)

        atom_title = Element('atom:title')
        atom_title.set('type', 'text')
        atom_title.text = data['name']
        root.append(atom_title)

        atom_content = Element('atom:content')
        atom_content.set('type', 'text')
        atom_content.text = 'Instagram: ' + data['instagram'] + \
                            '\n' + 'Skype: ' + data['skype'] + \
                            '\n' + 'Birthday: ' + data['bdate']
        root.append(atom_content)

        email = Element('gd:email')
        email.set('rel', 'http://schemas.google.com/g/2005#work')
        email.set('address', data['email'])
        root.append(email)

        if data['home_phone'] != '':
            phone_number = Element('gd:phoneNumber')
            phone_number.set('rel', 'http://schemas.google.com/g/2005#work')
            phone_number.set('primary', 'true')
            phone_number.text = data['home_phone']
            root.append(phone_number)

        organization = Element('gd:organization')
        organization.set('rel', 'http://schemas.google.com/g/2005#work')
        org_name = Element('gd:orgName')
        org_name.text = data['occupation']
        organization.append(org_name)
        root.append(organization)

        im = Element('gd:im')
        im.set('address', data['email'])
        im.set('protocol', 'http://schemas.google.com/g/2005#GOOGLE_TALK')
        im.set('primary', 'true')
        im.set('rel', 'http://schemas.google.com/g/2005#home')
        root.append(im)

        bdata = Element('gd:birthday')
        bdata.set('rel', 'http://schemas.google.com/g/2005#work')
        bdata.set('primary', 'true')
        bdata.text = data['bdate']
        root.append(bdata)

        address = Element('gd:postalAddress')
        address.set('rel', 'http://schemas.google.com/g/2005#work')
        address.set('primary', 'true')
        address.text = data['city'] + ',\n' + data['country']
        root.append(address)

        link = Element('link')
        link.set('rel', 'http://schemas.google.com/'
                        'contacts/2008/rel#photo')
        link.set('type', 'image/*')
        link.set('href', data['picture'])
        root.append(link)

        return tostring(root)

    def create_contact(self, xml_data):
        if self.access_token is None:
            self.access_token = self.google_oauth()
        headers = {'Content-Type': 'application/atom+xml',
                   'GData-Version': '1.0'}
        requests.post('https://www.google.com/'
                      'm8/feeds/contacts/default/full?access_token=' +
                      self.access_token[0],
                      data=xml_data, headers=headers)
