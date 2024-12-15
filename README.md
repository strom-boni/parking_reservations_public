# Parking Pass Auto-Reservations
## Purpose
The purpose of this script is to automate the parking reservation process for an unamed ski resort. It has been getting harder and harder to secure parking reservations, as there are limited reservations released. Most URLs have been changed and many values have been redacted for privacy reasons.

## Overview
This script automatically reserves a season pass parking reservation for the day that you specify.

## Steps
### 1. Login
The script with login with your account email and password that you specify and create a session with Cloudscraper. Cloudscraper is used because the site being automated uses Cloudflare.

### 2. Create Cart
A cart will be created so you can proceed with adding reservations to the cart.

### 3. Claim Cart
Claims the cart that you just created

### 4. Add Promo to Cart
This section will add your season pass parking code to your cart session

### 5. Change Cart Start
Specify which date you want to get a reservation for. This will change the details of the cart so you can proceed with the reservation

### 6. Get Rates
Queries for the parking rates are made on the cart with the specified target date. If no rates exist, the script will try again in X amount of seconds. You can set this variable yourself. This helps if you want to consistently run the script to look for any canceled reservations that can picked up.

### 7. Add Rate to Cart
Once the parking reservations becomes available (rate is found), this rate will be added to the cart.

### 8. Validate Promo Code
This sends a request to validate that your parking reservation code is valid and can be used to make this reservation.

### 9. Claim Reservation
Reservation is claimed and applies your vehicle license plate to the reservation. The vehicle ID was hardcoded because it appeared to be static, but it can be retrieved with a GET request to "url_vechicles". After the vehicle is applied, the next request checks out and the process is complete. Upon completion, a discord webhook is sent to my server
