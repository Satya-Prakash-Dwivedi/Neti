import os
import io
import razorpay
import requests
import base64
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .models import Order
from quizzes.models import Quiz, Book

# Initialize Razorpay Client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def generate_invoice_pdf(order):
    """Generates a PDF invoice for a given order and returns as bytes."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 750, "Neti Academy - Invoice")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 710, f"Order ID: {order.id}")
    p.drawString(100, 690, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(100, 670, f"Student: {order.user.name} ({order.user.email})")
    
    p.line(100, 650, 500, 650)
    
    p.drawString(100, 630, "Item")
    p.drawString(400, 630, "Amount (INR)")
    
    p.setFont("Helvetica-Bold", 12)
    item_title = order.book.title if order.book else order.quiz.title
    p.drawString(100, 610, f"Purchase: {item_title}")
    p.drawString(400, 610, f"Rs. {order.amount}")
    
    p.line(100, 590, 500, 590)
    p.drawString(100, 570, "Total Paid:")
    p.drawString(400, 570, f"Rs. {order.amount}")
    
    p.setFont("Helvetica", 10)
    p.drawString(100, 500, "Thank you for practicing with Neti Academy!")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.read()

def send_invoice_email(order, pdf_bytes):
    """Sends the generated PDF invoice to the user via Brevo API."""
    api_key = os.getenv('VITE_BREVO_API_KEY')
    sender_email = os.getenv('VITE_SENDER_EMAIL')
    
    if not api_key or not sender_email:
        return False
        
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    # Base64 encode the PDF
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    item_title = order.book.title if order.book else order.quiz.title
    payload = {
        "sender": {"name": "Neti Academy", "email": sender_email},
        "to": [{"email": order.user.email, "name": order.user.name}],
        "subject": f"Your Invoice for {item_title}",
        "htmlContent": f"<html><body><p>Dear {order.user.name},</p><p>Thank you for purchasing <strong>{item_title}</strong>. Your purchase is now unlocked and ready for practice on our platform.</p><p>Please find your invoice attached.</p><p>Best regards,<br/>Neti Academy Team</p></body></html>",
        "attachment": [
            {
                "content": pdf_base64,
                "name": f"Invoice_Neti_{order.id}.pdf"
            }
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code in [200, 201]


class CreateRazorpayOrderView(APIView):
    """Creates an Order in the DB and initializes a Razorpay order."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        quiz_id = request.data.get('quiz_id')
        book_id = request.data.get('book_id')
        
        if not quiz_id and not book_id:
            return Response({'error': 'quiz_id or book_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        quiz = None
        book = None
        amount = 0
        title = ""
        
        if book_id:
            book = get_object_or_404(Book, id=book_id)
            amount = int(book.full_price * 100)
            title = f"Book: {book.book_name}"
            existing_order = Order.objects.filter(user=request.user, book=book, status='Paid').first()
        else:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            amount = int(quiz.price * 100)
            title = f"Chapter: {quiz.title}"
            existing_order = Order.objects.filter(user=request.user, quiz=quiz, status='Paid').first()
        
        # Check if already purchased
        if existing_order:
            return Response({'error': 'Already purchased'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create Razorpay Order
            razorpay_order = razorpay_client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })
            
            # Create DB Order
            order = Order.objects.create(
                user=request.user,
                quiz=quiz,
                book=book,
                amount=(book.full_price if book else quiz.price),
                razorpay_order_id=razorpay_order['id'],
                status='Pending'
            )
            
            return Response({
                'order_id': order.id,
                'razorpay_order_id': razorpay_order['id'],
                'amount': amount,
                'currency': 'INR',
                'key_id': settings.RAZORPAY_KEY_ID,
                'quiz_title': title,
                'user_name': request.user.name,
                'user_email': request.user.email
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPaymentView(APIView):
    """Verifies the Razorpay signature and finalizes the order."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response({'error': 'Missing payment details'}, status=status.HTTP_400_BAD_REQUEST)
            
        order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id, user=request.user)
        
        try:
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Mark order as Paid
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.status = 'Paid'
            order.save()
            
            # Generate Invoice & Email
            pdf_bytes = generate_invoice_pdf(order)
            send_invoice_email(order, pdf_bytes)
            
            return Response({'message': 'Payment successful', 'order_id': order.id}, status=status.HTTP_200_OK)
            
        except razorpay.errors.SignatureVerificationError:
            order.status = 'Failed'
            order.save()
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadInvoiceView(APIView):
    """Allows a user to download their invoice PDF."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user, status='Paid')
        pdf_bytes = generate_invoice_pdf(order)
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice_Neti_{order.id}.pdf"'
        return response


class UserOrdersView(APIView):
    """Returns the paid orders for the authenticated user to unlock question banks."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        orders = Order.objects.filter(user=request.user, status='Paid').values(
            'id', 'quiz_id', 'book_id', 'amount', 'created_at'
        )
        return Response(list(orders), status=status.HTTP_200_OK)


class AdminOrdersView(APIView):
    """Returns all orders for the admin dashboard."""
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        # We use select_related for efficiency, though .values() implicitly does JOINs.
        orders = Order.objects.order_by('-created_at').values(
            'id', 'user__name', 'user__email', 'quiz__title', 'book__title', 'amount', 'status', 'razorpay_payment_id', 'created_at'
        )
        return Response(list(orders), status=status.HTTP_200_OK)

