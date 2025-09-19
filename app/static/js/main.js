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

function add_to_cart(id, event_name, vip_price, normal_price, normal_quantity = 0, vip_quantity = 0) {
  fetch("/api/ticket-cart", {
    method: "post",
    body: JSON.stringify({
      "id": id,
      "event_name": event_name,
      "vip_price": vip_price,
      "vip_quantity": vip_quantity,
      "normal_price": normal_price,
      "normal_quantity": normal_quantity
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
            if (data.total_quantity === 0) {
                // Giỏ trống => reload lại để Flask render nhánh {% else %}
                location.reload();
            } else {
                document.getElementById(`ticket-cart${event_id}`).remove();
                updateUI(data);
            }
        })
    }
}

function pay() {
    if(confirm("Bạn có chắc chắn muốn thanh toán không? ") === true){
        fetch('/api/pay', {method: 'POST'})
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
                window.location.href = data.payment_url;
            } else {
                alert(data.message || "Có lỗi xảy ra!");
            }
        })
    }
}

function addComment(event_id) {
    fetch(`/api/event/${event_id}/comments`, {
        method: "post",
        body: JSON.stringify({
            "content": document.getElementById("comment").value
        }),
        headers: {
            'Content-Type': "application/json"
        }
    }).then(res => res.json()).then(c => {
        let html = `<li class="list-group-item w-75 mx-auto">
        <div class="row">
            <div class="col-md-1 col-4">
                <img src="${ c.user.avatar }" class="img-fluid rounded-circle w-75 mx-auto d-block" />
                <p class="fw-bold text-center">${ c.user.username }</p>
            </div>
            <div class="col-md-11 col-8">
                <p>${ c.content }</p>
                <p class="date small fst-italic text-muted">${ moment(c.created_date).locale("vi").fromNow() }</p>
            </div>
        </div>
    </li>`;

    let comments = document.getElementById("comments");
    comments.innerHTML = html + comments.innerHTML;
    location.reload();
    })
}
