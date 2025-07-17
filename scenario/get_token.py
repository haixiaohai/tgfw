import requests
import json
import urllib3

urllib3.disable_warnings()


def get_ipadd():
    ip_add = "10.113.55.147"
    return ip_add


def get_token():
    # url = "https://" + get_ipadd() + "/api/v1/auth"
    # url_out = "https://" + get_ipadd() + "/api/v1/logout"

    # payload = json.dumps({
    #     "id": "admin",
    #     "val": {
    #         "username": "admin",
    #         "passwd": "Tmdmd0AxMjM=",
    #         "action": "login",
    #         "autht": 0,
    #         "code": ""
    #     }
    # })
    # headers = {
    #     'Content-Type': 'application/json'
    # }

    # response = requests.request("PUT", url, headers=headers, data=payload, verify=False)
    # response1 = requests.request("GET", url_out, headers=headers, data=payload, verify=False)
    # response_text = response.text
    # get_token = json.loads(response_text)
    # token = get_token.get('token')
    # token = 'UxBocadnjjygnqxfQpqtDyGzbPdpiE!jSnbrbm@!XDwboicyulDBp!$qbrhIYfCozVPG#SDy@CT!PYkbWbcx!kfEFocAqwDYNVPOX#mqo!cydLrasQ@bugSMQoeONdqO'
    # token = '!McMyuIzWdrCgJzezjHHAGpuLTaNJHAjZezxsWfPFEqzQnehgtjGNsVljLRAANtZQlVOGyhgTQElLgC@#iQGkdjXCuDPr@lrxJfWLoAshqDIudHzzblxPvNhnf@FGaCl'
    token = 'JAljtiEemGkmtyvslK!rizfFyPpbGbbS@mlT!lAHzpPqKLoKNAubtaamtYVjrLfYpbjMCCfAYWrkkjUNYTkan!ItYCNZIfiIunJbscSkmBKHQbFDGrJaYDeJwbj@ccSF'
    return token

