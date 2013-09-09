from ticket_sales.models import *

Order.objects.all().update(school=None)

pela = Product.objects.get(name__icontains='pe-la')
lasu = Product.objects.get(name__icontains='la-su')
valid_order = dict(confirm_time__isnull=False, payment_date__isnull=False, cancellation_time__isnull=True)
op_valid_order = dict(order__confirm_time__isnull=False, order__payment_date__isnull=False, order__cancellation_time__isnull=True)
tammerkoski = School.objects.get(name__icontains='Tammerkosk')
amuri = School.objects.get(name__icontains='Amuri')

both_friday_and_saturday = Order.objects.filter(**valid_order).filter(order_product_set__product=pela).filter(order_product_set__product=lasu)

both_friday_and_saturday.update(school=tammerkoski)
assert all(o.school == tammerkoski for o in both_friday_and_saturday)

friday_only = Order.objects.filter(**valid_order).filter(order_product_set__product=pela).exclude(order_product_set__product=lasu)
friday_only.update(school=tammerkoski)

saturday_only = Order.objects.filter(**valid_order).filter(order_product_set__product=lasu).exclude(order_product_set__product=pela)
assert all(not o.school for o in saturday_only)
saturday_only.update(school=amuri)

assert all(o.school for o in Order.objects.filter(order_product_set__product__name__icontains='majoitus', **valid_order))
assert all(op.order.school == tammerkoski for op in pela.order_product_set.filter(**op_valid_order))

Order.objects.filter(customer__last_name='Tyni').update(school=tammerkoski)

sum(op.count for op in pela.order_product_set.filter(order__school=tammerkoski, **op_valid_order))
sum(op.count for op in lasu.order_product_set.filter(order__school=tammerkoski, **op_valid_order))
sum(op.count for op in lasu.order_product_set.filter(order__school=amuri, **op_valid_order))