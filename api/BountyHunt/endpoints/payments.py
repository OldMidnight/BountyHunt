from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import stripe

bp = Blueprint('payments', __name__, url_prefix="/payments")

@bp.route('/create_intent', methods=('POST',))
@jwt_required()
def create_payments_intent():
  """
  create_payments_intent creates a payment intent that will be used in the frontend to complete a stripe transaction.
  """
  amount = request.get_json()['amount']
  # Convert amount float into string with necessary trailing zeros.
  amount = str(amount).split('.')
  if (len(amount) == 2 and len(amount[1]) == 1):
    amount[1] = amount[1] + '0'
  else:
    amount[0] = amount[0] + '00'
  amount = ''.join(amount)

  stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
  intent = stripe.PaymentIntent.create(
    amount=amount,
    currency='eur',
    metadata={'integration_check': 'accept_a_payment'}
  )
  return jsonify(client_secret=intent.client_secret)