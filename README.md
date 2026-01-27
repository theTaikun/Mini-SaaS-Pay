# Mini-SaaS-Pay

A small webapp that tests SaaS payment flows.

**DO NOT USE THIS PROJECT IN PRODUCTION**

This app is for testing only and is completely insecure.
It's intention is to show a basic,
but working Stripe purchasing flow,
for a SaaS subscription,
within an isolated environment.
It should contain just enough information to allow you to then read the docs,
for any additional features needed.

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
