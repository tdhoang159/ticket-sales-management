function add_to_cart(id, event_name, vip_price, normal_price) {
  fetch("/api/ticket-cart", {
    method: "post",
    body: JSON.stringify({
      "id": id,
      "event_name": event_name,
      "vip_price": vip_price,
      "normal_price": normal_price,
    }),
    headers: {
        'Content-Type': "application/json"
    }
  }).then(res => res.json()).then(data => {
    console.info(data);
    let items = document.getElementsByClassName("cart-counter");
    for (let item of items){
        item.innerText = data.total_quantity;
    }
  });
}
