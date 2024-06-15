import requests


def convert_headers(headers):
    def cd(a):
        for e in a.split(": ", 1):
            d[e[0]] = e[1]

    d = {}

    for x in headers.strip().split("\n"):
        cd(x)
    return d


def get_top2000_url():
    json_data = """
{"query":"query Tokens($channelSlug: String!) {
                core_channels(slug: $channelSlug) {
                    data {
                        live_audio {
                            token_url
                        }
                        live_video {
                            token_url
                        }
                    }
                }
            }","variables":{"channelSlug":"npo-radio-2"}}"""  # noqa
    session = requests.session()

    session.get("https://www.nporadio2.nl/online-radio-luisteren/gedraaid")

    url = "https://api.nporadio.nl/graphql"
    session.options(url, headers=convert_headers("""
Host: api.nporadio.nl
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type
Referer: https://www.nporadio2.nl/
Origin: https://www.nporadio2.nl
Connection: keep-alive
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: cross-site
Pragma: no-cache
Cache-Control: no-cache
"""))
    response = session.post(url, data=json_data, headers=convert_headers("""
Host: api.nporadio.nl
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/json;charset=utf-8
Content-Length: 437
Origin: https://www.nporadio2.nl
Connection: keep-alive
Referer: https://www.nporadio2.nl/
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: cross-site
Pragma: no-cache
Cache-Control: no-cache
TE: trailers"""))
    if not response.ok:
        print("ERROR At get_top2000_url")
        print(response.text)
        exit(0)

    data = response.json()

    token_url = data["data"]["core_channels"]["data"][0]["live_audio"]["token_url"]
    token = get_playertoken(session, token_url)

    player_data = """{"profileName":"dash","drmType":"widevine","referrerUrl":"https://www.nporadio2.nl/online-radio-luisteren/gedraaid"}"""  # noqa

    data = requests.post("https://prod.npoplayer.nl/stream-link", cookies={"Authorization": token}, data=player_data)
    print(data.json())


def get_playertoken(session, token_url):
    response = session.get(token_url)
    if not response.ok:
        print("ERROR At get_playertoken")
        print(response.text)
        exit(0)

    result = response.json()
    return result["playerToken"]


def main():
    url = get_top2000_url()


if __name__ == "__main__":
    main()
