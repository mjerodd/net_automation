import requests
import warnings
import json

warnings.filterwarnings("ignore", message="Unverified HTTPS request")


class RuckusInt:
    url = "https://ruckus.kyderby.com:8443/wsg/api/public/"

    def ruckus_auth(self, username, password):
        creds = {'username': username, 'password': password}
        st_req = f"{self.url}v11_0/serviceTicket"
        r = requests.post(st_req, json=creds, verify=False)
        #print(type(r))
        cookie = r.headers['Set-Cookie']
        resp = r.json()
        #print(resp)
        ticket = resp["serviceTicket"]
        response = {"ticket": ticket, "Cookie": cookie}
        return response

    def get_all_zones(self, auth_resp):
        headers = {
            'Content-Type': 'application/json',
            'Cookie': auth_resp['Cookie'],
        }

        payload = json.dumps({
            "username": "m.thomas@kyderby.com",
            "password": "Marvelou5marv77@"
        })
        print(f"{self.url}/wsg/api/public/v11_0/rkszones?serviceTicket={auth_resp['ticket']}")
        call_url = f"{self.url}/wsg/api/public/v11_0/rkszones?serviceTicket={auth_resp['ticket']}"
        print(auth_resp['ticket'])

        #req = requests.get(call_url, headers=headers, verify=False)
        req = requests.request("GET", call_url, headers=headers, data=payload, verify=False)
        z_resp = req.json()
        print(req.status_code)
        print(z_resp)
        zones = z_resp['list']
        return zones



ruckus_conn = RuckusInt()
tick = ruckus_conn.ruckus_auth("m.thomas@kyderby.com", "Marvelou5marv77@")
print(tick)
ruckus_zl = ruckus_conn.get_all_zones(tick)
print(ruckus_zl)





