from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from forms.models import Form
from items.models import Item
from orders.models import Order
from forms.validate import Validate
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
	
def cleanup_images(bucket, list1, list2, folder):
	bucket_keys = [str(item.key).replace(folder, "") for item in list1]
	item_keys   = [str(item.image).replace(folder, "") for item in list2]
	final_keys  = list(set(bucket_keys).symmetric_difference(set(item_keys)))
	
	for key in final_keys:
		get_s3().Object(bucket.name, folder+key).delete()

def index(request):
	user = request.session.get('user', None)
	
	if user != 'admin':
		request.session['referer'] = reverse('forms')
		return redirect(reverse('admin_login'))
	
	page  = request.POST.get("page", None)
	page  = 1 if page is None else int(page)
	forms = Form.objects.prefetch_related(
		Prefetch("order_set", queryset=Order.objects.all(), to_attr='form_orders')).order_by('id')[::1]
	x = [forms[i:i + 10] for i in range(0, len(forms), 10)]
	pages = range(1, len(x)+1) if len(x) > 1 else range(1, len(x))
	forms = x[page-1] if len(x) > 0 else forms
	return render(request, 'forms/index.html', {'forms': forms, 'pages': pages, 'active': page})		

def notify(request, form_id, isTest):
	form = Form.objects.get(id=form_id)
	form.notified = timezone.now()
	form.save()
	
	email_subj = 'DareDevils Activewear %s' % (form.title)
	email_link = request.build_absolute_uri(reverse('create', kwargs={'form_id': form_id}))
	email_from = settings.EMAIL_HOST_USER
	email_to   = [form.email]
	html_body  = '<p>Dear %s:</p><p>%s</p><p>Access your form at the following URL:</p><p>%s</p>' % (form.gym, form.instructions, email_link)
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
	
	return redirect(reverse('forms'))
	
def add(request):
	user = request.session.get('user', None)
	
	if user != 'admin':
		request.session['referer'] = reverse('add')
		return redirect(reverse('admin_login'))
	
	if request.is_ajax():
		form_title   = request.POST.get("title", None)
		instructions = request.POST.get("instructions", None)
		logo         = request.POST.get("logo", None)
		logo_file    = request.FILES.get('logo-new-file', None)			
		email        = request.POST.get("email", None)
		gym          = request.POST.get("gym", None)
		forSale      = request.POST.get("for-sale", None)
		
		val = Validate()		
		val.isEmpty(form_title, "Please enter Form Title.")
		val.isEmpty(instructions, "Please enter Form Instructions.")
		val.isEmpty(logo, "Please select Form Logo.")
		
		if logo == "new":			
			val.isImage(logo_file, "New Logo Image")
		
		val.isEmail(email, "Please enter valid Customer Email.")
		val.isEmpty(gym, "Please enter Customer Gym.")
		items = []
		
		if (forSale):
			for i in range(1, int(forSale)+1):
				order = i
				title = request.POST.get("item-title-"+str(i), None)
				price = request.POST.get("item-price-"+str(i), None)
				image = request.FILES.get('item-image-file-'+str(i), None)
				sizes = request.POST.get("item-sizes-"+str(i), None)

				val.isEmpty(title, "Please enter Item "+str(i)+" Title.")
				val.isInteger(price, "Please enter valid Item "+str(i)+" Price.")				
				val.isImage(image, "Item "+str(i)+" Image")
				val.isEmpty(sizes, "Please enter Item "+str(i)+" Sizes.")
				
				item       = Item()
				item.order = order
				item.title = title
				item.price = price
				item.image = image
				item.sizes = sizes
				item.form  = None

				items.append(item)
		
		errors = val.getErrors()
		
		if errors:
			return JsonResponse(errors, safe=False)
		else:
			form              = Form()
			form.title        = form_title
			form.instructions = instructions
			form.logo         = logo_file if logo_file else logo
			form.email        = email
			form.gym          = gym
			form.forSale      = forSale
			form.save()
			
			for item in items:
				item.form = form
				item.save()				
		
			return JsonResponse({"url": reverse('forms')})
	else:
		files  = []
		bucket = get_bucket()
		source = "https://%s.s3.%s.amazonaws.com/" %(bucket.name, settings.AWS_S3_REGION_NAME)
		
		for obj in bucket.objects.filter(Prefix='logos'):
			files.append(obj.key)
		
		return render(request, 'forms/add.html', {'source': source, 'files': files})

def edit(request, form_id):
	user = request.session.get('user', None)
	
	if user != 'admin':
		request.session['referer'] = reverse('add')
		return redirect(reverse('admin_login'))
	
	bucket = get_bucket()
	
	if request.is_ajax():
		form_title   = request.POST.get("title", None)
		instructions = request.POST.get("instructions", None)
		logo         = request.POST.get("logo", None)
		logo_file    = request.FILES.get('logo-new-file', None)			
		email        = request.POST.get("email", None)
		gym          = request.POST.get("gym", None)
		forSale      = request.POST.get("for-sale", None)
		
		val = Validate()
		val.isEmpty(form_title, "Please enter Form Title.")
		val.isEmpty(instructions, "Please enter Form Instructions.")
		val.isEmpty(logo, "Please select Form Logo.")
		
		if logo == "new":			
			val.isImage(logo_file, "New Logo Image")
		
		val.isEmail(email, "Please enter valid Customer Email.")
		val.isEmpty(gym, "Please enter Customer Gym.")
		items = []
		
		form = Form.objects.get(id=form_id)
		
		if (forSale):
			for i in range(1, int(forSale)+1):
				order = i
				title = request.POST.get("item-title-"+str(i), None)
				price = request.POST.get("item-price-"+str(i), None)
				image = request.FILES.get('item-image-file-'+str(i), None)
				sizes = request.POST.get("item-sizes-"+str(i), None)
				item  = Item.objects.filter(order=i, form=form).first()
				item  = Item() if item is None else item
				
				item.order = order
				item.title = title
				item.price = price
				item.sizes = sizes
				item.form  = form
					
				val.isEmpty(title, "Please enter Item "+str(i)+" Title.")
				val.isInteger(price, "Please enter valid Item "+str(i)+" Price.")
				
				if (item.pk and image) or (item.pk is None):
					val.isImage(image, "Item "+str(i)+" Image")					
					item.image = image					
					
				val.isEmpty(sizes, "Please enter Item "+str(i)+" Sizes.")
				
				items.append(item)
				
		errors = val.getErrors()
		
		if errors:
			return JsonResponse(errors, safe=False)
		else:
			form.title        = form_title
			form.instructions = instructions
			form.logo         = logo_file if logo_file else logo
			form.email        = email
			form.gym          = gym
			form.forSale      = forSale
			form.save()
			
			for item in items:
				item.save()
			
			folder = 'forms/%s/' %(str(form.id))
			cleanup_images(
				bucket,
				bucket.objects.filter(Prefix=folder),
				items,
				folder
			)
				
			Item.objects.filter(form=form, order__gt=forSale).delete()
		
			return JsonResponse({"url": reverse('forms')})
	else:
		files       = []
		items       = Item.objects.filter(form_id=form_id).order_by("order")
		form        = items.first().form
		order_count = Order.objects.filter(form_id=form_id).count()
		source      = "https://%s.s3.%s.amazonaws.com/" %(bucket.name, settings.AWS_S3_REGION_NAME)
		
		for obj in bucket.objects.filter(Prefix='logos'):
			files.append(obj.key)
		
		for item in items:
			item.image = "https://%s.s3.%s.amazonaws.com/%s" %(bucket.name, settings.AWS_S3_REGION_NAME, item.image)
		
		if order_count > 0:
			return redirect(reverse('forms'))
		
		return render(request, 'forms/edit.html', {'source': source, 'files': files, 'form': form, 'items': items})