import requests
from bs4 import BeautifulSoup
import cloudscraper
import time

def main():

    # Create a Cloudscraper session. This handles cloudflare blocks
    session = cloudscraper.create_scraper() 
    login_email = "email@gmail.com"
    login_password = "password"

    HONK_GUID = "x" #This could change, not sure yet if it does
    HONK_URL = f"https://platform.x.com/graphql?honkGUID={HONK_GUID}" #URL that is used for most graphql queries to retrieve info

    # Login Payload
    LOGIN_PAYLOAD = {
        "operationName": "Login",
        "variables": {
            "input": {
                "emailAddress": login_email,
                "password": login_password
            }
        },
        "query": """
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    userSession {
                        oaTag
                        __typename
                    }
                    errors
                    __typename
                }
            }
        """
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Origin": "https://reservenski.x.com",
        "Referer": "https://reservenski.x.com/",
    }
    
    ######################################################## LOGIN ################################################################
    LOGIN_URL = "https://platform.x.com/graphql"
    
    login_response = session.post(LOGIN_URL, json=LOGIN_PAYLOAD, headers=headers)

    if login_response.status_code == 200 and "userSession" in login_response.json().get("data", {}).get("login", {}):
        auth_token = login_response.json()["data"]["login"]["userSession"]["oaTag"]
        print("Login successful! Token retrieved.", auth_token)
    else:
        print("Login failed:", login_response.json())
        exit()
    
    headers["X-Authentication"] = f"{auth_token}"  
    
    # Step 2: Fetch Promo Codes. Values redacted for privacy sake
    PROMO_CODE = "VALUE"
    ZONE_ID = "VALUE"
    PARKING_INVENTORY_ID = "VALUE"
    
    ##################################################  CREATE CART #####################################################
    create_cart_payload = {
        "operationName": "CreateCart",
        "variables": {
            "input": {
                "startTime": "2024-10-01T07:00:00-06:00",
                "zoneId": ZONE_ID,
                "productType": "RESERVE"
            }
        },
        "query": """
            mutation CreateCart($input: CreateCartInput!) {
                createCart(input: $input) {
                    cart {
                        hashid
                        __typename
                    }
                    errors
                    __typename
                }
            }
        """
    }

    print("Creating Cart...")

    try:
        create_cart_response = session.post(
            HONK_URL,  # Correct GraphQL endpoint
            json=create_cart_payload,
            headers=headers
        )

        #print(create_cart_response.json())
        if create_cart_response.status_code ==200:
            cart_id = create_cart_response.json()["data"]["createCart"]["cart"]["hashid"]
            print(f"Cart creation successful. Cart ID: {cart_id}")
        else:
            print("Create cart did NOT return 200", create_cart_response.json())
            print(f"STATUS CODE: {create_cart_response.status_code}")

    except Exception as e:
        print("Error creating cart and fetching cart ID")
        print(e)
    
    ####################################################  CLAIM CART ##################################################
    claim_cart_payload = {
        "operationName": "ClaimCart",
        "variables": {
            "input": {
                "id": cart_id  # Replace this with the actual cart ID you want to claim
            }
        },
        "query": """
            mutation ClaimCart($input: ClaimCartInput!) {
                claimCart(input: $input) {
                    cart {
                        hashid
                        __typename
                    }
                    errors
                    __typename
                }
            }
        """
    }

    print("Claiming Cart...")

    try:
        claim_cart_response = session.post(
            HONK_URL,  # Correct GraphQL endpoint
            json=claim_cart_payload,
            headers=headers
        )
        if claim_cart_response.status_code == 200:
            print("Successfuly claimed cart")
            
        else:
            print("Claim cart did NOT return 200", claim_cart_response.json())
            print(f"STATUS CODE: {claim_cart_response.status_code}")

    except Exception as e:
        print("Error claiming cart")
        print(e)

    
    ################################################  ADD PROMO TO CART #####################################################
    #  (Might not be needed), keeping for now because it mimics the request flow in browser
  
    add_promo_to_cart_payload = {
        "operationName": "AddPromoToCart",
        "variables": {
            "input": {
                "cartId": cart_id,  
                "promoCode": PROMO_CODE,  
                "validate": False  
            }
        },
        "query": """
            mutation AddPromoToCart($input: AddPromoToCartInput!) {
                addPromoToCart(input: $input) {
                    cart {
                        hashid
                        promoCode {
                            hashid
                            shortDesc
                            redeemCode
                            promoCodesRates {
                                rate {
                                    hashid
                                    description
                                    zone {
                                        hashid
                                        __typename
                                    }
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                    errors
                    __typename
                }
            }
        """
    }
    
    print("Adding parking code to cart...")

    try:
        add_promo_to_cart_response = session.post(
            HONK_URL,  # Correct GraphQL endpoint
            json=add_promo_to_cart_payload,
            headers=headers
        )
        if add_promo_to_cart_response.status_code == 200:
            print("Successfully added parking code to cart")
            
            #promo_rate_id = add_promo_to_cart_response.json()["data"]["addPromoToCart"]["cart"]["promoCode"]["promoCodesRates"][0]["rate"]["hashid"]
        else:
            print("Parking code request did NOT return 200", add_promo_to_cart_response.json())
            print(f"STATUS CODE: {add_promo_to_cart_response.status_code}")

    except Exception as e:
        print("Error adding parking code to cart")
        print(e)
    
    ###############################################  Change Cart Start #######################################################
    #  (This function changes the reservation to a specific day, you can edit "startTime")

    reservation_date = "2024-12-14T07:00:00-07:00"
    change_cart_start_time_payload = {
        "operationName": "ChangeCartStartTime",
        "variables": {
            "input": {
                "startTime": reservation_date,  # The new start time for the cart
                "id": cart_id  # The cart ID whose start time you want to change
            }
        },
        "query": """
            mutation ChangeCartStartTime($input: ChangeCartStartTimeInput!) {
                changeCartStartTime(input: $input) {
                    cart {
                        hashid
                        startTime
                        __typename
                    }
                    errors
                    __typename
                }
            }
        """
    }
    
    print(f"Changing reservation day to {reservation_date}")

    try:
        change_cart_start_time_response = session.post(
            HONK_URL,
            json=change_cart_start_time_payload,
            headers=headers
        )
        if change_cart_start_time_response.status_code == 200:
            print(f"Successfully changed reservation date to {reservation_date}")
            
        else:
            print("Changing reservation date did NOT return 200", change_cart_start_time_response.json())
            print(f"STATUS CODE: {change_cart_start_time_response.status_code}")

    except Exception as e:
        print("Error changing reservation date")
        print(e)


    ############################################  Get Rates #######################################################
    #  This function gets the rates of the day specified in "change cart start" above. If no parking pass is available, it will check again in 30 seconds
  
    get_rates_payload = {
        "operationName": "GetRates",
        "variables": {
            "cartId": cart_id
        },
        "query": """
            query GetRates($cartId: ID!) {
                v2CartRates(cartId: $cartId) {
                    hashid
                    price
                    description
                    promoRate
                    behaviourType
                    freeFlag
                    __typename
                }
            }
        """
    }

    print("Getting Rates...")

    try:
        rate_available = False
        while not rate_available:
            get_rates_response = session.post(
                HONK_URL,  # Correct GraphQL endpoint
                json=get_rates_payload,
                headers=headers
            )

            print(get_rates_response.json(), get_rates_response.status_code)
            try:
                cart_rate = get_rates_response.json()["data"]["v2CartRates"][0]["hashid"]
                print(f"Cart Rate: {cart_rate}")
                rate_available = True

            except:
                print("No Reservations Available, trying again in 30 seconds")
                time.sleep(30)

    except Exception as e:
        print("Error getting rates")
        print(e)

    #If this is empty, no reservations available

    #####################################################  Add Rate to Cart ################################################################
    
    add_rate_to_cart_payload = {
        "operationName": "AddRateToCart",
        "variables": {
            "input": {
                "rateId": cart_rate,  
                "cartId": cart_id
            }
        },
        "query": """
            mutation AddRateToCart($input: AddRateToCartInput!) {
                addRateToCart(input: $input) {
                    cart {
                        id
                        hashid
                        __typename
                    }
                    errors
                    __typename
                }
            }
        """
    }
    
    print("Adding rate to cart...")

    try:
        add_rate_to_cart_response = session.post(
            HONK_URL,
            json=add_rate_to_cart_payload,
            headers=headers
        )

        if add_rate_to_cart_response.status_code == 200:
            print("Successfully added rate to cart")
            final_cart_id = add_rate_to_cart_response.json()["data"]["addRateToCart"]["cart"]["id"]
            print(f"Final Cart ID: {final_cart_id} ")
        else:
            print("Adding rate to cart request NOT 200", add_rate_to_cart_response.json())
            print(f"STATUS CODE: {add_rate_to_cart_response.status_code}")

    except Exception as e:
        print("Cannot validate final cart ID")
        print(e)

    ####################################################  Validate Cart Promo Code #######################################################
    validate_cart_promo_code_payload = {
        "operationName": "ValidateCartPromoCode",
        "variables": {
            "input": {
                "id": cart_id
            }
        },
        "query": """
            mutation ValidateCartPromoCode($input: ValidateCartPromoCodeInput!) {
                validateCartPromoCode(input: $input) {
                    cart {
                        hashid
                        __typename
                    }
                    errors
                    __typename
                }
            }
        """
    }

    print("Validating promo code on cart...")

    try:
        validate_cart_promo_code_response = session.post(
            "https://platform.x.com/graphql?honkGUID=beynfkdvh2o6qtvruv3b77",
            json=validate_cart_promo_code_payload,
            headers=headers
        )

        if validate_cart_promo_code_response.status_code == 200:
            print("Successfully validated parking code on cart")
        else:
            print("Validating promo code on cart NOT 200", validate_cart_promo_code_response.json())
            print(f"STATUS CODE: {validate_cart_promo_code_response.status_code}")
    except Exception as e:
        print("Error ")


    ####################################################### CLAIMING RESERVATION ##########################################################
    url_cart = f'https://platform.x.com/carts/{final_cart_id}/claim'
    url_payment_methods = f"https://platform.x.com/users/information?oa_tag={auth_token}&honkGUID=x&app_version=0"

    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Length': '102',
        'Content-Type': 'application/json',
        'Origin': 'https://parking.x.com',
        'Referer': 'https://parking.x.com/',
        'Sec-CH-UA': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    # The payload (data) for the request (could be empty or specific parameters depending on the API)
    payload = {
        "oa_tag": auth_token,
        "honkGUID": "x",
        "app_version": 0
    }
  
    payload = {
        "app_version": -,
        "cart_id": final_cart_id,
        "honkGUID": "x",
        "oa_tag": auth_token,
        "override_conflict": True,
        "source": "web-app",
        "vehicle": "0" #Hardcoded, can be retrieved through the url_vehicles request
        
        
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Origin": "https://ski.x.com",
        "Referer": "https://ski.x.com/",
    }

    checkout_url = "https://platform.x.com/parking_sessions"
    webhook_url = "your_webhook_url

    response = requests.post(checkout_url, json=payload, headers=headers)

    print(response.text, response.status_code)

    if response.status_code == 200:
        print("Successfully placed reservation")
        message = f"Successfully placed reservation for {reservation_date}"
        data = {"content": message}
        requests.post(webhook_url, json=data)



if __name__ == "__main__":
    main()
