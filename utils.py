import stripe

def syncStripeDataToKV(customerId: str):
    subscriptions = stripe.Subscription.list(
            customer=customerId,
            limit=1,
            status="all",
            expand=["data.default_payment_method"]
    )
    if len(subscriptions.data) == 0:
        subData = {"status": None}

    else:
        # Number of subscriptions per user should have already been limitted to one
        subscription = subscriptions.data[0]
        subscription_item = subscription["items"]["data"][0]

        subData = {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "price_id": subscription["items"]["data"][0].price.id,
            "current_period_start": subscription_item["current_period_start"],
            "current_period_end": subscription_item["current_period_end"],
            "cancel_at_period_end": subscription.cancel_at_period_end,
            # "payment_method": {}, # recommended by t3dotgg, but not needed
            }

    return subData
