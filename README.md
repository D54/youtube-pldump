## Requirements to run the script
#### Dependencies

- requests
- pyyaml

#### client_secret.json
In the same folder as the script

[HOWTO](https://developers.google.com/api-client-library/python/auth/installed-app#creatingcred)

Sample:
```
{
    "installed": {
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "client_id": "000000000000-00000000000000000000000000000000.apps.googleusercontent.com",
        "client_secret": "000000000000000000000000",
        "project_id": "youtube-pldump",
        "redirect_uris": [
            "urn:ietf:wg:oauth:2.0:oob",
            "http://localhost"
        ],
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}
```

## Usage

```
$ > python ytpld.py
```

## Convert yaml to json
```
$ > python y2j.py dump.yaml dump.json
```
