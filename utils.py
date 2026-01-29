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
        # extract and associated subData to here if needed
        return subData

    subscription = subscriptions.data[0]
    # extract and associated subData to here if needed
    subData = subscription

    return subData
