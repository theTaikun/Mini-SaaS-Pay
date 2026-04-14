## The Mini-SaaS Project

This repo is part of the Mini-SaaS project.

Sometimes when building a large complex system,
it helps to first start by isolating the major problems.
To do this,
I built the major portions of a small Software as a Service (SaaS) app
independetly from eachother.
This was used to learn how these portions should work individually,
rather than trying to learn it all at once.

The different projects invovled are:

* [Mini-SaaS-Auth](https://github.com/theTaikun/Mini-SaaS-Auth):
    Integrating Supabase for authentication only.
    Frontend and backend are portable,
    and database could be hosted on Supabase or elsewhere.
* [Mini-SaaS-Pay](https://github.com/theTaikun/Mini-SaaS-Pay):
Integrating Stripe for recurring payments.


## Overview

A small webapp that tests SaaS payment flows.

**DO NOT USE THIS PROJECT IN PRODUCTION**

This app is for testing only and comes with no warranty or support.


## How To Use

### Step 1: Clone this repo


### Step 2: Create the project environment and install required packages

1. Create virtual environment
    ```bash
    python -m venv .venv
    .venv/bin/pip install -r requirements.txt
    ```
2. Create .env file
    ```bash
    cp .env.example .env
    ```
3. Generate a Flask secret key, and add it to `.env`
    ```bash
    python -c 'import secrets; print(secrets.token_hex())'
    ```
4. Set `PUBLIC_URL` in `.env`
    If you will be running the app on the same workstation you're using,
    you can leave this as localhost,
    otherwise set it to the hostname or routable address of the server


### Step 3: Set Up Stripe

1. Create a sandbox/test environment
2. Add the publishable key and secret key to `.env` file
3. Limit customers to [one subscription](https://docs.stripe.com/payments/checkout/limit-subscriptions)
4. Create Product(s) → give it a name and description.
5. Create Prices → choose "Recurring" (monthly/yearly) and amount.
6. Add the price_id to the `.env` file


### Step 4: Run the Stripe CLI

This portion is necessary to allow stripe to reach your local development endpoint,
since it probably is not internet accessible

1. Install the stripe CLI, such as
    ```bash
    apt install stripe
    ```
2. Login to your stripe environment
    ```bash
    stripe login
    ```
3. Run it, specifying the endpoint the app should be listening on
    ```bash
    stripe listen --forward-to localhost:5000/webhook
    ```
4. Note the endpoint secret displayed, and copy it to the `.env`


### Step 5: Start The Server

```bash
.venv/bin/python server.py
```

### Step 6: Use the Web App

In a web browser,
navigate to the location you configured as `PUBLIC_URL`


## Purpose

The intention of this project
is to show a basic, but working Stripe flow.
It simulates a SaaS app with a subscription business model,
within an isolated environment.
The app isn't convoluted by actual features or business logic
beyond verifying user is current in payments,
and gate-keeping app access.
It should contain just enough information to help familiarize with how to set things up.
After which, the official documentation can be understood in context,
and referenced for any additional needed features.

Flask was chosen as a one-stop-shop for both backend and frontend.
This simplifies the codebase,
especially since no effort was made in aesthetic design.

Based in part on [t3dotgg/stripe-recommendations](https://github.com/t3dotgg/stripe-recommendations).


## Integration

If this repo is to be used in another project,
here are some recommendations for implentation.

Build authentication first.
Proper modern auth is beyond the scope of this project,
and passwords are being stored plaintext.
You will have to implement authorization yourself,
don't use the auth system of this repo.
There are tons of resources out there if you don't know how to do this.
Decide which pages and features will be public,
and which will be locked behind different paywalls.
Handle the user session,
and make sure the user can log in and out
prior to trying to implement payments.
I regretted not doing this first,
as adding it later was more difficult.

Don't fork this repo and build an app off it,
you're better off starting from scratch,
and using tailored versions of my methods as needed.
Take the time to Understand what this project does and how it works,
and then you can decide what you need,
what you don't,
and what to research more.

This repo doesn't handle all error cases.
Think about how payments in your app could fail,
and build error handling around that.
For instance,
plan for the case where Stripe's servers go down and are unreachable,
or the API responds in a format not expected.
