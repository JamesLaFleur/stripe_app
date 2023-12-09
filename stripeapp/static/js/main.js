const STRIPE_URL = '/config/';
const ORDER_URL = '/create-checkout-session/';
let stripe;

function main() {
  initializeStripe();
  setUpEventListeners();
}

// Get Stripe publishable key
function initializeStripe() {
  fetch(STRIPE_URL)
  .then((result) => { return result.json(); })
  .then((data) => {
    // Initialize Stripe.js
    stripe = new Stripe(data.publicKey);
  })  
}

function setUpEventListeners() {
  const container = document.querySelector('.cards__container');
  container.addEventListener('click', handleOrderById);
}

function handleOrderById (e) {
  const btn = e.target.closest('#submitBtn')
  console.log(btn);

  if(!btn) {
    return;
  }

  const productId = btn.getAttribute('data-card-id');

  if(!productId) {
    return;
  }

  fetch(ORDER_URL + '?product=' + productId)
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    })
    .catch(err => console.log(err));
}

window.addEventListener('load', main);