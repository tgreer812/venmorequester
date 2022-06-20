import argparse
import logging
import requests
import time
import pprint

LOG_FORMAT = "[%(levelname)s] %(message)s"
LOG_DEBUG_FORMAT = "[%(threadName)s-%(filename)s-%(funcName)s-%(lineno)s | %(levelname)s] %(message)s"

log = logging.getLogger(__name__)

def print_debug(request_object, show_request_body=False, show_response_body=False):
    print()
    print(request_object.request.method + " " + request_object.request.url)
    #print(request_object.request.headers)
    for k,v in request_object.request.headers.items():
        print(k + ": " + v)
    
    if show_request_body:
        print(request_object.request.body)

    print("\n")
    print(request_object.status_code)
    print("")
    print(request_object.headers)
    print()
    if show_response_body:
        print(request_object.text)

def save_progress(x, y, **kwargs):

    with open(kwargs['progress'],'w') as fd:
        progress_line = f"{x} {y}"
        log.debug(f"Saving {x} {y}")
        fd.write(progress_line)



def run(args, **kwargs):

    '''
    progress_line = ''
    with open(kwargs['progress'],'r') as fd:
        progress_line = fd.read().strip()  

    if(len(progress_line) == 0):
        progress_line = "0 0"

    current_x = int(progress_line.split(' ')[0])
    current_y = int(progress_line.split(' ')[1])
    progress_set = False
    '''

    my_session = 0
    target_domain = "https://venmo.com"
    account_target_domain = "https://account.venmo.com"
    test_domain = "http://127.0.0.1"
    venmo_otp_secret = ''
    '''
    Log in with user creds
    '''
    try:
        # create new session object
        my_session = requests.Session()

        
        # create and add Chrome user agent header (Venmo requires a valid browser)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
        }
        my_session.headers = headers

        # send get request to access the account page
        r = my_session.get(target_domain + "/account/sign-in")

        #print(r.status_code)
        #pprint.pprint(r.headers)

        # Set Content-Type header for the login POST request
        my_session.headers["Content-Type"] = "application/x-www-form-urlencoded"

        # Send login POST
        login_data = f'return_json=true&password={kwargs["password"]}&phoneEmailUsername={kwargs["username"]}'
        r = my_session.post(target_domain + "/login",data=login_data)

        # Handle 2F if present
        if r.status_code == 401:
            
            #strip content length headers
            my_session.headers.pop("Content-Type")

            # save secret
            venmo_otp_secret = r.headers.get('Venmo-Otp-Secret')

            # send request for the 2F page
            r = my_session.get(
                account_target_domain + 
                f"/account/mfa/code-prompt?k={r.headers.get('Venmo-Otp-Secret')}" +
                "&next=%2Faccount%2Flogout"
            )

            # extract the _next data URL
            left = r.text.find("buildId") + 10
            right = r.text.find("\"", left)
            build_ID = r.text[left:right]

            # extract the Csrf token
            left = r.text.find("csrfToken") + 12
            right = r.text.find("\"",left)

            csrf_token = r.text[left:right]

            print(csrf_token)

            # send the POST specifying 2F type (i.e sms)
            my_session.headers["Content-Type"]      = "application/json"
            my_session.headers["Csrf-Token"]        = csrf_token
            my_session.headers["Xsrf-Token"]        = csrf_token
            my_session.headers["Venmo-Otp-Secret"]  = venmo_otp_secret

            data = {
                "via":"sms"
            }

            r = my_session.post(
                account_target_domain + "/api/account/mfa/token",
                json=data
            )

            print_debug(r,show_response_body=True)

            two_factor_code = input("Enter 2F code: ")

            data = {
                "code":f"\"{two_factor_code}\""
            }

            #print(r.text)

            # send the GET for the page to enter the 2F code
            #r = my_session.get()


            # send the POST to send the 2F code
            #r = my_session.post(account_target_domain + "/api/account/mfa/sign-in", json=data)

            
            
            

        elif r.status_code != 200:
            log.error("In response to login - Bad status code: %d" %(r.status_code))
            assert False, "Bad status code"

        #print("Logged in successfully!")
        
        #print("\n\n")
        #print(r.status_code)
        #pprint.pprint(r.request.headers)
        #print(r.text)

    except AssertionError as e:
        #pass Assertion back to main
        raise AssertionError(e)
    except Exception as e:
        log.error("Unknown exception in run()")
        log.exception(e)
        

    '''
    The pay or request button on a person's page -> account.venmo.com/pay?recipients=<user_name_here>

    '''

    '''

    try:
        fail_message = "Sorry, the page you requested does not exist!"
        target_url = "https://account.venmo.com/api/payments"

        accounts_list = []

        i = 0
        log.info(f"Starting at {current_x}:{current_y}")

        for x in range(current_x, len(first_list)):
            for y in range(current_y, len(last_list)):
                
                current_x = x
                current_y = y

                f = first_list[x]
                l = last_list[y]

                cur_name = f.strip().lower() + l.strip().lower()
                full_url = target_url + cur_name
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
                }


                r = requests.get(full_url,headers=headers)

                if(r.status_code != 200):
                    log.debug(f"Account does not exist: ignoring {cur_name}")
                    log.error(r.status_code)
                    log.debug(r.text[0:50])
                    log.debug(full_url)
                else:
                    kwargs["validaccounts"].write(cur_name + "\n")
                        
                time.sleep(0.2)
                i += 1
                if not i % 1000:
                    log.info(i)

    except KeyboardInterrupt as e:
        save_progress(current_x, current_y, **kwargs)
        log.info("Saving progress...")

    except Exception as e:
        save_progress(current_x, current_y, **kwargs)
        log.error("Unknown exception - saving progress")
        log.exception(e)
    '''

class SymbolFormatter(logging.Formatter):
    symbols = ["x", "!", "-", "+", "DBG"]
    
    def format(self, record):
        symbol_record = logging.makeLogRecord(vars(record))
		
        for index, symbol in enumerate(self.symbols):
            if record.levelno >= (len(self.symbols) - index) * 10:
                symbol_record.levelname = symbol
                break
			
        return super(SymbolFormatter, self).format(symbol_record)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--validaccounts", type=argparse.FileType('a+'), default="0.0.0.0", help="Right endpoint host")
    parser.add_argument("--progress", type=str, default="", help="File containing the stopping x and y values")
    parser.add_argument("--debug", action="store_true", default=False, help="Show debug information")
    parser.add_argument("--logging", type=str, help="Log file")
    parser.add_argument("-u", "--username", type=str, required=True, help="Username of account to send requests with")
    parser.add_argument("-p", "--password", type=str, default="", help="Password of account to send requests with")
    args = parser.parse_args()
    kwargs = vars(args)

    log.setLevel(logging.DEBUG)
	
    formatter = logging.Formatter(LOG_DEBUG_FORMAT) if args.debug else SymbolFormatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
    handler.setFormatter(formatter)
    log.addHandler(handler)
	
    if args.logging:
        file_handler = logging.FileHandler(args.logging)
        file_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

    kwargs["password"] = kwargs["password"] if len(kwargs["password"]) else input("Enter password: ")

    try:
        run(args, **kwargs)
    except KeyboardInterrupt:
        log.debug("keyboard interrupt")
    except AssertionError as e:
        log.error(e)
    except Exception as e:
        log.debug("Unknown exception")
        log.exception(e)
		

if __name__ == "__main__":
    main()