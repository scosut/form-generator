from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from forms.models import Form
from items.models import Item
from orders.models import Order
from order_items.models import OrderItem
from forms.validate import Validate
from PIL import Image
import io
import re
import pytz
import xlsxwriter
import boto3

def get_s3():
	return boto3.resource(
		service_name='s3',
		region_name=settings.AWS_S3_REGION_NAME,
		aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
		aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY
	)

def get_bucket():
	return get_s3().Bucket(settings.AWS_STORAGE_BUCKET_NAME)

def get_order_data(order_items):
	total = 0
	items = {}
	
	for order_item in order_items:
		key = order_item.item_id
		obj = {
			'size':     order_item.size, 
			'quantity': order_item.quantity, 
			'athletes': order_item.athletes
		}
		
		if key not in items:
			items[key] = {
				'title':  order_item.item.title,
				'price':  order_item.item.price,
				'image':  order_item.item.image,
				'orders': []				
			}

		items[key]['orders'].append(obj)
		total += order_item.item.price * order_item.quantity
		
	return {'total': total, 'items': items}

def index(request):
	user = request.session.get('user', None)
	
	if user != 'admin':
		request.session['referer'] = reverse('orders')
		return redirect(reverse('admin_login'))
	
	page = request.POST.get("page", None)
	page = 1 if page is None else int(page)
	orders = Order.objects.all()[::1]
	x = [orders[i:i + 10] for i in range(0, len(orders), 10)]
	pages  = range(1, len(x)+1) if len(x) > 1 else range(1, len(x))
	orders = x[page-1] if len(x) > 0 else orders
	return render(request, 'orders/index.html', {'orders': orders, 'pages': pages, 'active': page})

def view(request, order_id):
	bucket = get_bucket()	
	source = "https://%s.s3.%s.amazonaws.com/" %(bucket.name, settings.AWS_S3_REGION_NAME)
	
	order_items = OrderItem.objects.filter(order_id=order_id)
	form        = order_items.first().order.form
	order_date  = order_items.first().order.orderDate
	data        = get_order_data(order_items)
	
	return render(request, 'orders/show.html', {'source': source, 'form': form, 'order_date': order_date, 'total': data['total'], 'items': data['items']})

def export(request, order_id):
	bucket = get_bucket()
	
	order_items = OrderItem.objects.filter(order_id=order_id)	
	form        = order_items.first().order.form
	order_date  = order_items.first().order.orderDate
	order_date  = order_date.astimezone(pytz.timezone('America/Los_Angeles'))
	order_date  = order_date.strftime('%m%d%Y_%I%M%S%p').lower()
	gym         = form.gym.lower().strip().replace(" ", "_")
	gym         = re.sub("[^a-zA-Z0-9_]", "", gym)
	data        = get_order_data(order_items)
	output      = io.BytesIO()
	filename    = '%s_%s' % (gym[:13], order_date)
	wb          = xlsxwriter.Workbook(output)
	ws          = wb.add_worksheet(filename)
	totals_row  = 0
	row = 0
	col = 0
	
	for key in data['items'].keys():
		image_url = "https://%s.s3.%s.amazonaws.com/%s" %(bucket.name, settings.AWS_S3_REGION_NAME, data['items'][key]['image'])
		file_byte_string = get_s3().Object(bucket.name, str(data['items'][key]['image'])).get()['Body'].read()
		file_bytes     = io.BytesIO(file_byte_string)
		item_image     = Image.open(file_bytes)
		item_image_dpi = max(item_image.info['dpi']) if "dpi" in item_image.info else 72
		item_title     = data['items'][key]['title']
		item_price     = data['items'][key]['price']
		my_format      = {'image_data': file_bytes, 'x_scale': item_image_dpi/item_image.width, 'y_scale': item_image_dpi/item_image.height}
		
		ws.merge_range(row, col, row, col+2, None)
		ws.insert_image(row, col, image_url, my_format)
		row += 1
		
		my_format = {'align': 'center', 'bold': True}		
		ws.merge_range(row, col, row, col+2, item_title, wb.add_format(my_format))
		row += 1
				
		ws.write(row, col, "Size", wb.add_format(my_format))
		ws.write(row, col+1, "Quantity", wb.add_format(my_format))
		ws.write(row, col+2, "Athletes", wb.add_format(my_format))
		row += 1
		
		my_format = {'valign': 'top'}
		
		for order_item in data['items'][key]['orders']:
			ws.write(row, col, order_item['size'], wb.add_format(my_format))
			ws.write(row, col+1, order_item['quantity'], wb.add_format(my_format))			
			my_format['text_wrap'] = True
			ws.write(row, col+2, order_item['athletes'], wb.add_format(my_format))
			row += 1
			
		totals_row = row if row > totals_row else totals_row
			
		ws.write(totals_row+1, col, "Subtotal")
		ws.write_formula(totals_row+1, col+1, '=SUM(INDIRECT(ADDRESS(1,COLUMN())&":"&ADDRESS(ROW()-2,COLUMN())))')
		
		my_format = {'num_format': '$#,##0.00'}
		ws.write(totals_row+2, col, "Price (each)")
		ws.write(totals_row+2, col+1, item_price, wb.add_format(my_format))	

		ws.write(totals_row+3, col, "Total")
		ws.write_formula(totals_row+3, col+1, '=PRODUCT(INDIRECT(ADDRESS(ROW()-2,COLUMN())&":"&ADDRESS(ROW()-1,COLUMN())))', wb.add_format(my_format))
		
		col += 3
		row = 0
	
	ws.write(totals_row+3, col, "Grand Total")
	ws.write_formula(totals_row+3, col+1, '=SUM(INDIRECT(ADDRESS(ROW(),1)&":"&ADDRESS(ROW(),COLUMN()-2)))', wb.add_format(my_format))
	
	ws.set_row(row, 72)
	ws.set_column(row, col+1, 15)
	wb.close()
	output.seek(0)
	
	response = HttpResponse(output, content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % filename
	
	return response

def login(request, form_id):
	if request.is_ajax():
		user = request.POST.get("user", None)
		form = Form.objects.get(id=form_id)
		
		val         = Validate()		
		check_email = val.isEmail(user, "Please enter valid Customer Email.")
		
		if check_email:
			val.doMatch(user, form.email, "Email provided is not found.")
		
		errors = val.getErrors()
		
		if errors:
			return JsonResponse(errors, safe=False)
		else:
			return JsonResponse({"post": reverse('create', kwargs={'form_id': form_id})})
	else:
		return render(request, 'orders/login.html', {'form_id': form_id})

def create(request, form_id, isTest):
	bucket = get_bucket()
	source = "https://%s.s3.%s.amazonaws.com/" %(bucket.name, settings.AWS_S3_REGION_NAME)
	items       = Item.objects.filter(form_id=form_id).order_by("order")
	form        = items.first().form
	emptyForm   = True
	order_items = []
	user        = request.POST.get("user", None)
	
	for item in items:
		item.sizes = item.sizes.splitlines()
	
	if request.is_ajax():		
		val = Validate()
		
		for item_index, item in enumerate(items, start=1):
			for size_index, size in enumerate(item.sizes, start=1):
				quantity = request.POST.get("qty-item-"+str(item_index)+"-size-"+str(size_index), None)
				
				athlete = request.POST.get("name-item-"+str(item_index)+"-size-"+str(size_index), None)
				
				check_quantity = False
				check_athlete  = False
				
				if quantity or athlete:
					emptyForm = False
					
					check_quantity = val.isQuantity(quantity, "Please provide valid quantity ("+item.title+", "+size+").")
					
					check_athlete = val.isEmpty(athlete, "Please provide athlete names ("+item.title+", "+size+").")
				
				if check_quantity and not check_athlete:
					athlete_size = len(athlete.strip().splitlines())
					
					if int(quantity) != athlete_size:
						val.setError("Please provide "+quantity+" athlete names ("+item.title+", "+size+").")
					else:
						order_item          = OrderItem()
						order_item.size     = size
						order_item.quantity = quantity
						order_item.athletes = athlete
						order_item.order    = None
						order_item.item     = item
						order_items.append(order_item)
						
		if emptyForm:
			errors = val.setError("Please provide quantity and athlete names.")
		
		errors = val.getErrors()
		
		if errors:
			return JsonResponse(errors, safe=False)
		else:
			order      = Order()
			order.form = form
			order.save()
			
			for order_item in order_items:
				order_item.order = order
				order_item.save()
				
			email_subj = 'Order placed by %s' % (form.gym)
			email_link = request.build_absolute_uri(reverse('orders'))
			email_from = settings.EMAIL_HOST_USER
			email_to   = [settings.EMAIL_HOST_USER]
			html_body  = '<p>Hello, Vendor.</p><p>Review your orders at the following URL to see the latest submission from %s:</p><p>%s</p>' % (form.gym, email_link)
			email_body = html_body.replace("<p>", "").replace("</p>", "\n\n")

			# send email
			if not isTest:
				send_mail(
					email_subj,
					email_body,
					email_from,
					email_to,
					fail_silently=False,
					html_message=html_body
				)
				
			return JsonResponse({"url": reverse('confirm')})
	else:
		if user:
			return render(request, 'orders/create.html', {'source': source, 'form': form, 'items': items, 'user': user})
		else:
			return login(request, form_id)