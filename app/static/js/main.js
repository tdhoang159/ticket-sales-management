function updateUI(data){
    let items_counter = document.getElementsByClassName("cart-counter");
    for (let item of items_counter){
        item.innerText = data.total_quantity;
    }

    let items_amount = document.getElementsByClassName("cart-amount");
    for (let item of items_amount){
        item.innerText = data.total_amount.toLocaleString();
    }
}

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
    updateUI(data);
  });
}

function updateCart(event_id, obj, type, vip_price, normal_price){
    let body = {};
    if (type === 'vip') {
        body.vip_quantity = obj.value;
    } else if (type === 'normal') {
        body.normal_quantity = obj.value;
    }

    fetch(`/api/ticket-cart/${event_id}`, {
        method: 'put',
        body: JSON.stringify(body),
        headers: {
            'Content-Type': "application/json"
        }
    }).then(res => res.json()).then(data => {
        updateUI(data);

        let vipQty = parseInt(document.querySelector(`#ticket-cart${event_id} input[onblur*="vip"]`).value);
        let normalQty = parseInt(document.querySelector(`#ticket-cart${event_id} input[onblur*="normal"]`).value);

        // Tính lại tổng số vé & tổng tiền
        let totalQty = vipQty + normalQty;
        let totalAmount = vipQty * vip_price + normalQty * normal_price;

        //Cập nhật lại UI total-quantity-{{ c.id }}
        document.getElementById(`total-quantity-${event_id}`).innerText = totalQty;
        document.getElementById(`total-amount-${event_id}`).innerText = totalAmount.toLocaleString();
    })
}

function deleteCart(event_id){
    if(confirm("Bạn có chắc chắn muốn xoá nó không? ") === true){
        fetch(`/api/ticket-cart/${event_id}`, {
            method: 'delete'
        }).then(res => res.json()).then(data => {
            document.getElementById(`ticket-cart${event_id}`).style.display = "none";
            updateUI(data);
        })
    }
}
