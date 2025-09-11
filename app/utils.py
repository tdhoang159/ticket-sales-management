def stats_cart(cart):
    total_amount, total_quantity = 0, 0

    if(cart != None):
        for c in cart.values():
            total_quantity += c['vip_quantity'] + c['normal_quantity']
            total_amount += c['vip_quantity']*c['vip_price']+c['normal_quantity']*c['normal_price']

    return {
        "total_amount": total_amount,
        "total_quantity": total_quantity
    }