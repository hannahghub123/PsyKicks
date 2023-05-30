// var updateBtns = document.getElementsByClassName('update-cart')


// for(var i=0; i<updateBtns.length; i++){
//     updateBtns[i].addEventListener('click', function(){
//         var productId = this.dataset.product
//         var action = this.dataset.action
//         console.log('productId:', productId, 'action:', action)

//         console.log('USER:', user);
//         if(user === 'AnonymousUser'){
//             console.log('Not Logged In')
//         }else{
//             updateUserOrder(productId, action)
//         }

//     })
// }

// function updateUserOrder(productId, action){
//     console.log('User is logged in, sending data')

//     var url = '/update_item/'

//     fetch(url, {
//         method:'POST',
//         headers:{
//             'Content-Type':'application/json',
//             'x-CSRFToken' : csrftoken,
//         },
//         body:JSON.stringify ({'productId': productId, 'action':action })
//     })

//         .then((response) =>{
//             return response.json()
//         })

//         .then((data) =>{
//             console.log('data:',data)
//         })
// }

$(document).ready(function() {
    $(".update-cart").click(function() {
        var productId = $(this).data("product");
        var action = $(this).data("action");
        var quantityInput = $(this).siblings("input[name='quantity']");
        var quantity = quantityInput.val();

        $.ajax({
            type: "POST",
            url: "{% url 'addtocart' 0 %}".replace("0", productId),
            data: {
                csrfmiddlewaretoken: "{{ csrf_token }}",
                quantity: quantity,
            },
            success: function(response) {
                // Handle the success response if needed
                window.location.href = "{% url 'cart' %}";  // Redirect to the cart page
            },
            error: function(response) {
                // Handle the error response if needed
            }
        });
    });
});
