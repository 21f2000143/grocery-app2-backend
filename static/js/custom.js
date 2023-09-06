function setCookie(cname, cvalue) {
    console.log("inside set function")
    document.cookie = cname + "=" + cvalue + ";" + ";path=/";
}
document.cookie = "username=John Doe";
function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    console.log(ca, "all cookies")
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            console.log(c.substring(name.length, c.length), "return to callee")
            return c.substring(name.length, c.length);
        }
    }
    console.log("nothing", "return to callee")
    return "";
}

function checkCookie(productId) {
    console.log(productId, "at checkCookie function")
    let cart = getCookie("cart");
    console.log(cart, "result from getCookie function")
    if (cart != "") {
        let newValue=cart+','+productId;
        console.log(newValue,"inside update")
        setCookie("cart", newValue);
    } else {
        if (cart == "" && productId != null) {
            console.log("inside initail set")
            setCookie("cart", productId);
        }
    }
}

function addToCartFromElement(productId) {
    if (productId) {
        console.log(productId, "passed from addToCartFromElement function")
        checkCookie(productId);
        increaseCartCount(); // Call the function to update the cart count
        alert('Product added to cart!');
    } else {
        alert('Invalid product ID.');
    }
}
function increaseCartCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        const currentCount = parseInt(cartCountElement.innerText);
        const newCount = currentCount + 1;
        cartCountElement.innerText = newCount.toString();
    }
}
