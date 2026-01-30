# Mini-SaaS-Pay

A small webapp that tests SaaS payment flows.

**DO NOT USE THIS PROJECT IN PRODUCTION**

This app is for testing only and comes with no warranty or support.


## How To Use

### Step 1: Clone this project


### Step 2: Create virtual environment and install required files

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```


### Step 3: Create Subscription Product

On Stripe:
1. Create a sandbox/test environment
2. Create Products → give it a name.
3. Create Prices → choose "Recurring" (monthly/yearly) and amount.
4. Note the Price IDs for later.


### Step 4: Run the Stripe CLI

```bash
apt install stripe
stripe login
stripe listen --forward-to localhost:5000/webhook
```


### Step 5: Configure Project

Create a Flask secret_key,
add both Stripe keys,
and the price_id of the product you just created.
Also add the endpoint secret from the stripe cli


### Step 6: Start The Server

```bash
.venv/bin/python server.py
```

## Purpose

It's intention is to show a basic,
but working Stripe flow.
It simulates a SaaS app with subscription business model,
within an isolated environment.
The app isn't convoluted by actual features or business logic
beyond verifying user is current in payments,
and gatekeeping app access.
It should contain just enough information to allow you to then read the docs,
for any additional features needed.

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
