import bpy, hashlib, base64, random, urllib, threading, webbrowser, pathlib, os, http, shutil, time, requests, re

def register(utils, package):
    PAGE_PATH = pathlib.Path(__file__).parent.parent.joinpath("oauth2_page.html")

    CLIENT_ID = str(9176813044105178389)
    PORT = 50540
    REDIRECT_URI = urllib.parse.quote(f"http://localhost:{PORT}")

    def base64url_encode(bytes):
        return base64.urlsafe_b64encode(bytes).decode("UTF-8").replace("=", "")
    def generate_random_string():
        return base64url_encode(random.getrandbits(32 * 8).to_bytes(32, "little"))
    def get_request_url(**kwargs):
        for k, v in kwargs.items():
            kwargs[k] = urllib.parse.quote(str(v))
        return (
            "https://apis.roblox.com/oauth/v1/authorize?"
            f"client_id={CLIENT_ID}"
            f"&code_challenge={kwargs['code_challenge']}"
            "&code_challenge_method=S256"
            f"&redirect_uri={REDIRECT_URI}"
            f"&scope={kwargs['scope']}"
            "&response_type=code"
            f"&state={kwargs['state']}"
        )
    
    outgoing_requests = {}
    lookup_tokens = {}
    def compare_scopes(scopes_set, scopes_str):
        return scopes_set == frozenset(re.split("\s+", scopes_str))
    def get_refresh_token(scopes_set):
        for refresh_token_prefs in utils.prefs.refresh_tokens.values():
            if compare_scopes(scopes_set, refresh_token_prefs.scopes_str):
                return refresh_token_prefs.refresh_token
    def delete_refresh_token(refresh_token):
        if refresh_token in lookup_tokens:
            del lookup_tokens[refresh_token]
        index = 0
        refresh_tokens = utils.prefs.refresh_tokens
        for refresh_token_prefs in refresh_tokens.values():
            if refresh_token_prefs.refresh_token == refresh_token:
                refresh_tokens.remove(index)
                return
            index += 1
    def add_refresh_token(refresh_token, scopes_str, access_token, request_time, expires_in):
        refresh_token_prefs = utils.prefs.refresh_tokens.add()
        refresh_token_prefs.refresh_token = refresh_token
        refresh_token_prefs.scopes_str = scopes_str
        lookup_tokens[refresh_token] = (access_token, request_time, expires_in)

    def get_access_token(scopes_set, callback):
        scopes_str = " ".join(scopes_set)
        refresh_token = get_refresh_token(scopes_set)
        if refresh_token in lookup_tokens:
            access_token, grant_time, expires_in = lookup_tokens[refresh_token]
            if (time.process_time() - grant_time) < (expires_in - 10):
                callback(access_token)
                return

        if refresh_token:
            delete_refresh_token(refresh_token)
            request_time = time.process_time()
            response = requests.post(
                "https://apis.roblox.com/oauth/v1/token", 
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": CLIENT_ID,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            if response.ok:
                response_dict = response.json()
                add_refresh_token(
                    response_dict["refresh_token"], 
                    scopes_str, 
                    response_dict["access_token"], 
                    request_time, 
                    response_dict["expires_in"]
                )
                callback(response_dict["access_token"])
                return

        code_verifier = generate_random_string()
        code_challenge = base64url_encode(hashlib.sha256(code_verifier.encode("UTF-8")).digest())
        state = generate_random_string()

        def request_callback(queries=None):
            del outgoing_requests[state]
            if queries:
                request_time = time.process_time()
                response = requests.post(
                    "https://apis.roblox.com/oauth/v1/token", 
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "client_id": CLIENT_ID, 
                        "code": queries["code"],
                        "code_verifier": code_verifier,
                        "grant_type": "authorization_code"
                    }
                )
                if response.ok:
                    response_dict = response.json()
                    add_refresh_token(
                        response_dict["refresh_token"], 
                        scopes_str, 
                        response_dict["access_token"], 
                        request_time, 
                        response_dict["expires_in"]
                    )
                    callback(response_dict["access_token"])
            else:
                callback()
        outgoing_requests[state] = request_callback
        webbrowser.open_new_tab(get_request_url(
            code_challenge=code_challenge,
            scope=scopes_str,
            state=state
        ))

    access_token_requests = {}
    global request
    def request(method, url, *, scopes, headers={}, data=None, callback):
        def do_request(access_token=None):
            reason = None
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
                headers["Content-Type"] = "application/json"
                response = requests.request(method, url, headers=headers, data=data)
                if response.ok:
                    callback(True, response_dict=response.json(), response=response)
                    return
                else:
                    reason = response.reason
            else:
                reason = "Failed to authorize access"
            print(method, url, "failed: ", reason)
            callback(False, reason=reason)

        scopes_set = frozenset(scopes)
        if not scopes_set in access_token_requests:
            access_token_requests[scopes_set] = []
        access_token_requests[scopes_set].append(do_request)

        def access_token_callback(access_token=None):
            if scopes_set in access_token_requests:
                while len(access_token_requests[scopes_set]) > 0:
                    threading.Thread(target=access_token_requests[scopes_set].pop(0), args=(access_token,)).run()
                del access_token_requests[scopes_set]
        threading.Thread(target=get_access_token, args=(scopes_set, access_token_callback)).run()

    class ServerHandler(http.server.BaseHTTPRequestHandler):
        server_version = ""
        sys_version = ""
        
        def do_GET(self):
            queries = {}
            for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).items():
                queries[k] = v[0]
            if "state" in queries:
                state = queries["state"]
                if state in outgoing_requests:
                    threading.Thread(target=outgoing_requests[state], args=(queries,)).run()

            with open(PAGE_PATH, "rb") as f:
                fs = os.fstat(f.fileno())
                self.send_response(http.HTTPStatus.OK)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(fs[6]))
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)

    class ServerThread(threading.Thread):
        def run(self):
            self.server = http.server.HTTPServer(("localhost", PORT), ServerHandler)
            self.server.serve_forever()
        
        def stop(self):
            if hasattr(self, "server"):
                self.server.shutdown()
                self.server.server_close()

    class RefreshTokenPrefs(bpy.types.PropertyGroup):
        refresh_token: bpy.props.StringProperty()
        scopes_str: bpy.props.StringProperty()

    def unregister():
        outgoing_requests_callbacks = list(outgoing_requests.values())
        for callback in outgoing_requests_callbacks:
            callback()
        for callbacks in access_token_requests.values():
            for callback in callbacks:
                callback()
    return {
        "classes": (RefreshTokenPrefs,),
        "prefs": {"refresh_tokens": bpy.props.CollectionProperty(type=RefreshTokenPrefs),},
        "threads": (ServerThread(name = "blender_roblox_sync OAuth2.0 Client"),),
        "unregister": unregister
    }